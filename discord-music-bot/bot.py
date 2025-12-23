"""
Discord Music Bot - Main Entry Point
=====================================
A fully functional Discord music bot with YouTube and Spotify support.

Author: Created with ❤️
"""

import discord
from discord.ext import commands
import asyncio
import logging

from config import DISCORD_TOKEN, BOT_PREFIX

# ============================================
# Logging Configuration
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('discord_music_bot')

# ============================================
# Bot Configuration
# ============================================
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix=BOT_PREFIX,
    intents=intents,
    description="🎵 A powerful Discord Music Bot with YouTube & Spotify support!"
)


# ============================================
# Bot Events
# ============================================
@bot.event
async def on_ready():
    """Called when the bot is ready."""
    print("=" * 50)
    print(f"🎵 {bot.user.name} is now online!")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"📡 Connected to {len(bot.guilds)} server(s)")
    print(f"🔧 Prefix: {BOT_PREFIX}")
    print("=" * 50)
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{BOT_PREFIX}help | Music"
        )
    )
    
    logger.info(f"Bot is ready! Logged in as {bot.user}")


@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new server."""
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    # Try to send a welcome message
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="🎵 Thanks for adding me!",
                description=(
                    f"I'm a music bot ready to play your favorite tunes!\n\n"
                    f"**Get started:**\n"
                    f"• `{BOT_PREFIX}join` - Join your voice channel\n"
                    f"• `{BOT_PREFIX}play <song>` - Play a song\n"
                    f"• `{BOT_PREFIX}help` - See all commands\n\n"
                    f"**Supported sources:** YouTube, Spotify"
                ),
                color=0x1DB954
            )
            await channel.send(embed=embed)
            break


@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ I don't have permission to do that!")
    
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Command on cooldown! Try again in {error.retry_after:.1f}s")
    
    else:
        logger.error(f"Command error: {error}")
        await ctx.send(f"❌ An error occurred: {str(error)}")


# ============================================
# Custom Help Command
# ============================================
class MusicHelpCommand(commands.HelpCommand):
    """Custom help command with better formatting."""
    
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="🎵 Music Bot Commands",
            description=f"Use `{BOT_PREFIX}help <command>` for more info on a command.",
            color=0x1DB954
        )
        
        embed.add_field(
            name="🎤 Voice",
            value=f"`{BOT_PREFIX}join` - Join voice channel\n`{BOT_PREFIX}leave` - Leave voice channel",
            inline=False
        )
        
        embed.add_field(
            name="🎵 Playback",
            value=(
                f"`{BOT_PREFIX}play <song>` - Play a song\n"
                f"`{BOT_PREFIX}pause` - Pause playback\n"
                f"`{BOT_PREFIX}resume` - Resume playback\n"
                f"`{BOT_PREFIX}stop` - Stop and clear queue\n"
                f"`{BOT_PREFIX}skip` - Skip current song"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📋 Queue",
            value=(
                f"`{BOT_PREFIX}queue` - View queue\n"
                f"`{BOT_PREFIX}nowplaying` - Current song\n"
                f"`{BOT_PREFIX}shuffle` - Shuffle queue\n"
                f"`{BOT_PREFIX}clear` - Clear queue\n"
                f"`{BOT_PREFIX}remove <#>` - Remove song"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Settings",
            value=(
                f"`{BOT_PREFIX}volume <0-100>` - Set volume\n"
                f"`{BOT_PREFIX}loop` - Toggle song loop\n"
                f"`{BOT_PREFIX}loopqueue` - Toggle queue loop"
            ),
            inline=False
        )
        
        embed.set_footer(text="🎧 Supports YouTube URLs, Spotify links, and search queries!")
        
        await self.get_destination().send(embed=embed)
    
    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"Command: {BOT_PREFIX}{command.name}",
            description=command.help or "No description available.",
            color=0x1DB954
        )
        
        if command.aliases:
            embed.add_field(
                name="Aliases",
                value=", ".join([f"`{BOT_PREFIX}{alias}`" for alias in command.aliases]),
                inline=False
            )
        
        await self.get_destination().send(embed=embed)


bot.help_command = MusicHelpCommand()


# ============================================
# Load Cogs and Run Bot
# ============================================
async def load_cogs():
    """Load all cogs."""
    try:
        await bot.load_extension('cogs.music')
        logger.info("Loaded music cog successfully!")
    except Exception as e:
        logger.error(f"Failed to load music cog: {e}")


async def main():
    """Main function to start the bot."""
    if not DISCORD_TOKEN:
        print("=" * 50)
        print("❌ ERROR: No Discord token found!")
        print("")
        print("Please set up your bot token:")
        print("1. Create a '.env' file in this folder")
        print("2. Add: DISCORD_TOKEN=your_token_here")
        print("")
        print("Get your token from:")
        print("https://discord.com/developers/applications")
        print("=" * 50)
        return
    
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutting down...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
