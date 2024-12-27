import discord
from discord.ext import tasks, commands
import requests
import asyncio
import os
from collections import defaultdict
from dotenv import load_dotenv
import random

# Load to env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))

# MGS-themed messages
MGS_QUOTES = [
    "Kept you waiting, huh?",
    "Snake? Snake?! SNAAAAKE!",
    "I'm no hero. Never was, never will be.",
    "Metal Gear?!",
    "War has changed...",
]

MGS_CODEC_SOUNDS = [
    "*codec ring*",
    "*codec beep*",
    "*codec static*",
]

class MGSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.polls = defaultdict(dict)
        self.remove_command('help')
        
    async def setup_hook(self):
        # Start background tasks here
        self.check_alerts.start()

    @tasks.loop(minutes=30)
    async def check_alerts(self):
        """Simulates random codec calls"""
        for guild in self.guilds:
            if random.random() < 0.3:  # 30% chance
                general = discord.utils.get(guild.text_channels, name='general')
                if general:
                    sound = random.choice(MGS_CODEC_SOUNDS)
                    quote = random.choice(MGS_QUOTES)
                    await general.send(f"{sound}\nColonel: {quote}")

bot = MGSBot()

# Enhanced welcome message
WELCOME_MESSAGE = """
```
╔══════════════════════════════════╗
  WELCOME TO MOTHER BASE, SOLDIER!
╚══════════════════════════════════╝

📡 CODEC FREQUENCY: 140.85

🔰 BASIC COMMANDS:
!codec   - Open codec menu
!intel   - Get latest intel
!mission - View current objectives
!alert - alert with user mention to know.

⚠ REMEMBER: Tactical Espionage Action ⚠
```
"""

@bot.event
async def on_member_join(member):
    channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🚀 Welcome to Mother Base!",
            description=WELCOME_MESSAGE,
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Soldier", value=f"{member.mention}", inline=False)
        await channel.send(embed=embed)

@bot.command(name='codec')
async def codec(ctx):
    """Simulates MGS codec conversation"""
    messages = [
        "*codec ring*",
        "Snake, do you copy?",
        f"I read you, {ctx.author.name}.",
        "Here's your mission briefing...",
    ]
    
    msg = await ctx.send(messages[0])
    for i in range(1, len(messages)):
        await asyncio.sleep(1.5)
        await msg.edit(content='\n'.join(messages[:i+1]))

@bot.command(name='intel')
async def intel(ctx):
    """Get latest news as intelligence reports"""
    try:
        params = {
            'apiKey': NEWS_API_KEY,
            'country': 'us',
            'pageSize': 3
        }
        response = requests.get('https://newsapi.org/v2/top-headlines', params=params)
        news = response.json().get('articles', [])
        
        if not news:
            await ctx.send("❗ No intel available at this time.")
            return

        intel_report = discord.Embed(
            title="⚠ INTEL REPORT ⚠",
            color=discord.Color.red()
        )
        
        for i, article in enumerate(news, 1):
            intel_report.add_field(
                name=f"Intel #{i}",
                value=f"```{article['title']}```\n[Read more]({article['url']})",
                inline=False
            )
            
        await ctx.send(embed=intel_report)
    except Exception as e:
        await ctx.send("❗ Intel retrieval failed")

@bot.command(name='alert')
@commands.has_permissions(administrator=True)
async def alert(ctx, *, message):
    """Send an alert in MGS style"""
    alert_msg = f"""
```
!!!!!!!!! ALERT !!!!!!!!!!

{message}

########################
```
"""
    await ctx.send(alert_msg)

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 3):
    """Clear messages in any channel
    
    Args:
        ctx: The context in which the command was called
        amount: The number of messages to clear (default: 10)
    """
    try:
        deleted = await ctx.channel.purge(limit=amount)
        confirmation = await ctx.send(f"🧹 Cleared {len(deleted)} messages in {ctx.channel.mention}")
        # Delete the confirmation message after 5 seconds
        await confirmation.delete(delay=5)
    except Exception as e:
        error_msg = await ctx.send(f"❌ An error occurred while clearing messages: {str(e)}")
        await error_msg.delete(delay=5)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❗ You don't have the security clearance for this operation!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❓ Unknown codec frequency")
    else:
        await ctx.send("❗ An error occurred.")

# Keep the existing moderation commands but add MGS theming
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"🚨 {member.name} has been extracted from Mother Base!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"⚠ {member.name} has been marked as an enemy combatant and eliminated!")

    

# Run the bot
def main():
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"Mission failed! Error: {e}")

if __name__ == "__main__":
    main()
