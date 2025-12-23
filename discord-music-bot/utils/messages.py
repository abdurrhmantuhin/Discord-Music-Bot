"""
Centralized Message System for Discord Music Bot.
All user-facing messages in one place for easy management.
"""

import discord
from enum import Enum


# ============================================
# Color Constants
# ============================================

class Colors:
    """Embed colors for different message types."""
    SUCCESS = 0x2ECC71   # Green
    ERROR = 0xE74C3C     # Red
    WARNING = 0xF39C12   # Orange
    INFO = 0x3498DB      # Blue
    MUSIC = 0x1DB954     # Spotify Green


# ============================================
# Voice Channel Messages
# ============================================

class Voice:
    """Voice channel related messages."""
    JOIN_FIRST = "❌ Join a voice channel first — I can't play music alone."
    NOT_SAME_CHANNEL = "❌ We need to be in the same voice channel."
    ALREADY_PLAYING = "❌ I'm already playing music in another channel."
    NOT_CONNECTED = "❌ I'm not connected to any voice channel."
    JOINED = "🎵 Joined **{channel}**!"
    MOVED = "🎵 Moved to **{channel}**!"
    DISCONNECTED = "👋 Disconnected from voice."
    KICKED = "🥺 Oh no! I got kicked from the voice channel..."


# ============================================
# Playback Messages
# ============================================

class Playback:
    """Playback related messages."""
    NOTHING_PLAYING = "❌ Nothing is playing right now."
    TRACK_ERROR = "❌ This track couldn't be played."
    QUEUE_EMPTY = "❌ The queue is currently empty."
    NO_RESULTS = "❌ I couldn't find any results for that."
    FORMAT_ERROR = "❌ This format isn't supported yet."
    NOW_PLAYING = "🎶 Now playing"
    PAUSED = "⏸️ Playback paused."
    RESUMED = "▶️ Playback resumed."
    SKIPPED = "⏭️ Skipped."
    STOPPED = "⏹️ Playback stopped."
    ADDED_TO_QUEUE = "✅ Added to queue: **{title}**"
    ADDED_MULTIPLE = "✅ Added **{count}** songs to queue!"


# ============================================
# Button/Control Messages
# ============================================

class Controls:
    """Button and control related messages."""
    NOT_ALLOWED = "❌ You're not allowed to use these controls."
    MUST_BE_IN_VC = "❌ Only users in the voice channel can use this."
    DJ_REQUIRED = "❌ DJ role required to use this control."
    COOLDOWN = "⏳ Easy there... try again in a moment."
    NOTHING_TO_SKIP = "❌ Nothing to skip!"
    NOTHING_TO_PAUSE = "❌ Nothing to pause!"


# ============================================
# Queue/Loop Messages
# ============================================

class Queue:
    """Queue and loop related messages."""
    NOTHING_TO_LOOP = "❌ There's nothing to loop right now."
    NEED_TRACKS = "❌ Queue must have at least one track."
    TRACK_NOT_FOUND = "❌ That track doesn't exist in the queue."
    QUEUE_CLEARED = "🗑️ Queue cleared!"
    LOOP_SONG = "🔂 Song loop enabled."
    LOOP_QUEUE = "🔁 Queue loop enabled."
    LOOP_OFF = "➡️ Loop disabled."
    SHUFFLED = "🔀 Queue shuffled!"


# ============================================
# Volume Messages
# ============================================

class Volume:
    """Volume related messages."""
    INVALID_RANGE = "❌ Volume must be between 1% and 100%."
    UNAVAILABLE = "❌ Volume control is unavailable right now."
    SET = "🔊 Volume set to **{level}%**"
    INCREASED = "🔊 Volume: **{level}%**"
    DECREASED = "🔉 Volume: **{level}%**"


# ============================================
# Spotify Messages  
# ============================================

class Spotify:
    """Spotify related messages."""
    NOT_AVAILABLE = "❌ Spotify integration is not available."
    PROCESSING = "🎵 Processing Spotify link..."
    PLAYLIST_ERROR = "❌ Couldn't access this playlist. It might be private or algorithmic."
    NO_TRACKS = "❌ No playable tracks found in this playlist."


# ============================================
# Generic/System Messages
# ============================================

class System:
    """Generic system messages."""
    UNKNOWN_ERROR = "⚠️ Something went wrong — please try again."
    UNEXPECTED = "⚠️ I ran into an unexpected issue."
    ACTION_FAILED = "⚠️ That action couldn't be completed."
    TIMEOUT = "⏰ Request timed out. Please try again."
    RATE_LIMITED = "⏳ Too many requests. Please slow down."


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
