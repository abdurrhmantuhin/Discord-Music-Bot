# 🎵 Discord Music Bot

A fully functional Discord music bot with **YouTube** and **Spotify** support! Play your favorite music directly in Discord voice channels.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blueviolet?logo=discord)

---

## ✨ Features

- 🎵 **YouTube Support** - Play songs via URL or search
- 🎧 **Spotify Support** - Play tracks, playlists, and albums from Spotify links
- 📋 **Queue Management** - Add, remove, shuffle, and clear songs
- 🔊 **Volume Control** - Adjustable volume (0-100)
- 🔂 **Loop Mode** - Loop single song or entire queue
- 🎨 **Rich Embeds** - Beautiful now playing and queue displays

---

## 📋 Commands

| Command | Description |
|---------|-------------|
| `!join` | Join your voice channel |
| `!leave` | Leave voice channel |
| `!play <song>` | Play from YouTube or Spotify (URL or search) |
| `!pause` | Pause current song |
| `!resume` | Resume playback |
| `!stop` | Stop and clear queue |
| `!skip` | Skip to next song |
| `!queue` | View the queue |
| `!nowplaying` | Show current song |
| `!volume <0-100>` | Set volume |
| `!shuffle` | Shuffle the queue |
| `!clear` | Clear the queue |
| `!loop` | Toggle song loop |
| `!loopqueue` | Toggle queue loop |
| `!remove <#>` | Remove song from queue |

---

## 🚀 Setup Guide

### Prerequisites

1. **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
2. **FFmpeg** - Required for audio processing

### Installing FFmpeg on Windows

**Option 1: Using Chocolatey (Recommended)**
```powershell
choco install ffmpeg
```

**Option 2: Manual Installation**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH

### Bot Setup

#### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → Name it → **"Create"**
3. Go to **Bot** tab → Click **"Add Bot"**
4. Under **TOKEN**, click **"Copy"** (save this!)
5. Enable these **Privileged Gateway Intents**:
   - ✅ MESSAGE CONTENT INTENT
6. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Connect`, `Speak`, `Embed Links`
7. Copy the generated URL and invite the bot to your server

#### Step 2: Setup Project

```powershell
# Navigate to bot folder
cd discord-music-bot

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
```

#### Step 3: Configure Bot Token

Edit the `.env` file and add your bot token:

```env
DISCORD_TOKEN=your_bot_token_here
```

#### Step 4 (Optional): Spotify Support

For Spotify link support, add Spotify API credentials:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app and get Client ID & Secret
3. Add to `.env`:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

### Run the Bot

```powershell
python bot.py
```

You should see:
```
==================================================
🎵 YourBotName is now online!
🆔 Bot ID: 123456789
📡 Connected to 1 server(s)
🔧 Prefix: !
==================================================
```

---

## 📁 Project Structure

```
discord-music-bot/
├── bot.py              # Main entry point
├── config.py           # Bot configuration
├── requirements.txt    # Dependencies
├── .env                # Your secrets (create this!)
├── .env.example        # Template for .env
├── cogs/
│   └── music.py        # Music commands
└── utils/
    ├── ytdl.py         # YouTube handler
    └── spotify.py      # Spotify handler
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Bot won't start | Check if `DISCORD_TOKEN` is set in `.env` |
| No audio playing | Make sure FFmpeg is installed and in PATH |
| "No module named X" | Run `pip install -r requirements.txt` |
| Spotify links not working | Add Spotify API credentials to `.env` |

---

## 📄 License

This project is open source and available for personal use.

---

Made with ❤️ for music lovers!
