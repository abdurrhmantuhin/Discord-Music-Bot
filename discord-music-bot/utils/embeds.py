"""
Aesthetic Music Embeds for Discord Music Bot.
Clean, minimal, premium design - no button controls.
"""

import discord
from utils.messages import Colors


def create_now_playing_embed(source, player, requester=None):
    """
    Create an aesthetic Now Playing embed.
    
    Design:
    - Minimal, clean layout
    - Soft purple/violet theme
    - No clutter, easy to read
    
    Args:
        source: The audio source with title, thumbnail, etc.
        player: The MusicPlayer instance
        requester: The user who requested the song (optional)
    
    Returns:
        discord.Embed: Aesthetic Now Playing embed
    """
    
    # Create embed with aesthetic color
    embed = discord.Embed(color=Colors.MUSIC)
    
    # Title - Clean and simple
    embed.title = "Now Playing"
    
    # Song info - Main content
    song_title = source.title if hasattr(source, 'title') else "Unknown Track"
    
    # Build description with clean formatting
    description_parts = []
    description_parts.append(f"**{song_title}**")
    
    # Add a subtle separator
    embed.description = "\n".join(description_parts)
    
    # Thumbnail (album art)
    if hasattr(source, 'thumbnail') and source.thumbnail:
        embed.set_thumbnail(url=source.thumbnail)
    
    # Duration - formatted nicely
    if hasattr(source, 'duration') and source.duration:
        try:
            duration = int(source.duration)
            if duration >= 3600:
                hours = duration // 3600
                minutes = (duration % 3600) // 60
                seconds = duration % 60
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                minutes = duration // 60
                seconds = duration % 60
                duration_str = f"{minutes}:{seconds:02d}"
        except:
            duration_str = "—"
        embed.add_field(name="Duration", value=duration_str, inline=True)
    
    # Volume
    volume_pct = int(player.volume * 100)
    embed.add_field(name="Volume", value=f"{volume_pct}%", inline=True)
    
    # Loop status
    if player.loop:
        loop_status = "Song"
    elif player.loop_queue:
        loop_status = "Queue"
    else:
        loop_status = "Off"
    embed.add_field(name="Loop", value=loop_status, inline=True)
    
    # Queue length
    queue_len = len(player.queue)
    if queue_len > 0:
        embed.add_field(name="Up Next", value=f"{queue_len} tracks", inline=True)
    
    # Footer - Subtle requester info
    if requester:
        embed.set_footer(
            text=f"Requested by {requester.display_name}",
            icon_url=requester.display_avatar.url if hasattr(requester, 'display_avatar') and requester.display_avatar else None
        )
    else:
        embed.set_footer(text="Enjoy the music")
    
    return embed


def create_queue_embed(queue, current_song=None):
    """
    Create an aesthetic queue embed.
    
    Args:
        queue: The song queue (deque or list)
        current_song: Currently playing song info (optional)
    
    Returns:
        discord.Embed: Aesthetic queue embed
    """
    embed = discord.Embed(
        title="Queue",
        color=Colors.MUSIC
    )
    
    if not queue and not current_song:
        embed.description = "*The queue is empty*"
        return embed
    
    description_parts = []
    
    # Current song
    if current_song:
        title = current_song.get('title', 'Unknown')[:45]
        description_parts.append(f"**Now:** {title}")
        description_parts.append("")
    
    # Queue items (max 8)
    queue_list = list(queue)[:8]
    for i, song in enumerate(queue_list, 1):
        title = song.get('title', 'Unknown')[:40]
        description_parts.append(f"`{i}.` {title}")
    
    # More indicator
    if len(queue) > 8:
        description_parts.append(f"\n*+{len(queue) - 8} more tracks*")
    
    embed.description = "\n".join(description_parts) if description_parts else "*Empty*"
    embed.set_footer(text=f"{len(queue)} tracks in queue")
    
    return embed


def create_status_embed(message: str, status_type: str = "info"):
    """
    Create a status/notification embed.
    
    Args:
        message: The status message
        status_type: "info", "success", "error", "warning"
    
    Returns:
        discord.Embed: Status embed
    """
    color_map = {
        "info": Colors.INFO,
        "success": Colors.SUCCESS,
        "error": Colors.ERROR,
        "warning": Colors.WARNING
    }
    
    embed = discord.Embed(
        description=message,
        color=color_map.get(status_type, Colors.INFO)
    )
    
    return embed
