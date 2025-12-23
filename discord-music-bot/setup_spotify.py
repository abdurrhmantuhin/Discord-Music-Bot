"""
Spotify Authorization Script (Simple Version)
Run this script locally to authorize the bot to access your Spotify account.
"""

import os
import sys
import webbrowser

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    from dotenv import load_dotenv
except ImportError:
    print("[ERROR] Missing dependencies!")
    print("Run: pip install spotipy python-dotenv")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Load environment variables
env_path = os.path.join(parent_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"[OK] Loaded .env from: {env_path}")
else:
    load_dotenv()
    print("[INFO] Loaded default .env")

# Configuration
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-library-read playlist-read-private playlist-read-collaborative user-top-read"
CACHE_PATH = os.path.join(current_dir, ".spotify_cache")

def setup_spotify():
    """Run the interactive Spotify setup."""
    print("\n" + "=" * 50)
    print("   SPOTIFY AUTHORIZATION SETUP")
    print("=" * 50)
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n[ERROR] Missing Spotify credentials!")
        print("Make sure your .env file has:")
        print("  SPOTIFY_CLIENT_ID=your_id_here")
        print("  SPOTIFY_CLIENT_SECRET=your_secret_here")
        return False

    print(f"\nClient ID: {CLIENT_ID[:8]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    
    # Create OAuth object WITHOUT auto-opening browser
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=CACHE_PATH,
        open_browser=False  # We'll open manually
    )
    
    # Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()
    
    print("\n" + "-" * 50)
    print("STEP 1: Copy this URL and open in browser:")
    print("-" * 50)
    print(auth_url)
    print("-" * 50)
    
    # Try to open browser automatically
    print("\n[Trying to open browser automatically...]")
    webbrowser.open(auth_url)
    
    print("\nSTEP 2: Login to Spotify and click 'Agree'")
    print("\nSTEP 3: After clicking Agree, you'll see a page.")
    print("        Copy the ENTIRE URL from your browser's address bar.")
    print("        (It will look like: http://127.0.0.1:8888/callback?code=...)")
    
    print("\n" + "-" * 50)
    redirect_response = input("Paste the URL here and press Enter: ").strip()
    print("-" * 50)
    
    if not redirect_response:
        print("\n[ERROR] No URL provided!")
        return False
    
    try:
        # Extract the code from the URL
        code = sp_oauth.parse_response_code(redirect_response)
        
        if not code:
            print("\n[ERROR] Could not extract authorization code from URL!")
            return False
        
        # Get the access token
        token_info = sp_oauth.get_access_token(code)
        
        if token_info:
            print("\n" + "=" * 50)
            print("   SUCCESS! Token saved!")
            print("=" * 50)
            print(f"\nToken file: {os.path.abspath(CACHE_PATH)}")
            print("\nYour bot can now access:")
            print("  - Private playlists")
            print("  - Discover Weekly")
            print("  - All personalized playlists")
            print("\nNext: Push this file to GitHub for Railway deployment.")
            return True
        else:
            print("\n[ERROR] Failed to get access token!")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        print("\nTroubleshooting:")
        print("- Make sure you copied the ENTIRE URL")
        print("- Make sure the Redirect URI in Spotify Dashboard matches exactly")
        return False

if __name__ == "__main__":
    try:
        success = setup_spotify()
        if success:
            print("\n[DONE] You can now close this window.")
        else:
            print("\n[FAILED] Please try again or check settings.")
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
    finally:
        input("\nPress Enter to close...")
