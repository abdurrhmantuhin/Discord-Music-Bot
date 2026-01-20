<div align="center">

# 🎵 Discord Music Bot

### A powerful, feature-rich Discord music bot with YouTube & Spotify integration

[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3%2B-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-Open%20Source-green?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](Dockerfile)

<br>

**Stream music from YouTube and Spotify directly in your Discord server.**  
*Queue management • Loop modes • Volume control • Rich embeds*

<br>

[Features](#-features) •
[Commands](#-commands) •
[Installation](#-installation) •
[Configuration](#-configuration) •
[Deployment](#-deployment) •
[Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎵 **YouTube Support** | Play songs via URL or search query |
| 🎧 **Spotify Integration** | Play tracks, playlists, and albums from Spotify links |
| 📋 **Queue Management** | Add, remove, shuffle, and clear songs from queue |
| 🔊 **Volume Control** | Adjustable volume from 0-100% |
| 🔂 **Loop Modes** | Loop single song or entire queue |
| 🎨 **Rich Embeds** | Beautiful now playing and queue displays |
| ⚡ **Fast & Reliable** | Optimized YT-DLP configuration for quick playback |
| 🐳 **Docker Ready** | Easy deployment with Docker support |

---

## � Commands

### Voice Commands
| Command | Description |
|---------|-------------|
| `!join` | Join your voice channel |
| `!leave` | Leave voice channel |

### Playback Commands
| Command | Description |
|---------|-------------|
| `!play <song>` | Play from YouTube or Spotify (URL or search) |
| `!pause` | Pause current song |
| `!resume` | Resume playback |
| `!stop` | Stop and clear queue |
| `!skip` | Skip to next song |

### Queue Commands
| Command | Description |
|---------|-------------|
| `!queue` | View the current queue |
| `!nowplaying` | Show currently playing song |
| `!shuffle` | Shuffle the queue |
| `!clear` | Clear the entire queue |
| `!remove <#>` | Remove song by position |

### Settings Commands
| Command | Description |
|---------|-------------|
| `!volume <0-100>` | Set playback volume |
| `!loop` | Toggle song loop |
| `!loopqueue` | Toggle queue loop |
| `!help` | Show all commands |

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+** — [Download Python](https://www.python.org/downloads/)
- **FFmpeg** — Required for audio processing

### Step 1: Install FFmpeg

<details>
<summary><b>Windows</b></summary>

**Using Chocolatey (Recommended):**
```powershell
choco install ffmpeg
```

**Manual Installation:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

</details>

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
sudo apt update && sudo apt install ffmpeg
```

</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install ffmpeg
```

</details>

### Step 2: Clone Repository

```bash
git clone https://github.com/your-username/Discord-Music-Bot.git
cd Discord-Music-Bot/discord-music-bot
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Name your bot → **"Create"**
3. Navigate to **Bot** tab → Click **"Add Bot"**
4. Copy the **TOKEN** (save this for later!)
5. Enable **Privileged Gateway Intents**:
   - ✅ `MESSAGE CONTENT INTENT`
6. Go to **OAuth2 → URL Generator**:
   - **Scopes:** `bot`, `applications.commands`
   - **Bot Permissions:** `Send Messages`, `Connect`, `Speak`, `Embed Links`
7. Copy the generated URL and invite the bot to your server

---

## ⚙️ Configuration

### Required: Discord Token

Create a `.env` file in the `discord-music-bot` folder:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### Optional: Spotify Integration

To enable Spotify link support:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new application
3. Get your **Client ID** and **Client Secret**
4. Add to your `.env` file:

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

---

## ▶️ Running the Bot

### Local Development

```bash
cd discord-music-bot
python bot.py
```

**Expected output:**
```
==================================================
🎵 YourBotName is now online!
🆔 Bot ID: 123456789
📡 Connected to 1 server(s)
🔧 Prefix: !
==================================================
```

---

## � Deployment

### Docker

Build and run with Docker:

```bash
# Build the image
docker build -t discord-music-bot .

# Run the container
docker run -d --env-file .env discord-music-bot
```

### Railway / Heroku

This bot is ready for cloud deployment with included:
- `Dockerfile` — Container configuration
- `Procfile` — Process file for Heroku
- `runtime.txt` — Python version specification
- `nixpacks.toml` — Railway configuration

---

## 📁 Project Structure

```
Discord-Music-Bot/
├── Dockerfile              # Docker configuration
├── requirements.txt        # Dependencies
├── README.md               # Documentation
│
└── discord-music-bot/
    ├── bot.py              # Main entry point
    ├── config.py           # Bot configuration
    ├── .env                # Your secrets (create this!)
    ├── .env.example        # Environment template
    │
    ├── cogs/
    │   └── music.py        # Music commands & queue
    │
    └── utils/
        ├── ytdl.py         # YouTube handler
        ├── spotify.py      # Spotify integration
        ├── embeds.py       # Rich embed templates
        ├── messages.py     # User message system
        └── cache.py        # Cache management
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Bot won't start** | Verify `DISCORD_TOKEN` is set correctly in `.env` |
| **No audio playing** | Ensure FFmpeg is installed and added to PATH |
| **"No module named X"** | Run `pip install -r requirements.txt` |
| **Spotify links not working** | Add Spotify API credentials to `.env` |
| **Bot disconnects randomly** | Check internet connection and Discord API status |
| **Permission denied** | Ensure bot has `Connect` and `Speak` permissions |

---

## 📄 Tech Stack

| Technology | Purpose |
|------------|---------|
| [discord.py](https://discordpy.readthedocs.io/) | Discord API wrapper |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube audio extraction |
| [spotipy](https://spotipy.readthedocs.io/) | Spotify API integration |
| [PyNaCl](https://pynacl.readthedocs.io/) | Voice encryption |
| [FFmpeg](https://ffmpeg.org/) | Audio processing |

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

---

## 📝 License

This project is open source and available for personal use.

---

<div align="center">

**Made with ❤️ for music lovers!**

*Star ⭐ this repo if you found it helpful!*

</div>
