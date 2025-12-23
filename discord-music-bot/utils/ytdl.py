"""
YouTube-DL Source Handler for Discord Music Bot.
Handles audio extraction from YouTube and other sources.
"""

import asyncio
import discord
import yt_dlp
import re
from config import YTDL_FORMAT_OPTIONS, FFMPEG_OPTIONS


# Create YT-DLP instance
ytdl = yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)


class YTDLSource(discord.PCMVolumeTransformer):
    """
    Audio source that uses YT-DLP to stream audio.
    Inherits from PCMVolumeTransformer for volume control.
    """
    
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.webpage_url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')
    
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True, volume=0.5):
        """
        Create a YTDLSource from a URL.
        
        Args:
            url: YouTube URL or search query
            loop: Event loop to use
            stream: Whether to stream or download
            volume: Initial volume (0.0 to 1.0)
        
        Returns:
            YTDLSource instance or list of song data for playlists
        """
        loop = loop or asyncio.get_event_loop()
        
        try:
            data = await loop.run_in_executor(
                None, 
                lambda: ytdl.extract_info(url, download=not stream)
            )
        except Exception as e:
            raise Exception(f"Could not extract info: {str(e)}")
        
        if data is None:
            raise Exception("Could not find any results")
        
        # Handle playlists
        if 'entries' in data:
            entries = data['entries']
            if not entries:
                raise Exception("Playlist is empty")
            
            # Return list of song data for queue
            songs = []
            for entry in entries:
                if entry:
                    songs.append({
                        'title': entry.get('title', 'Unknown'),
                        'webpage_url': entry.get('webpage_url') or entry.get('url'),
                        'duration': entry.get('duration'),
                        'thumbnail': entry.get('thumbnail'),
                        'uploader': entry.get('uploader', 'Unknown')
                    })
            return songs
        
        # Single video
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        
        return cls(
            discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS),
            data=data,
            volume=volume
        )
    
    @classmethod
    async def search(cls, query, *, loop=None):
        """
        Search YouTube for a query and return first result.
        
        Args:
            query: Search query string
            loop: Event loop to use
        
        Returns:
            Dictionary with song info
        """
        loop = loop or asyncio.get_event_loop()
        
        search_query = f"ytsearch:{query}"
        
        try:
            data = await loop.run_in_executor(
                None,
                lambda: ytdl.extract_info(search_query, download=False)
            )
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
        
        if not data or 'entries' not in data or not data['entries']:
            raise Exception("No results found")
        
        # Return first result
        entry = data['entries'][0]
        return {
            'title': entry.get('title', 'Unknown'),
            'webpage_url': entry.get('webpage_url') or entry.get('url'),
            'duration': entry.get('duration'),
            'thumbnail': entry.get('thumbnail'),
            'uploader': entry.get('uploader', 'Unknown')
        }
    
    @staticmethod
    def format_duration(seconds):
        """Format duration in seconds to MM:SS or HH:MM:SS."""
        if seconds is None:
            return "Unknown"
        
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    @staticmethod
    def is_url(string):
        """Check if a string is a URL."""
        url_pattern = re.compile(
            r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|spotify\.com)/.+$'
        )
        return bool(url_pattern.match(string))
    
    @staticmethod
    def is_spotify_url(url):
        """Check if URL is a Spotify link."""
        return 'spotify.com' in url if url else False
    
    @staticmethod
    def is_youtube_url(url):
        """Check if URL is a YouTube link."""
        return any(domain in url for domain in ['youtube.com', 'youtu.be']) if url else False
