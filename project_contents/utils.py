import random
from mutagen.mp3 import MP3
import discord
import asyncio

def get_clip_length(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        print(f"> Error while getting clip length: {str(e)}")
        return 0.0

async def play_in_channel(target_channel,selected_sound_files,volume_level,extra_channel_time_seconds,ffmpeg_path):
    
    if not target_channel.members:
        return  # skip empty channels

    # Get common roles across all members
    common_roles = set(role.name for role in target_channel.members[0].roles)
    for member in target_channel.members[1:]:
        member_roles = set(role.name for role in member.roles)
        common_roles &= member_roles

    # Filter sounds by common roles
    filtered_sound_files = [
        f for f in selected_sound_files if f.split('/')[1] in common_roles
    ]

    if not filtered_sound_files:
        print(f"> No matching sounds for {target_channel.name}, skipping...")
        return

    voice_client = None
    member_list=target_channel.members
    for member in member_list:
        if member.voice:
            try:
                voice_client = await member.voice.channel.connect()
            except Exception as e:
                print(f"> Could not connect to {target_channel.name}: {e}")
            break

    if voice_client:
        print(f'> Joined voice channel: {target_channel.name}')

        sound_file = random.choice(filtered_sound_files)
        sound_path = sound_file

        clip_length = get_clip_length(sound_path)
        print(f'> Playing sound: \n> {sound_file.rsplit("/", 1)[-1]}')
        print(f'> Duration: {clip_length:.2f} seconds')
        print(f"> Present members:\n> {', '.join([m.name for m in member_list])}")

        voice_client.stop()

        volume_filter = f"volume={volume_level}"
        audio_source = discord.FFmpegPCMAudio(
            executable=ffmpeg_path,
            source=sound_path,
            options=f"-af {volume_filter}"
        )
        voice_client.play(audio_source)

        await asyncio.sleep(clip_length + extra_channel_time_seconds)

        await voice_client.disconnect()
        print(f'> Left voice channel: {target_channel.name}')