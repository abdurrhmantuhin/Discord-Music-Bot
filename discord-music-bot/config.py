"""
Configuration settings for the Discord Music Bot.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# Discord Bot Configuration
# ============================================
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_PREFIX = '!'

# ============================================
# Spotify Configuration (Optional)
# ============================================
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')

# Spotify OAuth Scopes
SPOTIFY_SCOPE = "user-library-read playlist-read-private playlist-read-collaborative user-top-read"
SPOTIFY_CACHE_PATH = ".spotify_cache"

# ============================================
# YT-DLP Configuration
# ============================================
YTDL_FORMAT_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'extract_flat': False,
}

# ============================================
# FFmpeg Configuration
# ============================================
import shutil

# Find FFmpeg executable
FFMPEG_EXECUTABLE = shutil.which('ffmpeg') or 'ffmpeg'

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
    'executable': FFMPEG_EXECUTABLE
}

# ============================================
# Bot Settings
# ============================================
DEFAULT_VOLUME = 0.5  # 50% volume
MAX_QUEUE_SIZE = 100
DISCONNECT_TIMEOUT = 300  # 5 minutes of inactivity

# ============================================
# Embed Colors
# ============================================
EMBED_COLOR = 0x1DB954  # Spotify green
ERROR_COLOR = 0xFF0000  # Red
SUCCESS_COLOR = 0x00FF00  # Green
