#python -u "c:\Users\Owner\Desktop\TierListBot\TierListBot\bot.py"
import asyncio
import shutil
import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from unicodedata import lookup
from requests import get
import requests
from tinydb import TinyDB, Query, where
from discord.ui import Select, View
import datetime
# from pytube import Search
from pytube import Search
from util import *
import re
from discord.ext.commands import cooldown, BucketType
import pafy
from debug import debug

load_dotenv()
TOKEN = os.getenv('TOKEN')
MAXVIDEOLENGTH = 3600
bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())
myID = 281911981089226762


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="Tissi Coding"))
    await bot.change_presence(status=discord.Status.dnd,activity=discord.CustomActivity(name='david sucks ass' ,emoji='🖥️'))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
        
# @bot.event
# async def on_voice_state_update(member, before, after):
#     if member==bot.user:
#         print("Bot has been Moved")
#         voice = discord.utils.get(bot.voice_clients, guild=member.guild)
#         if after is None:
#             queue = TinyDB('queue.json')
#             queue.update({'queue': []}, where('server') == member.guild.id)
#             voice.stop()

@bot.tree.error
async def on_app_command_error(interacton:discord.Interaction, error:app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interacton.response.send_message(f"This command is on cooldown, please retry in {round(error.retry_after, 2)} seconds. (when this message goes away)", ephemeral = True, delete_after=error.retry_after)
    else: raise error
        
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
async def say(interaction: discord.Interaction, thing_to_say: str, secret: bool = True):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not secret:
        await interaction.response.send_message(f"{interaction.user.mention} said: {thing_to_say}", ephemeral = True, delete_after=5)
    else:
        await interaction.channel.send(f"{thing_to_say}")
    
@bot.tree.command(name = "tierlist", description='Starts voting for the Teir List')
@app_commands.describe(timer = "is this timed? (true: timer, false: command to end)")
@app_commands.describe(voting_time_seconds = "How long are we waiting for votes to come in? (seconds)")
async def tierlist(interaction: discord.Interaction, timer: bool = False, voting_time_seconds: int = 5):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not (interaction.user.guild_permissions.administrator or interaction.user.id == myID):
        await interaction.response.send_message(f"You don't have permission to do that {interaction.user.mention}", ephemeral = True, delete_after=5)
        return
    db = TinyDB('db.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    if len(res) >= 1:
        await interaction.response.send_message(f"already one tierlist ongoing, try /endtierlist", ephemeral = True, delete_after=7)
        return
    
    await interaction.response.send_message(f"kys!!!!", ephemeral = True, delete_after=3)
    
    if not timer: db.insert({'channel': interaction.channel.id, 'vote_msg_list': interaction.channel.id, 'memberids': interaction.channel.id})
    
    members = [x for x in interaction.channel.members if (not x.bot and x.id != 704872368572465163) or x.id == 1186185707258134560]
    vote_msg_list = []
    await interaction.channel.send('@everyone starting tierlist')
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
        return
        
@bot.tree.command(name = "endtierlist", description='ends voting for the Teir List')
async def endtierlist(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not (interaction.user.guild_permissions.administrator or interaction.user.id == myID):
        await interaction.response.send_message(f"You don't have permission to do that {interaction.message.author.mention}", ephemeral = True, delete_after=5)
        return
    db = TinyDB('db.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    
    if len(res) == 0 or (res[0]['channel'] == res[0]['vote_msg_list'] and res[0]['channel'] == res[0]['memberids']):
        await interaction.response.send_message(f"no tierlist to end, try /tierlist", ephemeral = True, delete_after=7)
        return
    
    await interaction.response.send_message(f"KYS!!!!", ephemeral = True, delete_after=3)
    
    res = res[0]
    vote_msg_list = res['vote_msg_list']
    memberids = [await bot.fetch_user(x) for x in res['memberids']]
    await createlist(interaction.channel, vote_msg_list, memberids)
    # Remove the query from the database
    db.remove(User.channel == interaction.channel.id)

@bot.tree.command(name = "play", description='plays music?')
@app_commands.describe(query = "looks up the song")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id))
async def play(interaction: discord.Interaction, query: str):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
    
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild) # This allows for more functionality with voice channels
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    if len(res) == 0:
        queue.insert({'server': interaction.guild.id, 'queue': []})
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
        
    if (os.path.exists(f'vids/{interaction.guild.id}.webm') or os.path.exists(f'vids/{interaction.guild.id}_queue') or len(res[0]['queue']) >=1) and voice is None:
        if (os.path.exists(f'vids/{interaction.guild.id}.webm')): os.remove(f'vids/{interaction.guild.id}.webm')
        if (os.path.exists(f'vids/{interaction.guild.id}_queue')): shutil.rmtree(f'vids/{interaction.guild.id}_queue')
        queue.update({'queue': []}, where('server') == interaction.guild.id)
    
    uservoice = interaction.user.voice
    if uservoice is None:
        await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True, delete_after=5)
        return
    if "https://www.youtube.com/" in query or "https://youtube.com/" in query:
        video_id = re.search(r'(?<=watch\?v=)(.*?)(?=&|$)', query)
        checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
        video_url = checker_url + (str(video_id.group(0)) if video_id is not None else "0")
        if video_id and requests.get(video_url).status_code == 200:
            query = f'https://www.youtube.com/watch?v={str(video_id.group(0))}'
            videoObj = Search(query).results[0]
            
            if videoObj.length is None or videoObj.vidlength is None or videoObj.length_seconds is None:
                await interaction.response.send_message(f'You can not play live videos on the bot, Try Again', ephemeral=True, delete_after=7)
                return
            if videoObj.length_seconds > MAXVIDEOLENGTH:
                await interaction.response.send_message(f"Video is too long, go fuck yourself.", ephemeral = True, delete_after=7)
                return
            output = addtoQueue(interaction,videoObj)
            if voice is None:
                await interaction.response.send_message(f"playing", ephemeral = True, delete_after=3)
                await downloadAndPlay(interaction,output,query,uservoice)
            else:
                await interaction.response.send_message(f"adding to Queue", ephemeral = True, delete_after=3)
                await download(output,query)
        else:
            await interaction.response.send_message(f"invalid youtube link", ephemeral = True, delete_after=5)
        return
    
    s = Search(query)
    if (len(s.results) == 0):
        await interaction.response.send_message(f"no results found", ephemeral = True, delete_after=5)
        return
    
    await interaction.response.send_message(f"Searching!", ephemeral = True, delete_after=3)
    # - {v.length} - {v.viewCountText}
    selectionmessage = [f" {k+1} : {v.title}\n" if k!=9 else f"{k+1} : {v.title}\n" for k,v in enumerate(s.results[0:10])]
    # print(s.results[0].views)
    # print(s.results[0].length)
    # debug(youtubeobj,"youtubeobj.json")
    # video = pafy.new(s.results[0].watch_url)
    # video.viewcount
    # video.duration
    #work on this, gn
    select = Select(options = [discord.SelectOption(label = f'{k+1} : {v.title}'[:99] if len(f'{k+1}: {v.title}') > 99 else f'{k+1} : {v.title}', description = f'{v.length} - {v.viewCountText}', value=k) for k,v in enumerate(s.results[0:10])])
    
    async def my_mycallback(ints:Interaction[Client]):
        if ints.user.id != interaction.user.id: 
            await ints.response.send_message(f"You cant select this video, you did not search it", ephemeral = True, delete_after=7)
            return
        videoObj = s.results[int(select.values[0])]
        if videoObj.length is None or videoObj.vidlength is None or videoObj.length_seconds is None:
            await ints.response.send_message(f'You can not play live videos on the bot, Try Again', ephemeral=True, delete_after=7)
            return
        if videoObj.length_seconds > MAXVIDEOLENGTH:
            await ints.response.send_message(f"Video is too long, go fuck yourself.", ephemeral = True, delete_after=7)
            return
        await newint.delete()
        
        videourl = videoObj.watch_url
        output=addtoQueue(interaction,videoObj)
        #runqueue instead
        if voice is None:
            # await interaction.response.send_message(f"playing", ephemeral = True, delete_after=3)
            await downloadAndPlay(interaction,output,videourl,uservoice)
        else:
            # await interaction.response.send_message(f"adding to Queue", ephemeral = True, delete_after=3)
            await download(output,videourl)
    
    select.callback = my_mycallback
    view = View()
    view.add_item(select)
    # davidsid = 382271649724104705
    #if interaction.user.id != davidsid else f'{interaction.user.mention} Searched: "gay furry porn"\n'
    searchstring = f'{interaction.user.mention} Searched: "*{query}*"\n' 
    newint = await interaction.channel.send(f'{searchstring}```'+''.join(map(str, selectionmessage))+'```',view=view)

# @bot.tree.command(name = "stop", description='stops music?')
# async def stop(interaction: discord.Interaction):
#     print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick if interaction.user.nick is not None else interaction.user.global_name} in {interaction.guild.name} - {interaction.channel.name}')
#     voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild) # This allows for more functionality with voice channels
#     if voice is None:
#         await interaction.response.send_message(f"not playing anything in this server", ephemeral = True, delete_after=5)
#     else:
#         await interaction.response.send_message(f"Stopping!", ephemeral = True, delete_after=3)
#         voice.stop()
#         # await voice.disconnect(force = True)
#         # try:
#         #     os.remove(f"vids/{interaction.guild.id}.webm")
#         # except:
#         #     pass
        
bot.run(TOKEN)