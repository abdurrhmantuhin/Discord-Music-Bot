"""
Spotify Authorization Script
run this script locally to authorize the bot to access your Spotify account.
This is required for:
- Private playlists
- Personalized playlists (Discover Weekly, etc.)
"""

import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
SCOPE = "user-library-read playlist-read-private playlist-read-collaborative user-top-read"
CACHE_PATH = ".spotify_cache"

def setup_spotify():
    """Run the interactive Spotify setup."""
    print("🎵 Spotify Authorization Setup")
    print("=" * 30)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Error: Missing Spotify credentials in .env file.")
        print("Please make sure you have SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET set.")
        return

    print(f"Client ID found: {CLIENT_ID[:5]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print("\nRequesting authorization...")
    
    try:
        sp_oauth = SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            cache_path=CACHE_PATH,
            open_browser=True
        )
        
        # This will open the browser and trigger theauth flow
        token_info = sp_oauth.get_access_token()
        
        if token_info:
            print("\n✅ Authorization successful!")
            print(f"🔑 Token saved to: {os.path.abspath(CACHE_PATH)}")
            print("\nNext steps:")
            print("1. This file (.spotify_cache) contains your access credentials.")
            print("2. The bot will use this file to access your playlists.")
            print("3. IMPORTANT: If deploying to Railway/Cloud, you need to upload this file")
            print("   OR copy its contents to a SPOTIFY_TOKEN_CACHE environment variable.")
        else:
            print("\n❌ Authorization failed.")
            
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        print("\nTroubleshooting:")
        print("- Check if 'Redirect URI' in your Spotify Developer Dashboard matches exactly.")
        print(f"  Expected: {REDIRECT_URI}")
        print("- Check your Client ID and Secret.")

if __name__ == "__main__":
    setup_spotify()
