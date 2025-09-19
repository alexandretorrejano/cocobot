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

# Redirect stdout and stderr to a file
log_file = "logs/random_log.txt"
sys.stdout = open(log_file, "w", buffering=1)  # Line buffering for real-time output
sys.stderr = sys.stdout  # Redirect errors to the same file
load_dotenv()

print("Logging started...")  # This will be written to the log file

print('Random Trigger Started!')

sound_folder=os.getenv("sound_folder","sounds")
min_interval_seconds=int(os.getenv("min_interval_seconds",10))
max_interval_seconds=int(os.getenv("max_interval_seconds",3600))
volume_level=os.getenv("volume_level",0.5)
target_channel_name=os.getenv("target_channel_name","")
extra_channel_time_seconds=int(os.getenv("extra_channel_time_seconds",1))
token=os.getenv("token_random")




intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_path = 'ffmpeg/bin/ffmpeg.exe'

def get_clip_length(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"Error while getting clip length: {str(e)}")
        return 0.0
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(interval_task())  # Start the interval task


async def interval_task():
    while True:
        try:
            interval = random.randint(min_interval_seconds, max_interval_seconds)
            
            print(f'Waiting for a random time')

            await asyncio.sleep(interval)
            
            print(f'Interval: {interval} seconds')


            target_channel = discord.utils.get(bot.get_all_channels(), name=target_channel_name, type=discord.ChannelType.voice)
            if target_channel and target_channel.members:
                voice_client = None

                # Start with the role set of the first member
                common_roles = set(role.name for role in target_channel.members[0].roles)

                # Intersect with the roles of every other member
                for member in target_channel.members[1:]:
                    member_roles = set(role.name for role in member.roles)
                    common_roles &= member_roles

                filtered_sound_files = [f for f in sound_files if f.split('/')[1] in common_roles]

                # print(f"common_roles: {common_roles}")
                # print(f"sound_files: {sound_files}")
                # print(f"filtered_sound_files: {filtered_sound_files}")

                for member in target_channel.members:
                    if member.voice and len(filtered_sound_files)>0:
                        try:
                            voice_client = await member.voice.channel.connect()
                        except IndexError:
                            print("Discord did not return any encryption modes. Skipping this attempt.")
                        break

              
                if voice_client:
                    print(f'Joining voice channel: {target_channel_name}')

                    sound_file = random.choice(filtered_sound_files)
                    sound_path = sound_file

                    clip_length = get_clip_length(sound_path)
                    print(f'Playing sound: {sound_file} (Duration: {clip_length:.2f} seconds)')

                    voice_client.stop()

                    # Adjust the volume using the 'volume' filter
                    volume_filter = f"volume={volume_level}"
                    audio_source = discord.FFmpegPCMAudio(executable=ffmpeg_path, source=sound_path, options=f"-af {volume_filter}")
                    voice_client.play(audio_source)

                    await asyncio.sleep(clip_length + extra_channel_time_seconds)

                    await voice_client.disconnect()
                    print('Left voice channel')
        except Exception as e:
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
