"""
Professional Message System for Discord Music Bot.
All user-facing messages - Clear, direct, and professional.
"""

import discord
from enum import Enum


# ============================================
# Professional Message System
# ============================================
# Style Guide:
# - Direct and actionable
# - Minimal emojis (functional only)
# - No anthropomorphization ("I", "me")
# - Consistent structure
# - Professional tone for mature users
# ============================================


# ============================================
# Color Constants
# ============================================

class Colors:
    """Unified color scheme for all embeds."""
    PRIMARY = 0xAFC6E9  # Soft Pastel Blue
    
    # Aliases for compatibility
    SUCCESS = ERROR = WARNING = INFO = MUSIC = PRIMARY
    UNIFIED = PRIMARY


# ============================================
# Voice Channel Messages
# ============================================

class Voice:
    """Voice channel related messages."""
    JOIN_FIRST = "❌ Join a voice channel to use this command"
    NOT_SAME_CHANNEL = "❌ Must be in the same voice channel as the bot"
    ALREADY_PLAYING = "❌ Already active in another voice channel"
    NOT_CONNECTED = "❌ Not connected to a voice channel"
    JOINED = "✅ Connected to {channel}"
    MOVED = "✅ Moved to {channel}"
    DISCONNECTED = "✅ Disconnected from voice channel"
    KICKED = "⚠️ Disconnected from voice channel"


# ============================================
# Playback Messages
# ============================================

class Playback:
    """Playback related messages."""
    NOTHING_PLAYING = "❌ No track currently playing"
    TRACK_ERROR = "❌ Unable to play this track"
    QUEUE_EMPTY = "❌ Queue is empty"
    NO_RESULTS = "❌ No results found for that query"
    FORMAT_ERROR = "❌ Unsupported media format"
    NOW_PLAYING = "▶️ Now playing"
    PAUSED = "⏸️ Paused"
    RESUMED = "▶️ Resumed"
    SKIPPED = "⏭️ Skipped"
    STOPPED = "⏹️ Stopped"
    ADDED_TO_QUEUE = "✅ Added to queue: **{title}**"
    ADDED_MULTIPLE = "✅ Added {count} tracks to queue"


# ============================================
# Control Messages
# ============================================

class Controls:
    """Button and control related messages."""
    NOT_ALLOWED = "❌ Insufficient permissions for this control"
    MUST_BE_IN_VC = "❌ Must be in voice channel to use controls"
    DJ_REQUIRED = "❌ DJ role required"
    COOLDOWN = "⏳ Command on cooldown"
    NOTHING_TO_SKIP = "❌ No track to skip"
    NOTHING_TO_PAUSE = "❌ No track to pause"


# ============================================
# Queue Messages
# ============================================

class Queue:
    """Queue and loop related messages."""
    NOTHING_TO_LOOP = "❌ No active track to loop"
    NEED_TRACKS = "❌ Queue requires at least one track"
    TRACK_NOT_FOUND = "❌ Track not found in queue"
    QUEUE_CLEARED = "✅ Queue cleared"
    LOOP_SONG = "🔂 Track loop enabled"
    LOOP_QUEUE = "🔁 Queue loop enabled"
    LOOP_OFF = "✅ Loop disabled"
    SHUFFLED = "🔀 Queue shuffled"


# ============================================
# Volume Messages
# ============================================

class Volume:
    """Volume related messages."""
    INVALID_RANGE = "❌ Volume must be 1-100%"
    UNAVAILABLE = "❌ Volume control unavailable"
    SET = "🔊 Volume: {level}%"
    INCREASED = "🔊 Volume: {level}%"
    DECREASED = "🔉 Volume: {level}%"


# ============================================
# Spotify Messages
# ============================================

class Spotify:
    """Spotify related messages."""
    NOT_AVAILABLE = "❌ Spotify integration unavailable"
    PROCESSING = "⏳ Processing Spotify link"
    PLAYLIST_ERROR = "❌ Unable to access playlist (may be private or algorithmic)"
    NO_TRACKS = "❌ No playable tracks in this playlist"


# ============================================
# System Messages
# ============================================

class System:
    """System and error messages."""
    UNKNOWN_ERROR = "❌ An error occurred, try again"
    UNEXPECTED = "❌ Unexpected error occurred"
    ACTION_FAILED = "❌ Action failed"
    TIMEOUT = "❌ Request timed out"
    RATE_LIMITED = "⏳ Rate limit exceeded, try again shortly"


# ============================================
# Helper Functions
# ============================================

async def send_error(ctx, message: str, ephemeral: bool = False):
    """
    Send an error message.
    
    Args:
        ctx: Command context or interaction
        message: Error message to send
        ephemeral: Whether to send as ephemeral (only for interactions)
    """
    embed = discord.Embed(description=message, color=Colors.ERROR)
    
    if hasattr(ctx, 'response'):  # It's an interaction
        if ctx.response.is_done():
            await ctx.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
    else:  # It's a context
        await ctx.send(embed=embed)


async def send_success(ctx, message: str, ephemeral: bool = False):
    """
    Send a success message.
    
    Args:
        ctx: Command context or interaction
        message: Success message to send
        ephemeral: Whether to send as ephemeral (only for interactions)
    """
    embed = discord.Embed(description=message, color=Colors.SUCCESS)
    
    if hasattr(ctx, 'response'):  # It's an interaction
        if ctx.response.is_done():
            await ctx.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
    else:  # It's a context
        await ctx.send(embed=embed)


async def send_info(ctx, message: str, ephemeral: bool = False):
    """
    Send an info message.
    
    Args:
        ctx: Command context or interaction
        message: Info message to send
        ephemeral: Whether to send as ephemeral (only for interactions)
    """
    embed = discord.Embed(description=message, color=Colors.INFO)
    
    if hasattr(ctx, 'response'):  # It's an interaction
        if ctx.response.is_done():
            await ctx.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
    else:  # It's a context
        await ctx.send(embed=embed)


async def reply_ephemeral(interaction: discord.Interaction, message: str):
    """
    Quick helper for ephemeral button responses.
    
    Args:
        interaction: Button interaction
        message: Message to send
    """
    try:
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except:
        pass  # Silently fail if interaction expired
