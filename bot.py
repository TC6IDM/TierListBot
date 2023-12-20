import asyncio
import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from unicodedata import lookup
from discord import File
from requests import get
from tinydb import TinyDB, Query, where
from discord.ui import Select, View
import time
import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from pytube import Search
import yt_dlp
from util import createlist

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
myID = 281911981089226762

def my_hook(d):
    if d['status'] == 'finished':
        # print(d['filepath'])
        print('Done downloading, now post-processing ...')

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        
COOKIE_FILE = 'www.youtube.com_cookies.txt'

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# @bot.event
# async def on_voice_state_update(member, before, after):
#     if after.channel is None and member==bot.user:
#         print("Bot has been Disconnected")
#         await os.remove("vids/music.mp3")
        
@bot.tree.command(name = "ping", description='Returns latency')
async def ping(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms", ephemeral = True)

@bot.tree.command(name = "hello", description='Says hello')
async def hello(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral = True)

@bot.tree.command(name = "say", description='Repeats what you say')
@app_commands.describe(thing_to_say = "what should i say")
@app_commands.describe(secret = "is this a secret?")
async def say(interaction: discord.Interaction, thing_to_say: str, secret: bool = False):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    await interaction.response.send_message(f"{interaction.user.mention} said: {thing_to_say}" if not secret else f"{thing_to_say}")
    
@bot.tree.command(name = "tierlist", description='Starts voting for the Teir List')
@app_commands.describe(timer = "is this timed? (true: timer, false: command to end)")
@app_commands.describe(voting_time_seconds = "How long are we waiting for votes to come in? (seconds)")
async def tierlist(interaction: discord.Interaction, timer: bool = False, voting_time_seconds: int = 5):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not (interaction.message.author.guild_permissions.administrator or interaction.message.author.id == myID):
        await interaction.response.send_message(f"You don't have permission to do that {interaction.user.mention}", ephemeral = True)
        return
    db = TinyDB('db.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    if len(res) >= 1:
        await interaction.response.send_message(f"already one tierlist ongoing", ephemeral = True)
        return
    
    await interaction.response.send_message(f"kys!!!!", ephemeral = True)
    
    if not timer: db.insert({'channel': interaction.channel.id, 'vote_msg_list': interaction.channel.id, 'memberids': interaction.channel.id})
    
    members = [x for x in interaction.channel.members if not x.bot]
    vote_msg_list = []
    for member in members:
        vote_msg = await interaction.channel.send(f'Where should {member.global_name if member.global_name is not None else member.name} be placed?')
        await vote_msg.add_reaction('🆘')
        vote_msg.id
        indicators = ["s", "a", "b", "c", "d", "e", "f"]
        for i in indicators:
            await vote_msg.add_reaction(lookup("REGIONAL INDICATOR SYMBOL LETTER %s" % i))
        
        vote_msg_list.append(vote_msg.id)
    
    if timer:        
        presentDate = datetime.datetime.now()
        unix_timestamp = datetime.datetime.timestamp(presentDate) + voting_time_seconds
        await interaction.channel.send(f'ending <t:{round(unix_timestamp)}:R>')
        #timer needed
        await asyncio.sleep(voting_time_seconds)
        await createlist(interaction.channel, vote_msg_list, members) 
    else:
        memberids = [x.id for x in members]
        db.update_multiple([
            ({'vote_msg_list': vote_msg_list}, where('channel') == interaction.channel.id),
            ({'memberids': memberids}, where('channel') == interaction.channel.id),
            ])
        # db.update(set('vote_msg_list',vote_msg_list), User.channel == interaction.channel.id)
        # db.update(set('memberids',memberids), User.channel == interaction.channel.id)
        # db.insert({'channel': interaction.channel.id, 'vote_msg_list': vote_msg_list, 'memberids': memberids})
        return
        
@bot.tree.command(name = "endtierlist", description='ends voting for the Teir List')
async def endtierlist(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not (interaction.message.author.guild_permissions.administrator or interaction.message.author.id == myID):
        await interaction.response.send_message(f"You don't have permission to do that {interaction.message.author.mention}", ephemeral = True)
        return
    db = TinyDB('db.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    
    if len(res) == 0 or (res[0]['channel'] == res[0]['vote_msg_list'] and res[0]['channel'] == res[0]['memberids']):
        await interaction.response.send_message(f"no tierlist to end", ephemeral = True)
        return
    
    await interaction.response.send_message(f"KYS!!!!", ephemeral = True)
    
    res = res[0]
    vote_msg_list = res['vote_msg_list']
    memberids = [await bot.fetch_user(x) for x in res['memberids']]
    await createlist(interaction.channel, vote_msg_list, memberids)
    
    # Remove the query from the database
    db.remove(User.channel == interaction.channel.id)

@bot.tree.command(name = "play", description='plays music?')
@app_commands.describe(query = "looks up the song")
async def play(interaction: discord.Interaction, query: str):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if os.path.exists(f'vids/{interaction.guild.id}.mp3'):
        voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild) # This allows for more functionality with voice channels
        if voice is None:
            os.remove(f'vids/{interaction.guild.id}.mp3')
        else:
            await interaction.response.send_message(f"https://tenor.com/view/ltg-low-tier-god-yskysn-ltg-thunder-thunder-gif-23523876", ephemeral = True)
            return
    uservoice = interaction.user.voice
    if uservoice is None:
        await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True)
        return
    await interaction.response.send_message(f"Searching!", ephemeral = True)
    s = Search(query)
    # strcat = ""
    selectionmessage = [f"{k+1} : {v.title}\n" for k,v in enumerate(s.results[0:10])]
    #[discord.SelectOption(label = f'{k+1} - {v.title}', description= f"length {v.length}") for k,v in enumerate(s.results[0:10])]
    select = Select(options = [discord.SelectOption(label = f'{k+1}: {v.title}'[:99] if len(f'{k+1} - {v.title}') > 99 else f'{k+1} - {v.title}', description = f"{v.watch_url}", value=k) for k,v in enumerate(s.results[0:10])])
    
    async def my_mycallback(ints):
        # print(ints)
        await newint.delete()
        videourl = s.results[int(select.values[0])].watch_url
        await interaction.channel.send(f"Playing {videourl}")
        ydl_opts = {
            'format': 'mp3/bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',#highest quality
            },{
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }],
            'ignoreerrors': True, #ignore errors
            # 'outtmpl': '/vids/(%(video_autonumber)s) %(uploader)s - %(title)s.%(ext)s', #save songs here .%(ext)s
            'outtmpl': '/vids/'+str(interaction.guild.id)+'.%(ext)s', #save songs here .%(ext)s

            # 'outtmpl': dir_path2+"("+getzeros(int('%(video_autonumber)s'),int('%(playlist_count)s'))+') '+ removePunctuation("%(uploader)s")+ ' - ' +removePunctuation("%(title)s") +'.%(ext)s', #save songs here .%(ext)s
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'cookiefile': COOKIE_FILE, #cookies for downloading age restricted videos
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(videourl)
        
        # create StreamPlayer
        if uservoice.channel is None:
            await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True)
            return
        vc = await uservoice.channel.connect()
        while not os.path.exists(f'vids/{interaction.guild.id}.mp3'):
            await asyncio.sleep(1)
        
        vc.play(discord.FFmpegPCMAudio(f'vids/{interaction.guild.id}.mp3'), after=lambda e: print('done', e))
        # player = vc.create_ffmpeg_player('vuvuzela.mp3', after=lambda: print('done'))
        # print(vc.is_playing())
        while vc.is_playing():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        vc.stop()
        await vc.disconnect()
        os.remove(f'vids/{interaction.guild.id}.mp3')
        
        # await interaction.channel.send(s.results[ints[0]].watch_url)
    
    select.callback = my_mycallback
    view = View()
    view.add_item(select)
    newint = await interaction.channel.send(f'```'+''.join(map(str, selectionmessage))+'```',view=view)
    try:
        newint.respond()
    except:
        pass
    # for r in numbers.keys():
    #     await interactionmessage.add_reaction(r)

@bot.tree.command(name = "stop", description='stops music?')
async def stop(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild) # This allows for more functionality with voice channels
    if voice is None:
        await interaction.response.send_message(f"not playing anything in this server", ephemeral = True)
    else:
        await interaction.response.send_message(f"Stopping!", ephemeral = True)
        voice.stop()
        await voice.disconnect()
        try:
            os.remove(f"vids/{interaction.guild.id}.mp3")
        except:
            pass
        
        
    
bot.run(TOKEN)