import discord
import os
import random
import asyncio
import traceback
import sys  # Import the sys module
import subprocess
import json
from discord.ext import commands
from mutagen.mp3 import MP3
from dotenv import load_dotenv

# Get the directory where the main script is located
script_directory = os.path.dirname(os.path.abspath(__file__))
# Set the current working directory to the script's directory
os.chdir(script_directory)
load_dotenv()


# Open a file to store the output
log_file = open('logs/manual_log.txt', 'w')

# Redirect stdout to the file
sys.stdout = log_file

# Redirect stderr to the file (optional)
sys.stderr = log_file

sound_folder=os.getenv("sound_folder","sounds")
volume_level=os.getenv("volume_level",0.5)
target_channel_name=os.getenv("target_channel_name","")
extra_channel_time_seconds=int(os.getenv("extra_channel_time_seconds",1))
token=os.getenv("token_manual")


# Get the JSON string passed from the main script
selected_paths_str = sys.argv[1]  # Access the passed JSON string argument

# Convert the JSON string back into a Python list of strings
selected_paths = json.loads(selected_paths_str)

print(selected_paths)
# Global parameters




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
    await join_channel()


async def join_channel():
        try:
                  
            target_channel = discord.utils.get(bot.get_all_channels(), name=target_channel_name, type=discord.ChannelType.voice)

            if target_channel:
                voice_client = None

                for member in target_channel.members:
                    if member.voice:
                        voice_client = await member.voice.channel.connect()
                        break

                if voice_client:
                    print(f'Joining voice channel: {target_channel_name}')

                    sound_file = random.choice(sound_files)
                    sound_path = os.path.join('sounds', sound_file)

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
                    sys.exit(0)
        except Exception as e:
            traceback.print_exc()
            await asyncio.sleep(60)

@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()

# List all sound files in the folder
sound_files = selected_paths
bot.run(token)


# Close the file when you're done
log_file.close()

# Reset stdout and stderr to their default behavior (optional)
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__