# Use Python 3.11 slim image
FROM python:3.11-slim

# Install FFmpeg and other audio dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus0 \
    libsodium23 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY discord-music-bot/ ./discord-music-bot/

# Set working directory to bot folder
WORKDIR /app/discord-music-bot

# Run the bot
CMD ["python", "bot.py"]
