"""
Music Control Buttons for Discord Music Bot.
Provides interactive button controls for music playback.
"""

import discord
from discord.ext import commands
from discord import ui
import asyncio
from datetime import datetime, timedelta


class MusicControlView(ui.View):
    """
    Interactive button controls for music playback.
    Attached to Now Playing embeds.
    """
    
    def __init__(self, ctx, player, cog, *, timeout=None):
        """
        Initialize the music control view.
        
        Args:
            ctx: The command context
            player: The MusicPlayer instance
            cog: The Music cog instance
            timeout: View timeout (None = no timeout)
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.player = player
        self.cog = cog
        self.message = None  # Will store the message this view is attached to
        self.cooldowns = {}  # Per-user cooldowns: {user_id: last_interaction_time}
        
        # Update button states based on current player state
        self._update_buttons()
    
    def _update_buttons(self):
        """Update button labels and styles based on player state."""
        # Update pause/resume button
        if self.ctx.voice_client and self.ctx.voice_client.is_paused():
            self.pause_resume.emoji = "▶️"
            self.pause_resume.label = "Resume"
            self.pause_resume.style = discord.ButtonStyle.success
        else:
            self.pause_resume.emoji = "⏸️"
            self.pause_resume.label = "Pause"
            self.pause_resume.style = discord.ButtonStyle.secondary
        
        # Update loop button
        if self.player.loop:
            self.loop_btn.emoji = "🔂"
            self.loop_btn.label = "Loop: Song"
            self.loop_btn.style = discord.ButtonStyle.success
        elif self.player.loop_queue:
            self.loop_btn.emoji = "🔁"
            self.loop_btn.label = "Loop: Queue"
            self.loop_btn.style = discord.ButtonStyle.primary
        else:
            self.loop_btn.emoji = "🔁"
            self.loop_btn.label = "Loop: Off"
            self.loop_btn.style = discord.ButtonStyle.secondary
    
    async def _check_permissions(self, interaction: discord.Interaction, dj_required: bool = False) -> bool:
        """
        Check if user has permission to use the button.
        
        Args:
            interaction: The button interaction
            dj_required: Whether DJ role is required for this action
            
        Returns:
            True if permitted, False otherwise
        """
        # Check if user is in the same voice channel as the bot
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ You must be in a voice channel to use these controls.",
                ephemeral=True
            )
            return False
        
        bot_voice = interaction.guild.voice_client
        if not bot_voice or interaction.user.voice.channel != bot_voice.channel:
            await interaction.response.send_message(
                "❌ You must be in **my** voice channel to use these controls.",
                ephemeral=True
            )
            return False
        
        # Check DJ role requirement
        if dj_required:
            dj_role = discord.utils.get(interaction.guild.roles, name="DJ")
            if dj_role:
                # DJ role exists - check if user has it
                if dj_role not in interaction.user.roles:
                    await interaction.response.send_message(
                        "❌ You need the **DJ** role to use this control.",
                        ephemeral=True
                    )
                    return False
        
        # Check cooldown (3 seconds per user)
        user_id = interaction.user.id
        now = datetime.now()
        if user_id in self.cooldowns:
            time_since = (now - self.cooldowns[user_id]).total_seconds()
            if time_since < 3:
                await interaction.response.send_message(
                    f"⏳ Please wait {3 - int(time_since)} seconds before clicking again.",
                    ephemeral=True
                )
                return False
        
        self.cooldowns[user_id] = now
        return True
    
    async def on_timeout(self):
        """Called when the view times out - disable all buttons."""
        await self._disable_all_buttons()
    
    async def _disable_all_buttons(self):
        """Disable all buttons and update the message."""
        for child in self.children:
            child.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except:
                pass
    
    # ============================================
    # Button Definitions
    # ============================================
    
    @ui.button(emoji="⏸️", label="Pause", style=discord.ButtonStyle.secondary, row=0)
    async def pause_resume(self, interaction: discord.Interaction, button: ui.Button):
        """Toggle pause/resume."""
        if not await self._check_permissions(interaction):
            return
        
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("❌ Not playing anything!", ephemeral=True)
            return
        
        if vc.is_paused():
            vc.resume()
            button.emoji = "⏸️"
            button.label = "Pause"
            button.style = discord.ButtonStyle.secondary
            await interaction.response.edit_message(view=self)
        elif vc.is_playing():
            vc.pause()
            button.emoji = "▶️"
            button.label = "Resume"
            button.style = discord.ButtonStyle.success
            await interaction.response.edit_message(view=self)
        else:
            await interaction.response.send_message("❌ Nothing to pause/resume!", ephemeral=True)
    
    @ui.button(emoji="⏭️", label="Skip", style=discord.ButtonStyle.primary, row=0)
    async def skip_btn(self, interaction: discord.Interaction, button: ui.Button):
        """Skip the current song."""
        if not await self._check_permissions(interaction, dj_required=True):
            return
        
        vc = interaction.guild.voice_client
        if not vc or not (vc.is_playing() or vc.is_paused()):
            await interaction.response.send_message("❌ Nothing to skip!", ephemeral=True)
            return
        
        self.player.loop = False  # Disable loop when skipping
        vc.stop()
        await interaction.response.send_message(
            f"⏭️ Skipped by {interaction.user.display_name}",
            ephemeral=False
        )
    
    @ui.button(emoji="⏹️", label="Stop", style=discord.ButtonStyle.danger, row=0)
    async def stop_btn(self, interaction: discord.Interaction, button: ui.Button):
        """Stop playback and clear queue."""
        if not await self._check_permissions(interaction, dj_required=True):
            return
        
        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message("❌ Not connected!", ephemeral=True)
            return
        
        # Clear queue and stop
        self.player.queue.clear()
        self.player.loop = False
        self.player.loop_queue = False
        self.player.stopped = True
        
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        
        # Disable buttons
        await self._disable_all_buttons()
        
        await interaction.response.send_message("⏹️ Stopped and cleared queue!", ephemeral=False)
    
    @ui.button(emoji="🔁", label="Loop: Off", style=discord.ButtonStyle.secondary, row=0)
    async def loop_btn(self, interaction: discord.Interaction, button: ui.Button):
        """Cycle through loop modes: Off -> Song -> Queue -> Off."""
        if not await self._check_permissions(interaction, dj_required=True):
            return
        
        # Cycle through modes
        if not self.player.loop and not self.player.loop_queue:
            # Off -> Song loop
            self.player.loop = True
            self.player.loop_queue = False
            button.emoji = "🔂"
            button.label = "Loop: Song"
            button.style = discord.ButtonStyle.success
            status = "🔂 Song loop enabled"
        elif self.player.loop:
            # Song -> Queue loop
            self.player.loop = False
            self.player.loop_queue = True
            button.emoji = "🔁"
            button.label = "Loop: Queue"
            button.style = discord.ButtonStyle.primary
            status = "🔁 Queue loop enabled"
        else:
            # Queue -> Off
            self.player.loop = False
            self.player.loop_queue = False
            button.emoji = "🔁"
            button.label = "Loop: Off"
            button.style = discord.ButtonStyle.secondary
            status = "➡️ Loop disabled"
        
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(status, ephemeral=True)
    
    @ui.button(emoji="📜", label="Queue", style=discord.ButtonStyle.secondary, row=1)
    async def queue_btn(self, interaction: discord.Interaction, button: ui.Button):
        """Show the current queue."""
        if not await self._check_permissions(interaction):
            return
        
        queue = self.player.queue
        if not queue:
            await interaction.response.send_message("📜 Queue is empty!", ephemeral=True)
            return
        
        # Build queue list (max 10 shown)
        queue_list = list(queue)[:10]
        description = ""
        for i, song in enumerate(queue_list, 1):
            title = song.get('title', 'Unknown')[:40]
            description += f"`{i}.` {title}\n"
        
        if len(queue) > 10:
            description += f"\n*...and {len(queue) - 10} more*"
        
        embed = discord.Embed(
            title="📜 Current Queue",
            description=description,
            color=0x7289DA
        )
        embed.set_footer(text=f"Total: {len(queue)} songs")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(emoji="🔊", label="+10%", style=discord.ButtonStyle.secondary, row=1)
    async def volume_up(self, interaction: discord.Interaction, button: ui.Button):
        """Increase volume by 10%."""
        if not await self._check_permissions(interaction, dj_required=True):
            return
        
        new_vol = min(self.player.volume + 0.1, 1.0)
        self.player.volume = new_vol
        
        # Update source volume if playing
        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = new_vol
        
        await interaction.response.send_message(
            f"🔊 Volume: {int(new_vol * 100)}%",
            ephemeral=True
        )
    
    @ui.button(emoji="🔉", label="-10%", style=discord.ButtonStyle.secondary, row=1)
    async def volume_down(self, interaction: discord.Interaction, button: ui.Button):
        """Decrease volume by 10%."""
        if not await self._check_permissions(interaction, dj_required=True):
            return
        
        new_vol = max(self.player.volume - 0.1, 0.0)
        self.player.volume = new_vol
        
        # Update source volume if playing
        vc = interaction.guild.voice_client
        if vc and vc.source:
            vc.source.volume = new_vol
        
        await interaction.response.send_message(
            f"🔉 Volume: {int(new_vol * 100)}%",
            ephemeral=True
        )
    
    @ui.button(emoji="❌", label="Dismiss", style=discord.ButtonStyle.secondary, row=1)
    async def dismiss_btn(self, interaction: discord.Interaction, button: ui.Button):
        """Dismiss the control panel (delete the message)."""
        if not await self._check_permissions(interaction):
            return
        
        try:
            await interaction.message.delete()
        except:
            await interaction.response.send_message("Could not delete message.", ephemeral=True)


def create_now_playing_embed(source, player, requester=None):
    """
    Create a professional Now Playing embed.
    
    Args:
        source: The YTDLSource audio source
        player: The MusicPlayer instance
        requester: The user who requested the song (optional)
    
    Returns:
        discord.Embed: The formatted embed
    """
    embed = discord.Embed(
        title="🎵 Now Playing",
        color=0x1DB954  # Spotify green
    )
    
    # Song title with link
    embed.description = f"**[{source.title}]({source.webpage_url})**"
    
    # Thumbnail
    if source.thumbnail:
        embed.set_thumbnail(url=source.thumbnail)
    
    # Duration
    if source.duration:
        from utils.ytdl import YTDLSource
        duration_str = YTDLSource.format_duration(source.duration)
        embed.add_field(name="⏱️ Duration", value=duration_str, inline=True)
    
    # Volume
    embed.add_field(name="🔊 Volume", value=f"{int(player.volume * 100)}%", inline=True)
    
    # Loop status
    if player.loop:
        loop_status = "🔂 Song"
    elif player.loop_queue:
        loop_status = "🔁 Queue"
    else:
        loop_status = "➡️ Off"
    embed.add_field(name="🔁 Loop", value=loop_status, inline=True)
    
    # Queue length
    queue_len = len(player.queue)
    embed.add_field(name="📜 Queue", value=f"{queue_len} songs", inline=True)
    
    # Requester
    if requester:
        embed.set_footer(
            text=f"Requested by {requester.display_name}",
            icon_url=requester.display_avatar.url if requester.display_avatar else None
        )
    
    return embed
