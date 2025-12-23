"""
Spotify Integration Helper for Discord Music Bot.
Extracts track information from Spotify links for playback via YouTube.
"""

import re
import os

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    print("⚠️  Spotipy not installed. Spotify links will not work.")


class SpotifyHandler:
    """
    Handler for Spotify link processing.
    Extracts track/playlist info and searches YouTube for playback.
    """
    
    def __init__(self):
        """Initialize Spotify client (lazy initialization)."""
        self.sp = None
        self._initialized = False
        self._init_attempted = False
    
    def _ensure_initialized(self):
        """Lazy initialization of Spotify client."""
        if self._init_attempted:
            return self._initialized
        
        self._init_attempted = True
        
        if not SPOTIPY_AVAILABLE:
            print("⚠️  Spotipy not available.")
            return False
        
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        # Debug: Print what we got (masked)
        print(f"🔍 Spotify Client ID: {'*' * 8 + client_id[-4:] if client_id else 'NOT SET'}")
        print(f"🔍 Spotify Client Secret: {'*' * 8 + client_secret[-4:] if client_secret else 'NOT SET'}")
        
        if client_id and client_secret:
            try:
                auth_manager = SpotifyClientCredentials(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                # Test the connection
                self.sp.search(q='test', limit=1)
                self._initialized = True
                print("✅ Spotify integration initialized!")
                return True
            except Exception as e:
                print(f"⚠️  Spotify initialization failed: {e}")
                return False
        else:
            print("⚠️  Spotify credentials not found in environment variables.")
            return False
    
    @property
    def is_available(self):
        """Check if Spotify API is available."""
        return self._ensure_initialized() and self.sp is not None
    
    def extract_spotify_id(self, url):
        """
        Extract Spotify ID and type from URL.
        
        Args:
            url: Spotify URL
        
        Returns:
            Tuple of (type, id) or (None, None) if invalid
        """
        patterns = {
            'track': r'spotify\.com/track/([a-zA-Z0-9]+)',
            'playlist': r'spotify\.com/playlist/([a-zA-Z0-9]+)',
            'album': r'spotify\.com/album/([a-zA-Z0-9]+)',
        }
        
        for content_type, pattern in patterns.items():
            match = re.search(pattern, url)
            if match:
                return content_type, match.group(1)
        
        return None, None
    
    async def get_track_info(self, track_id):
        """
        Get track information from Spotify.
        
        Args:
            track_id: Spotify track ID
        
        Returns:
            Search query for YouTube
        """
        if not self.is_available:
            return None
        
        try:
            track = self.sp.track(track_id)
            artist = track['artists'][0]['name']
            title = track['name']
            return f"{artist} - {title}"
        except Exception as e:
            print(f"Error fetching Spotify track: {e}")
            return None
    
    async def get_playlist_tracks(self, playlist_id):
        """
        Get all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID
        
        Returns:
            List of search queries for YouTube
        """
        if not self.is_available:
            return []
        
        try:
            tracks = []
            results = self.sp.playlist_tracks(playlist_id)
            
            while results:
                for item in results['items']:
                    track = item.get('track')
                    if track:
                        artist = track['artists'][0]['name']
                        title = track['name']
                        tracks.append(f"{artist} - {title}")
                
                # Get next page if exists
                if results['next']:
                    results = self.sp.next(results)
                else:
                    break
            
            return tracks
        except Exception as e:
            print(f"Error fetching Spotify playlist: {e}")
            return []
    
    async def get_album_tracks(self, album_id):
        """
        Get all tracks from a Spotify album.
        
        Args:
            album_id: Spotify album ID
        
        Returns:
            List of search queries for YouTube
        """
        if not self.is_available:
            return []
        
        try:
            tracks = []
            album = self.sp.album(album_id)
            
            for track in album['tracks']['items']:
                artist = track['artists'][0]['name']
                title = track['name']
                tracks.append(f"{artist} - {title}")
            
            return tracks
        except Exception as e:
            print(f"Error fetching Spotify album: {e}")
            return []
    
    async def process_spotify_url(self, url):
        """
        Process a Spotify URL and return YouTube search queries.
        
        Args:
            url: Spotify URL
        
        Returns:
            List of search queries or single query string
        """
        content_type, spotify_id = self.extract_spotify_id(url)
        
        if not spotify_id:
            return None
        
        # If Spotify API not available, extract from URL and search
        if not self.is_available:
            # Try to extract from URL path as fallback
            return None
        
        if content_type == 'track':
            query = await self.get_track_info(spotify_id)
            return [query] if query else None
        
        elif content_type == 'playlist':
            return await self.get_playlist_tracks(spotify_id)
        
        elif content_type == 'album':
            return await self.get_album_tracks(spotify_id)
        
        return None
