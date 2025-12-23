"""
Aesthetic Music Embeds for Discord Music Bot.
Clean, minimal, premium design.
Supports: Playlist embeds and Single song embeds.
"""

import discord
from utils.messages import Colors


def format_duration(seconds):
    """Format duration in seconds to human-readable format."""
    try:
        seconds = int(seconds)
        if seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}:{secs:02d}"
    except:
        return "—"


def format_total_duration(seconds):
    """Format total duration for playlists (e.g. '1h 42m')."""
    try:
        seconds = int(seconds)
        if seconds <= 0:
            return "—"  # Show dash when duration unavailable
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m"
        else:
            return "<1m"
    except (TypeError, ValueError):
        return "—"


# ============================================
# Playlist Embed
# ============================================

def create_playlist_embed(playlist_name: str, total_tracks: int, total_duration: int, 
                          remaining: int, thumbnail: str = None):
    """
    Create an embed for playlist playback.
    
    Shows:
    - Playlist name
    - Total tracks
    - Total duration
    - Songs remaining
    
    Args:
        playlist_name: Name of the playlist
        total_tracks: Total number of tracks
        total_duration: Total duration in seconds
        remaining: Songs remaining in queue
        thumbnail: Playlist thumbnail URL
    
    Returns:
        discord.Embed
    """
    embed = discord.Embed(color=Colors.MUSIC)
    embed.title = "Added Playlist"
    
    # Playlist name as main content
    embed.add_field(name="Playlist", value=f"**{playlist_name}**", inline=False)
    
    # Thumbnail
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Stats in one row (only show length if available)
    if total_duration and total_duration > 0:
        embed.add_field(name="Playlist Length", value=format_total_duration(total_duration), inline=True)
    embed.add_field(name="Tracks", value=str(total_tracks), inline=True)
    
    # Footer
    embed.set_footer(text="Enjoy the music!")
    
    return embed


# ============================================
# Now Playing Embed (for single songs during playback)
# ============================================

def create_now_playing_embed(source, player=None, requester=None, remaining: int = 0):
    """
    Create Now Playing embed for current track.
    
    For single songs: Shows song name + duration only
    During playlist: Shows song + remaining count
    
    Args:
        source: Audio source with title, duration, thumbnail
        player: MusicPlayer instance (optional)
        requester: User who requested (optional)
        remaining: Songs remaining in queue
    
    Returns:
        discord.Embed
    """
    embed = discord.Embed(color=Colors.MUSIC)
    embed.title = "Now Playing"
    
    # Song title
    song_title = source.title if hasattr(source, 'title') else "Unknown Track"
    embed.description = f"**{song_title}**"
    
    # Thumbnail
    if hasattr(source, 'thumbnail') and source.thumbnail:
        embed.set_thumbnail(url=source.thumbnail)
    
    # Duration
    if hasattr(source, 'duration') and source.duration:
        embed.add_field(name="Length", value=format_duration(source.duration), inline=True)
    
    # Remaining songs (only show if there are more)
    if remaining > 0:
        embed.add_field(name="Remaining", value=f"{remaining} tracks", inline=True)
    
    # Footer - consistent behavior
    if requester:
        footer_text = f"Requested by {requester.display_name}"
        icon_url = requester.display_avatar.url if hasattr(requester, 'display_avatar') and requester.display_avatar else None
        embed.set_footer(text=footer_text, icon_url=icon_url)
    else:
        embed.set_footer(text="Enjoy the music!")
    
    return embed


# ============================================
# Single Song Added Embed
# ============================================

def create_song_added_embed(title: str, duration: int = None, url: str = None, 
                            thumbnail: str = None, position: int = None):
    """
    Create embed when a single song is added to queue.
    
    Args:
        title: Song title
        duration: Song duration in seconds
        url: Song URL
        thumbnail: Thumbnail URL
        position: Position in queue
    
    Returns:
        discord.Embed
    """
    embed = discord.Embed(color=Colors.MUSIC)
    embed.title = "Added to Queue"
    
    # Song title with link if available
    if url:
        embed.description = f"**[{title}]({url})**"
    else:
        embed.description = f"**{title}**"
    
    # Thumbnail
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    # Duration - check for None explicitly (0 is valid)
    if duration is not None:
        embed.add_field(name="Length", value=format_duration(duration), inline=True)
    
    # Position - check for None explicitly (position 1 should show)
    if position is not None and position >= 1:
        embed.add_field(name="Position", value=f"#{position}", inline=True)
    
    # Footer
    embed.set_footer(text="Enjoy the music!")
    
    return embed


# ============================================
# Status/Error Embeds
# ============================================

def create_status_embed(message: str, status_type: str = "info"):
    """Create a status embed."""
    color_map = {
        "info": Colors.INFO,
        "success": Colors.SUCCESS,
        "error": Colors.ERROR,
        "warning": Colors.WARNING
    }
    
    # Safe color lookup with fallback
    color = getattr(Colors, 'INFO', 0x6366F1)  # Fallback to soft indigo
    color = color_map.get(status_type, color)
    
    return discord.Embed(
        description=message,
        color=color
    )
