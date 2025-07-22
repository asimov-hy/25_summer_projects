import discord
from discord.ext import commands

import json
import os


# REDACTED + 채널 개인정보
TOKEN = 'REDACTED'   # Replace
USER_ID = REDACTED       # The user you want to watch
GAME_NAME = "REDACTED"    # Exact name as shown in Discord
CHANNEL_ID = REDACTED    # The channel to send alerts


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True  # Needed for commands

bot = commands.Bot(command_prefix='!', intents=intents)

# --- PERSISTENT COUNTER ---
DATA_FILE = "player_stats.json"

def load_play_count():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return data.get("play_count", 0)
    return 0

def save_play_count(count):
    with open(DATA_FILE, "w") as f:
        json.dump({"play_count": count}, f)






# --- GLOBAL STATE ---
user_playing = False
play_count = load_play_count()

@bot.event
async def on_ready():
    global user_playing, play_count

    print(f'봇 활성화!')

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("👀REDACTED를 감시 중!👀\n")

    # Check if the target user is already playing
    for guild in bot.guilds:
        member = guild.get_member(USER_ID)
        if member:
            activities = [a.name for a in member.activities if isinstance(a, discord.Activity)]
            if any(GAME_NAME in name for name in activities):
                user_playing = True
                play_count += 1
                save_play_count(play_count)
                await channel.send(f"\n{member.display_name}는 이미 {GAME_NAME} 문명을 하고 있습니다.")
                await channel.send(f"축적 비용: {play_count * 10}만원 입니다.")
            else:
                user_playing = False
                await channel.send("REDACTED아 문명하자...\n")
            break

@bot.event
async def on_presence_update(before, after):
    global user_playing, play_count

    if after.id != USER_ID:
        return

    activities = [a.name for a in after.activities if isinstance(a, discord.Activity)]
    is_playing = any(GAME_NAME in name for name in activities)

    channel = bot.get_channel(CHANNEL_ID)

    if is_playing and not user_playing:
        play_count += 1
        save_play_count(play_count)
        await channel.send(f"\n{after.display_name}가 문명하기 시작했습니다.")
        await channel.send(f"축적 비용: {play_count * 10}만원 입니다.")
        user_playing = True

    elif not is_playing and user_playing:
        await channel.send(f"\n{after.display_name}는 문명을 잠깐 쉬기로 했습니다.")
        await channel.send(f"(ㄲㅂ...)")
        user_playing = False

# --- COMMANDS ---

@bot.command(name='report')
async def report(ctx):
    guild = ctx.guild
    member = guild.get_member(USER_ID)

    status = f"📊 **{member.display_name} 부채 보고서**\n"

    # Online status
    if member.status == discord.Status.offline:
        status += "• **Status:** Offline\n"
    else:
        status += f"• **Status:** {member.status}\n"

    # Game status
    activities = [a.name for a in member.activities if isinstance(a, discord.Activity)]
    print("Current activities:", activities)

    if any(GAME_NAME in name for name in activities):
        status += f"• **빛쌓는 중? :** YES 🎮\n"
    else:
        status += f"• **빛쌓는 중? :** NO 💤\n"

    status += f"• **총 부채:** {play_count * 10}만원 💰\n"

    await ctx.send(status)

bot.run(TOKEN)
