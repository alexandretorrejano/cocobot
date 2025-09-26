import discord
import os
import random
import asyncio
import traceback
import time
import json
import pandas as pd
from discord.ext import commands
from mutagen.mp3 import MP3
from util_functions import *
import sys
from dotenv import load_dotenv
from utils import *

# Redirect stdout and stderr to a file
log_file = "logs/random_log.txt"
sys.stdout = open(log_file, "w", buffering=1)  # Line buffering for real-time output
sys.stderr = sys.stdout  # Redirect errors to the same file
load_dotenv()

print("> Logging started...")  # This will be written to the log file

print('> Random Trigger Started!')

sound_folder=os.getenv("sound_folder","sounds")
min_interval_seconds=int(os.getenv("min_interval_seconds",10))
max_interval_seconds=int(os.getenv("max_interval_seconds",3600))
volume_level=os.getenv("volume_level",0.5)
extra_channel_time_seconds=int(os.getenv("extra_channel_time_seconds",1))
token=os.getenv("token_random")




intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_path = 'ffmpeg/bin/ffmpeg.exe'


@bot.event
async def on_ready():
    print(f'> Logged in as {bot.user.name}')

    # Start the interval task
    bot.loop.create_task(interval_task())




async def interval_task():
    # Loop through all guilds and their voice channels
    voice_channel_list=[]
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            voice_channel_list.append(vc)

    while True:
        try:
            interval = random.randint(min_interval_seconds, max_interval_seconds)
            print("> Waiting for a random time")
            await asyncio.sleep(interval)
            print(f'> Interval: {interval} seconds')

            # 🔹 For now: just target one channel name like before
            target_channel = voice_channel_list[0]
            selected_sound_files=sound_files

            # 🔹 Iterate over ALL voice channels each cycle
            for target_channel in voice_channel_list:
                await play_in_channel(target_channel, selected_sound_files, volume_level,extra_channel_time_seconds,ffmpeg_path)

        except Exception:
            traceback.print_exc()
            await asyncio.sleep(60)


@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

# Path to the sound folder
sound_folder = r"sounds"

# Build the file tree and convert it to tree_select nodes
file_tree = build_file_tree(sound_folder)
nodes = tree_to_treeselect(file_tree)
# Iterate through the dictionary
rows = []
for Folder, inner_dict in file_tree.items():
    for File, value in inner_dict.items():
        rows.append([Folder, File])

# Create a DataFrame
df_files = pd.DataFrame(rows, columns=['Folder', 'File'])
df_files['Path'] = df_files['Folder'] + '/' + df_files['File']
sound_files=df_files['Path'].tolist()
sound_files=['sounds/'+s for s in sound_files]

bot.run(token)
