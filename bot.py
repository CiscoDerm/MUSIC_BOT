# Bot Discord Musique avec commandes slash
# Utilise discord.py, yt_dlp et PyNaCl

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp as youtube_dl
import os

# Configuration yt_dlp
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
    # 'source_address': '0.0.0.0'  # Enlever si problèmes TLS
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.thumbnail = data.get('thumbnail')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.queue = {}
        self.current_songs = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("Commandes slash synchronisées!")

bot = MusicBot()

@bot.event
async def on_ready():
    print(f'{bot.user} est connecté!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/play"))

async def play_next(interaction):
    guild_id = interaction.guild_id
    if guild_id in bot.queue and bot.queue[guild_id]:
        url, requester_id = bot.queue[guild_id].pop(0)
        await play_song(interaction, url, requester_id)
    else:
        bot.current_songs.pop(guild_id, None)

async def play_song(interaction, url, requester_id=None):
    guild_id = interaction.guild_id
    voice_client = interaction.guild.voice_client
    if not voice_client:
        return
    try:
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=False)

        bot.current_songs[guild_id] = {
            'title': player.title,
            'url': url,
            'thumbnail': player.thumbnail,
            'requester_id': requester_id,
            'duration': player.duration,
            'uploader': player.uploader
        }

        def after_playing(e):
            if not e and not player.url.startswith("http"):
                try:
                    os.remove(player.source.filename)
                except: pass
            asyncio.run_coroutine_threadsafe(play_next(interaction), bot.loop)

        voice_client.play(player, after=after_playing)

        embed = discord.Embed(title="🎵 En train de jouer", description=f"**{player.title}**", color=discord.Color.green())
        if player.thumbnail:
            embed.set_thumbnail(url=player.thumbnail)
        if requester_id:
            embed.set_footer(text=f"Demandé par {interaction.guild.get_member(requester_id).display_name}")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Erreur de lecture: {e}")
        await interaction.followup.send(f"Erreur: {e}")

@bot.tree.command(name="join", description="Connecte le bot à votre canal vocal")
async def join(interaction: discord.Interaction):
    await interaction.response.defer()
    if not interaction.user.voice:
        return await interaction.followup.send("Vous n'êtes pas dans un canal vocal!", ephemeral=True)
    channel = interaction.user.voice.channel
    if not interaction.guild.voice_client:
        await channel.connect()
    else:
        await interaction.guild.voice_client.move_to(channel)
    await interaction.followup.send(embed=discord.Embed(title="Connecté", description=f"Dans **{channel.name}**", color=discord.Color.blue()))

@bot.tree.command(name="leave", description="Déconnecte le bot")
async def leave(interaction: discord.Interaction):
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        bot.queue.pop(interaction.guild_id, None)
        bot.current_songs.pop(interaction.guild_id, None)
        await interaction.followup.send("Déconnecté!")
    else:
        await interaction.followup.send("Pas connecté à un canal vocal.", ephemeral=True)

@bot.tree.command(name="play", description="Joue une chanson depuis YouTube")
@app_commands.describe(url="URL ou titre de la chanson")
async def play(interaction: discord.Interaction, url: str):
    await interaction.response.defer()
    guild_id = interaction.guild_id
    if not interaction.user.voice:
        return await interaction.followup.send("Vous devez être dans un canal vocal!", ephemeral=True)
    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()
    if guild_id not in bot.queue:
        bot.queue[guild_id] = []
    if guild_id not in bot.current_songs or not interaction.guild.voice_client.is_playing():
        await play_song(interaction, url, interaction.user.id)
    else:
        bot.queue[guild_id].append((url, interaction.user.id))
        await interaction.followup.send("Ajouté à la file d'attente!")

@bot.tree.command(name="skip", description="Passe à la chanson suivante")
async def skip(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()
        await interaction.followup.send("⏭️ Chanson suivante!")
    else:
        await interaction.followup.send("Aucune chanson en cours.", ephemeral=True)

@bot.tree.command(name="stop", description="Arrête et vide la file")
async def stop(interaction: discord.Interaction):
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if vc:
        vc.stop()
        bot.queue.pop(interaction.guild_id, None)
        bot.current_songs.pop(interaction.guild_id, None)
        await interaction.followup.send("⏹️ Lecture arrêtée.")
    else:
        await interaction.followup.send("Aucune lecture en cours.", ephemeral=True)

@bot.tree.command(name="pause", description="Met en pause la lecture")
async def pause(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause()
        await interaction.followup.send("⏸️ Lecture en pause.")
    else:
        await interaction.followup.send("Rien à mettre en pause.", ephemeral=True)

@bot.tree.command(name="resume", description="Reprend la lecture")
async def resume(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume()
        await interaction.followup.send("▶️ Lecture reprise.")
    else:
        await interaction.followup.send("Aucune lecture à reprendre.", ephemeral=True)

@bot.tree.command(name="now", description="Affiche la chanson en cours")
async def now(interaction: discord.Interaction):
    await interaction.response.defer()
    song = bot.current_songs.get(interaction.guild_id)
    if not song:
        return await interaction.followup.send("Aucune chanson en cours.", ephemeral=True)
    embed = discord.Embed(title="🎵 En cours de lecture", description=f"**{song['title']}**", color=discord.Color.green())
    if song['thumbnail']:
        embed.set_thumbnail(url=song['thumbnail'])
    if song['uploader']:
        embed.add_field(name="Uploader", value=song['uploader'], inline=True)
    if song['duration']:
        m, s = divmod(song['duration'], 60)
        embed.add_field(name="Durée", value=f"{m}:{s:02d}", inline=True)
    if song['requester_id']:
        user = interaction.guild.get_member(song['requester_id'])
        if user:
            embed.set_footer(text=f"Demandé par {user.display_name}")
    await interaction.followup.send(embed=embed)

TOKEN = 'VOTRE_TOKEN_DISCORD_ICI'
if TOKEN and TOKEN != 'VOTRE_TOKEN_DISCORD_ICI':
    bot.run(TOKEN)
else:
    print("Erreur: Veuillez définir votre token Discord.")
