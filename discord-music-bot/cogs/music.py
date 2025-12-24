"""
Music Cog for Discord Music Bot.
Contains all music-related commands and queue management.
"""

import asyncio
import random
import logging
import discord
from discord.ext import commands
from collections import deque

logger = logging.getLogger('discord_music_bot')

from config import (
    EMBED_COLOR, ERROR_COLOR, SUCCESS_COLOR,
    DEFAULT_VOLUME, MAX_QUEUE_SIZE, DISCONNECT_TIMEOUT
)
from utils.ytdl import YTDLSource
from utils.spotify import SpotifyHandler
from utils.embeds import create_now_playing_embed, create_playlist_embed, create_song_added_embed


class MusicPlayer:
    """
    Represents a music player for a guild.
    Manages queue, current song, and playback state.
    """
    
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog
        
        self.queue = deque()
        self.next = asyncio.Event()
        self.current = None
        self.volume = DEFAULT_VOLUME
        self.loop = False
        self.loop_queue = False
        self.stopped = False  # Flag to completely stop the player
        
        ctx.bot.loop.create_task(self.player_loop())
    
    async def player_loop(self):
        """Main player loop - plays songs from queue."""
        await self.bot.wait_until_ready()
        
        while not self.bot.is_closed():
            # Check if stopped flag is set
            if self.stopped:
                return self.destroy(self.guild, intentional=True)
            
            self.next.clear()
            
            # Check if we're still connected to voice
            if not self.guild.voice_client or not self.guild.voice_client.is_connected():
                # Bot was disconnected, cleanup silently
                return self.destroy(self.guild)
            
            if self.loop and self.current:
                # Re-add current song if looping - don't pop from queue
                pass
            elif self.loop_queue and self.current:
                # Add current song back to end of queue
                self.queue.append(self.current)
            
            try:
                # Wait for next song with timeout
                async with asyncio.timeout(DISCONNECT_TIMEOUT):
                    if not self.loop or not self.current:
                        if not self.queue:
                            # Check if stopped before waiting
                            if self.stopped:
                                return self.destroy(self.guild, intentional=True)
                            # Ensure we are not sending any audio data (fix for green circle)
                            if self.guild.voice_client and self.guild.voice_client.is_connected():
                                # Only stop if we are truly idle (not playing and not paused)
                                if not self.guild.voice_client.is_playing() and not self.guild.voice_client.is_paused():
                                    self.guild.voice_client.stop()
                            
                            # Wait for songs to be added
                            await asyncio.sleep(2)
                            # Check if stopped again after sleep
                            if self.stopped or not self.guild.voice_client:
                                return self.destroy(self.guild, intentional=True if self.stopped else False)
                            continue
                        self.current = self.queue.popleft()
            except asyncio.TimeoutError:
                # Disconnect after timeout (silently)
                # This is "intentional" from the bot's perspective (timeout)
                return self.destroy(self.guild, intentional=True)
            
            # Double check stopped flag and voice connection before playing
            if self.stopped or not self.guild.voice_client or not self.guild.voice_client.is_connected():
                return self.destroy(self.guild, intentional=True if self.stopped else False)
            
            try:
                # Create audio source
                source = await YTDLSource.from_url(
                    self.current['webpage_url'],
                    loop=self.bot.loop,
                    stream=True,
                    volume=self.volume
                )
                
                if isinstance(source, list):
                    # It's a playlist, shouldn't happen here
                    continue
                
                # Final check before playing
                if self.stopped or not self.guild.voice_client:
                    return self.destroy(self.guild, intentional=True if self.stopped else False)
                
                self.guild.voice_client.play(
                    source,
                    after=lambda e: self.bot.loop.call_soon_threadsafe(self.next.set)
                )
                
                # Send fresh Now Playing embed for EACH song (no editing)
                try:
                    requester = self.current.get('requester', None) if self.current else None
                    remaining = len(self.queue)  # Songs remaining after this one
                    embed = create_now_playing_embed(source, self, requester, remaining)
                    await self.channel.send(embed=embed)
                except Exception as embed_error:
                    # Fallback to simple message if embed fails
                    print(f"Embed error: {embed_error}")
                    await self.channel.send(f"Now Playing: **{source.title}**")
                
            except AttributeError:
                # Voice client was disconnected, exit silently (handled by on_voice_state_update if kick)
                return self.destroy(self.guild, intentional=False)
            except Exception as e:
                # Only send error if still connected
                if self.guild.voice_client and self.guild.voice_client.is_connected():
                    await self.channel.send(f"❌ Error: {str(e)[:50]}")
                self.current = None
                continue
            
            await self.next.wait()
            
            if not self.loop:
                self.current = None
    
    def destroy(self, guild, intentional=False):
        """Disconnect and cleanup."""
        # Note: If intentional, the cog's cleanup will mark it as such
        return self.bot.loop.create_task(self.cog.cleanup(guild, intentional=intentional))


class Music(commands.Cog):
    """
    Music cog with all playback commands.
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
        self.spotify = SpotifyHandler()
        self.intentional_disconnects = set()
    
    # ============================================
    # Parallel Processing Helpers (10x faster!)
    # ============================================
    
    async def _search_song_safe(self, query):
        """Search with error handling."""
        try:
            result = await YTDLSource.search(query, loop=self.bot.loop)
            return result
        except Exception as e:
            logger.warning(f"Search failed: {query[:30]} - {e}")
            return None
    
    async def _process_playlist_background(self, ctx, tracks, player):
        """Process playlist songs in background (sequential but non-blocking)."""
        logger.info(f"Background processing {len(tracks)} songs")
        added = 0
        
        try:
            for query in tracks:
                if len(player.queue) >= MAX_QUEUE_SIZE:
                    break
                    
                try:
                    result = await YTDLSource.search(query, loop=self.bot.loop)
                    if result:
                        player.queue.append(result)
                        added += 1
                except Exception as e:
                    logger.warning(f"Background search failed: {query[:30]}")
                    continue
            
            logger.info(f"Background complete: {added}/{len(tracks)} songs")
        except Exception as e:
            logger.error(f"Background processing error: {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """
        Listen for voice state updates to handle 'kick' events.
        If the bot is disconnected and it wasn't intentional, send a message.
        """
        if member.id != self.bot.user.id:
            return
        
        # Check if bot was disconnected
        if before.channel and after.channel is None:
            guild_id = member.guild.id
            
            # If it was an intentional disconnect (triggered by command/timeout), ignore
            if guild_id in self.intentional_disconnects:
                self.intentional_disconnects.discard(guild_id)
                return
            
            # If we are here, the bot was likely kicked or disconnected forcefully
            # Find the player to get the text channel
            if guild_id in self.players:
                player = self.players[guild_id]
                if player.channel:
                    try:
                        embed = discord.Embed(
                            description="🥺 **Oh no! I got kicked from the voice channel...**\n*Was I being a bad bot?* 👉👈",
                            color=ERROR_COLOR
                        )
                        await player.channel.send(embed=embed)
                    except:
                        pass
                
                # Ensure cleanup happens even if kicked
                await self.cleanup(member.guild, intentional=False)
    
    async def cleanup(self, guild, intentional=False):
        """Cleanup player and disconnect from voice."""
        if intentional:
            self.intentional_disconnects.add(guild.id)
            
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass
        
        try:
            del self.players[guild.id]
        except KeyError:
            pass
    
    def get_player(self, ctx):
        """Get or create a player for the guild."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        
        return player
    
    # ============================================
    # Voice Channel Commands
    # ============================================
    
    @commands.command(name='join', aliases=['connect', 'j'])
    async def join(self, ctx, silent=False):
        """Join your voice channel."""
        if not ctx.author.voice:
            if not silent:
                return await ctx.send("❌ You need to be in a voice channel!")
            return
        
        channel = ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                return  # Already in channel, no message needed
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        # Only send join message if explicitly called (not silent)
        if not silent and ctx.invoked_with in ['join', 'connect', 'j']:
            await ctx.send(f"🎵 Joined **{channel.name}**!")
    
    @commands.command(name='leave', aliases=['disconnect', 'dc', 'bye'])
    async def leave(self, ctx):
        """Leave voice channel."""
        if not ctx.voice_client:
            return await ctx.send("❌ I'm not in a voice channel!")
        
        await self.cleanup(ctx.guild, intentional=True)
        await ctx.send("👋 Disconnected from voice channel!")
    
    # ============================================
    # Playback Commands
    # ============================================
    
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """
        Play a song from YouTube or Spotify.
        
        Usage:
            !play <YouTube URL>
            !play <Spotify URL>
            !play <search query>
        """
        if not ctx.author.voice:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        if not ctx.voice_client:
            await ctx.invoke(self.join, silent=True)
        
        player = self.get_player(ctx)
        
        if len(player.queue) >= MAX_QUEUE_SIZE:
            return await ctx.send(f"❌ Queue is full! (Max: {MAX_QUEUE_SIZE})")
        
        # Process the query (no typing indicator to avoid continuous typing)
        try:
            # Check if it's a Spotify URL
            if 'spotify.com' in query:
                # Get playlist/track data from Spotify
                spotify_data = await self.spotify.process_spotify_url(query)
                
                if spotify_data:
                    # Check if it's a playlist (dict) or single track (list)
                    if isinstance(spotify_data, dict) and 'tracks' in spotify_data:
                        # It's a playlist
                        tracks = spotify_data.get('tracks', [])
                        if not tracks:
                            return await ctx.send(
                                "❌ **Cannot access this playlist!**\n"
                                "This might be a personalized/algorithmic playlist.\n"
                                "Try a regular public Spotify playlist instead."
                            )
                        
                        # STEP 1: Send playlist embed FIRST (instant feedback)
                        embed = create_playlist_embed(
                            playlist_name=spotify_data.get('name', 'Spotify Playlist'),
                            total_tracks=len(tracks),
                            total_duration=0,
                            remaining=len(tracks),
                            thumbnail=spotify_data.get('image')
                        )
                        await ctx.send(embed=embed)
                        
                        # Add ALL songs to queue (simple, reliable)
                        added = 0
                        for search_query in tracks:
                            try:
                                result = await YTDLSource.search(search_query, loop=self.bot.loop)
                                if result:
                                    player.queue.append(result)
                                    added += 1
                            except:
                                continue
                        
                        logger.info(f"Playlist complete: {added}/{len(tracks)} songs added")
                        return
                    else:
                        # It's a single track or album (list of queries)
                        queries = spotify_data if isinstance(spotify_data, list) else [spotify_data]
                        for search_query in queries:
                            try:
                                result = await YTDLSource.search(search_query, loop=self.bot.loop)
                                player.queue.append(result)
                                
                                # FIX #3: Show feedback for single track additions
                                current_playing = 1 if player.current else 0
                                embed = create_song_added_embed(
                                    title=result.get('title', 'Unknown'),
                                    duration=result.get('duration'),
                                    url=result.get('webpage_url'),
                                    thumbnail=result.get('thumbnail'),
                                    position=len(player.queue) + current_playing
                                )
                                await ctx.send(embed=embed)
                            except Exception as e:
                                await ctx.send(f"⚠️ Couldn't add track")
                        return
                else:
                    return await ctx.send(
                        "❌ **Cannot access this playlist!**\n"
                        "This might be a personalized/algorithmic playlist.\n"
                        "Try a regular public Spotify playlist instead."
                    )
            
            # YouTube URL or search query
            if YTDLSource.is_url(query):
                # Direct URL
                result = await YTDLSource.from_url(query, loop=self.bot.loop, stream=True)
                
                if isinstance(result, list):
                    # YouTube playlist - send embed FIRST
                    total_duration = sum(song.get('duration', 0) or 0 for song in result)
                    
                    # STEP 1: Send embed immediately
                    embed = create_playlist_embed(
                        playlist_name="YouTube Playlist",
                        total_tracks=len(result),
                        total_duration=total_duration,
                        remaining=len(result),
                        thumbnail=result[0].get('thumbnail') if result else None
                    )
                    await ctx.send(embed=embed)
                    
                    # STEP 2: Then add to queue
                    added = 0
                    for song in result:
                        if len(player.queue) < MAX_QUEUE_SIZE:
                            player.queue.append(song)
                            added += 1
                else:
                    # Single song - create source and add to queue
                    song_data = {
                        'title': result.title,
                        'webpage_url': result.webpage_url,
                        'duration': result.duration,
                        'thumbnail': result.thumbnail,
                        'uploader': result.uploader
                    }
                    player.queue.append(song_data)
                    
                    # FIX #4: Use correct position (account for currently playing)
                    current_playing = 1 if player.current else 0
                    embed = create_song_added_embed(
                        title=result.title,
                        duration=result.duration,
                        url=result.webpage_url,
                        thumbnail=result.thumbnail,
                        position=len(player.queue) + current_playing
                    )
                    await ctx.send(embed=embed)
            else:
                # Search query
                result = await YTDLSource.search(query, loop=self.bot.loop)
                player.queue.append(result)
                
                # FIX #4: Use create_song_added_embed with correct position
                current_playing = 1 if player.current else 0
                embed = create_song_added_embed(
                    title=result.get('title', 'Unknown'),
                    duration=result.get('duration'),
                    url=result.get('webpage_url'),
                    thumbnail=result.get('thumbnail'),
                    position=len(player.queue) + current_playing
                )
                await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the current song."""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("❌ Nothing is playing!")
        
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused!")
    
    @commands.command(name='resume', aliases=['unpause'])
    async def resume(self, ctx):
        """Resume the paused song."""
        if not ctx.voice_client or not ctx.voice_client.is_paused():
            return await ctx.send("❌ Nothing is paused!")
        
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed!")
    
    @commands.command(name='stop', aliases=['s'])
    async def stop(self, ctx):
        """Stop playback and clear the queue."""
        if not ctx.voice_client:
            return await ctx.send("❌ I'm not playing anything!")
        
        player = self.get_player(ctx)
        
        # Set stopped flag FIRST to prevent player loop from continuing
        player.stopped = True
        player.queue.clear()
        player.current = None
        player.loop = False
        player.loop_queue = False  # Reset queue loop too!
        
        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            # This is key: stop() usually doesn't trigger on_voice_state_update disconnect immediately,
            # but cleanup() below will.
            ctx.voice_client.stop()
        
        # Remove the player completely to prevent any ghost playback
        try:
            del self.players[ctx.guild.id]
        except KeyError:
            pass
        
        await ctx.send("⏹️ Stopped and cleared the queue!")
    
    @commands.command(name='skip', aliases=['n', 'next'])
    async def skip(self, ctx):
        """Skip to the next song."""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("❌ Nothing is playing!")
        
        player = self.get_player(ctx)
        player.loop = False  # Disable loop for skip
        
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped!")
    
    # ============================================
    # Queue Commands
    # ============================================
    
    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue(self, ctx):
        """Display the current queue."""
        player = self.get_player(ctx)
        
        if not player.queue and not player.current:
            return await ctx.send("📭 Queue is empty!")
        
        embed = discord.Embed(title="🎵 Music Queue", color=EMBED_COLOR)
        
        # Current song
        if player.current:
            current_title = player.current.get('title', 'Unknown')
            embed.add_field(
                name="▶️ Now Playing",
                value=f"[{current_title}]({player.current.get('webpage_url', '')})",
                inline=False
            )
        
        # Queue
        if player.queue:
            queue_list = []
            for i, song in enumerate(list(player.queue)[:10], 1):
                title = song.get('title', 'Unknown')
                duration = YTDLSource.format_duration(song.get('duration'))
                queue_list.append(f"`{i}.` [{title}]({song.get('webpage_url', '')}) `[{duration}]`")
            
            embed.add_field(
                name=f"📋 Up Next ({len(player.queue)} songs)",
                value="\n".join(queue_list) if queue_list else "Empty",
                inline=False
            )
            
            if len(player.queue) > 10:
                embed.set_footer(text=f"And {len(player.queue) - 10} more songs...")
        
        # Loop status
        if player.loop:
            embed.add_field(name="🔂", value="Loop: ON", inline=True)
        if player.loop_queue:
            embed.add_field(name="🔁", value="Queue Loop: ON", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='nowplaying', aliases=['np', 'current'])
    async def nowplaying(self, ctx):
        """Show the currently playing song."""
        player = self.get_player(ctx)
        
        if not player.current:
            return await ctx.send("❌ Nothing is playing!")
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"[{player.current.get('title', 'Unknown')}]({player.current.get('webpage_url', '')})",
            color=EMBED_COLOR
        )
        
        if player.current.get('thumbnail'):
            embed.set_thumbnail(url=player.current['thumbnail'])
        if player.current.get('duration'):
            embed.add_field(
                name="Duration",
                value=YTDLSource.format_duration(player.current['duration']),
                inline=True
            )
        if player.current.get('uploader'):
            embed.add_field(name="Uploader", value=player.current['uploader'], inline=True)
        
        embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume', aliases=['vol', 'v'])
    async def volume(self, ctx, volume: int = None):
        """
        Set the volume (0-100).
        
        Usage: !volume 50
        """
        player = self.get_player(ctx)
        
        if volume is None:
            return await ctx.send(f"🔊 Current volume: **{int(player.volume * 100)}%**")
        
        if not 0 <= volume <= 100:
            return await ctx.send("❌ Volume must be between 0 and 100!")
        
        player.volume = volume / 100
        
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = player.volume
        
        await ctx.send(f"🔊 Volume set to **{volume}%**")
    
    @commands.command(name='clear', aliases=['cl'])
    async def clear(self, ctx):
        """Clear the queue."""
        player = self.get_player(ctx)
        
        if not player.queue:
            return await ctx.send("📭 Queue is already empty!")
        
        count = len(player.queue)
        player.queue.clear()
        await ctx.send(f"🗑️ Cleared **{count}** songs from the queue!")
    
    @commands.command(name='shuffle', aliases=['sh'])
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        player = self.get_player(ctx)
        
        if len(player.queue) < 2:
            return await ctx.send("❌ Not enough songs in queue to shuffle!")
        
        queue_list = list(player.queue)
        random.shuffle(queue_list)
        player.queue = deque(queue_list)
        
        await ctx.send("🔀 Queue shuffled!")
    
    @commands.command(name='loop', aliases=['l', 'repeat'])
    async def loop(self, ctx):
        """Toggle loop for current song."""
        player = self.get_player(ctx)
        
        player.loop = not player.loop
        
        if player.loop:
            await ctx.send("🔂 Loop enabled!")
        else:
            await ctx.send("➡️ Loop disabled!")
    
    @commands.command(name='loopqueue', aliases=['lq', 'queueloop'])
    async def loopqueue(self, ctx):
        """Toggle loop for the entire queue."""
        player = self.get_player(ctx)
        
        player.loop_queue = not player.loop_queue
        
        if player.loop_queue:
            await ctx.send("🔁 Queue loop enabled!")
        else:
            await ctx.send("➡️ Queue loop disabled!")
    
    @commands.command(name='remove', aliases=['rm'])
    async def remove(self, ctx, position: int):
        """
        Remove a song from the queue by position.
        
        Usage: !remove 3
        """
        player = self.get_player(ctx)
        
        if not player.queue:
            return await ctx.send("📭 Queue is empty!")
        
        if not 1 <= position <= len(player.queue):
            return await ctx.send(f"❌ Invalid position! Must be between 1 and {len(player.queue)}")
        
        queue_list = list(player.queue)
        removed = queue_list.pop(position - 1)
        player.queue = deque(queue_list)
        
        await ctx.send(f"🗑️ Removed **{removed.get('title', 'Unknown')}** from the queue!")
    
    # ============================================
    # Error Handling
    # ============================================
    
    @play.error
    async def play_error(self, ctx, error):
        """Handle play command errors."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide a song name or URL!\nUsage: `!play <song name or URL>`")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)}")
    
    @volume.error
    async def volume_error(self, ctx, error):
        """Handle volume command errors."""
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Volume must be a number between 0 and 100!")
    
    @remove.error
    async def remove_error(self, ctx, error):
        """Handle remove command errors."""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please provide a position!\nUsage: `!remove <position>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Position must be a number!")


async def setup(bot):
    """Add the cog to the bot."""
    await bot.add_cog(Music(bot))
