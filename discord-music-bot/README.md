# 🎵 Discord Music Bot

> **The ultimate lightweight, high-performance music bot for your Discord server.**
> *Stream music from YouTube and Spotify with zero lag, rich embeds, and smart queue management.*

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![Discord.py Version](https://img.shields.io/badge/discord.py-2.3+-5865F2.svg?style=for-the-badge&logo=discord&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-success.svg?style=for-the-badge)

---

## 🚀 Features

This bot is built for speed and reliability, featuring advanced optimizations not found in basic music bots.

- **🎵 Multi-Platform Support**:  
  - **YouTube**: Direct videos, playlists, and search.
  - **Spotify**: Tracks, albums, and playlists (converted to YouTube for playback).
- **⚡ High Performance**:  
  - **Parallel Playlist Loading**: Loads large playlists in the background (10x faster).
  - **Instant Playback**: First song plays immediately while others load.
  - **Smart Caching**: Caches popular songs (`.spotify_cache`) for instant future playback.
- **🎧 Advanced Controls**:  
  - **Loop Modes**: Single song loop (`!loop`) or entire queue loop (`!loopqueue`).
  - **Queue Management**: Shuffle, remove specific songs, logical queue ordering.
  - **Volume Control**: Adjustable playback volume.
- **✨ Professional Experience**:  
  - **Rich Embeds**: Beautiful "Now Playing" and "Added to Queue" notifications with thumbnails.
  - **Error Handling**: Friendly error messages instead of technical jargon.
  - **Auto-Cleanup**: Automatically disconnects after 5 minutes of inactivity to save resources.

---

## 🎬 Demo

Play music instantly with simple commands:

```bash
!play Blinding Lights       # Search and play
!play <spotify_playlist>    # Load entire Spotify playlist
!loop                       # Loop your favorite song
```

---

## ⚡ Quick Start

Get your bot running in under 5 minutes.

### Prerequisites
- **Python 3.11+**
- **FFmpeg** (Required for audio streaming)
- **Discord Bot Token**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-music-bot.git
   cd discord-music-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg**
   - **Windows**: `choco install ffmpeg` (using Chocolatey) or [download manually](https://ffmpeg.org/download.html).
   - **Debian/Ubuntu**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

4. **Configure Environment**
   Create a `.env` file in the root directory:
   ```env
   DISCORD_TOKEN=your_token_here
   ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

---

## 🛠️ Configuration

### Environment Variables (.env)

| Variable | Required | Description |
|----------|:--------:|-------------|
| `DISCORD_TOKEN` | ✅ | Your Discord Bot Token from [Developer Portal](https://discord.com/developers/applications). |
| `SPOTIFY_CLIENT_ID` | ❌ | Required for Spotify support. Get it from [Spotify Dashboard](https://developer.spotify.com/dashboard). |
| `SPOTIFY_CLIENT_SECRET` | ❌ | Required for Spotify support. |
| `SPOTIFY_REDIRECT_URI` | ❌ | URI for Spotify OAuth (default: `http://127.0.0.1:8888/callback`). |

### Spotify Setup (Optional)
To enable Spotify support (Playlists/Albums):
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create an App and get your **Client ID** and **Client Secret**.
3. Add them to your `.env` file.
4. Run the setup script to authorize:
   ```bash
   python setup_spotify.py
   ```
   *Note: Without Spotify credentials, only YouTube links will work.*

### Bot Settings (`config.py`)
You can tweak advanced settings in `config.py`:
- `DEFAULT_VOLUME`: Default volume (0.0 - 1.0).
- `MAX_QUEUE_SIZE`: Maximum songs in queue (default: 100).
- `DISCONNECT_TIMEOUT`: Time in seconds before bot leaves empty channel (default: 300s).

---

## 🎮 Commands

All commands are case-insensitive. Default prefix: `!`

| Command | Aliases | Description | Example |
|:--------|:--------|:------------|:--------|
| **`!play <query>`** | `p` | Play song or playlist (YouTube/Spotify) | `!p Starboy` |
| **`!pause`** | - | Pause playback | `!pause` |
| **`!resume`** | `unpause` | Resume playback | `!resume` |
| **`!stop`** | `s` | Stop playback and clear queue | `!s` |
| **`!skip`** | `n`, `next` | Skip current song | `!n` |
| **`!queue`** | `q`, `playlist` | Show current queue | `!q` |
| **`!loop`** | `l`, `repeat` | Toggle single song loop | `!loop` |
| **`!loopqueue`** | `lq`, `queueloop` | Toggle entire queue loop | `!lq` |
| **`!shuffle`** | `sh` | Shuffle current queue | `!shuffle` |
| **`!remove <#>`** | `rm` | Remove song at specific position | `!rm 3` |
| **`!clear`** | `cl` | Clear the entire queue | `!clear` |
| **`!volume <0-100>`** | `v`, `vol` | Set volume percentage | `!v 80` |
| **`!nowplaying`** | `np`, `current` | Show current song info | `!np` |
| **`!join`** | `j`, `connect` | Join voice channel | `!join` |
| **`!leave`** | `dc`, `disconnect` | Disconnect from voice | `!leave` |

---

## 🌐 Deployment

### 1. Local Development
Simply run with Python:
```bash
python bot.py
```

### 2. Railway (Recommended)
This project includes `nixpacks.toml` optimized for Railway.
1. Fork this repo.
2. Create a new project on [Railway](https://railway.app/).
3. Connect your GitHub repo.
4. Add your Environment Variables (`DISCORD_TOKEN`, etc.).
5. Deploy!

### 3. Docker
Build and run the container:
```bash
docker build -t discord-music-bot .
docker run -d --env-file .env discord-music-bot
```

### 4. VPS / Linux Service
Use `systemd` to keep the bot running 24/7.
<details>
<summary>Click for Service File Example</summary>

Create `/etc/systemd/system/musicbot.service`:
```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/discord-music-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```
</details>

---

## 📂 Project Structure

```
discord-music-bot/
├── bot.py                 # 🤖 Main bot entry point
├── config.py              # ⚙️ Configuration constants
├── setup_spotify.py       # 🔐 Spotify OAuth helper
├── requirements.txt       # 📦 Dependencies
├── nixpacks.toml          # 🚂 Railway build config
├── cogs/
│   └── music.py           # 🎵 Main music logic (Commands & Events)
└── utils/
    ├── ytdl.py            # 📺 YouTube-DL / yt-dlp handler
    ├── spotify.py         # 🟢 Spotify API handler
    ├── messages.py        # 💬 Text formatting utils
    └── embeds.py          # 🎨 Discord Embed builders
```

---

## ⚠️ Troubleshooting

**Bot not playing audio?**
- Ensure **FFmpeg** is installed and added to your system PATH.
- Check if the bot has `Connect` and `Speak` permissions in the voice channel.

**"Video unavailable" errors?**
- This usually means age-restricted content or region locks.
- The bot is configured to skip errors and play the next song automatically.

**Spotify playlists not loading?**
- Verify your `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.
- Ensure the playlist is Public.
- For private playlists, you must run `setup_spotify.py` locally first to generate the `.spotify_cache` token.

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙌 Credits

- **[discord.py](https://github.com/Rapptz/discord.py)**: The core library.
- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)**: High-speed media downloader.
- **[Spotipy](https://spotipy.readthedocs.io/)**: Lightweight Spotify API wrapper.
