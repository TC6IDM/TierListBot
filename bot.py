#python -u "c:\Users\Owner\Desktop\TierListBot\TierListBot\bot.py"
#Getting rate limited by youtube? refresh cookie file
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
from YoutubeSearchCustom import YoutubeSearchCustom
from createQueueEmbed import createQueueEmbed
# from pytube import Search
from pytube import Search
from pytube.contrib.playlist import Playlist
from tierlistUtil import createlist
from songUtil import *
from buttonviews import deleteView, queueView
import re
from discord.ext.commands import cooldown, BucketType
import pafy
from debug import debug
from ytmusicapi import YTMusic

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
        try:
            await interacton.response.send_message(f"This command is on cooldown, please retry in {round(error.retry_after, 2)} seconds. (when this message goes away)", ephemeral = True, delete_after=error.retry_after)
        except:
            pass
    else: raise error
        
@bot.tree.command(name = "ping", description='Returns latency')
async def ping(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
    try:
        await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms", ephemeral = True)
    except:
        pass
@bot.tree.command(name = "hello", description='Says hello')
async def hello(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
    try:
        await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral = True)
    except:
        pass
@bot.tree.command(name = "say", description='Repeats what you say')
@app_commands.describe(thing_to_say = "what should i say")
@app_commands.describe(secret = "is this a secret?")
async def say(interaction: discord.Interaction, thing_to_say: str, secret: bool = True):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}\nthing_to_say: {thing_to_say} - secret: {secret}')
    if not secret:
        try:
            await interaction.response.send_message(f"{interaction.user.mention} said: {thing_to_say}", ephemeral = True, delete_after=5)
        except:
            pass
    else:
        try:
            await interaction.response.send_message(f"ok", ephemeral = True, delete_after=0)
        except:
            pass
        await interaction.channel.send(f"{thing_to_say}")

@bot.tree.command(name = "tierlist", description='Starts voting for the Teir List')
@app_commands.describe(timer = "is this timed? (true: timer, false: type command to end)")
@app_commands.describe(voting_time_seconds = "How long are we waiting for votes to come in? (seconds)")
async def tierlist(interaction: discord.Interaction, timer: bool = False, voting_time_seconds: int = 5):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}\ntimer: {timer} - voting_time_seconds: {voting_time_seconds}')
    if not (interaction.user.guild_permissions.administrator or interaction.user.id == myID):
        try:
            await interaction.response.send_message(f"You don't have permission to do that {interaction.user.mention}", ephemeral = True, delete_after=5)
        except:
            pass
        return
    
    db = TinyDB('databases/tierlist.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    if len(res) >= 1:
        try:
            await interaction.response.send_message(f"already one tierlist ongoing, try /endtierlist", ephemeral = True, delete_after=7)
        except:
            pass
        return
    try:
        await interaction.response.send_message(f"starting tierlist", ephemeral = True, delete_after=5)
    except:
        pass
    if not timer: db.insert({'channel': interaction.channel.id, 'vote_msg_list': interaction.channel.id, 'memberids': interaction.channel.id})
    charliealtid = 704872368572465163
    botid = 1186185707258134560
    #gets all members that can view the channel, excludes bots and charlie's alt, includes my bot
    members = [x for x in interaction.channel.members if (not x.bot and x.id != charliealtid) or x.id == botid]
    vote_msg_list = []
    await interaction.channel.send('@everyone starting tierlist')
    
    for member in members:
        #reaction message
        vote_msg = await interaction.channel.send(f'Where should {member.global_name if member.global_name is not None else member.name} be placed?')
        await vote_msg.add_reaction('🆘')
        vote_msg.id
        indicators = ["s", "a", "b", "c", "d", "e", "f"]
        for i in indicators:
            await vote_msg.add_reaction(lookup("REGIONAL INDICATOR SYMBOL LETTER %s" % i))
        
        vote_msg_list.append(vote_msg.id)
    
    if timer: #timed
        presentDate = datetime.datetime.now()
        unix_timestamp = datetime.datetime.timestamp(presentDate) + voting_time_seconds
        await interaction.channel.send(f'ending <t:{round(unix_timestamp)}:R>')
        #timer needed
        await asyncio.sleep(voting_time_seconds)
        await createlist(interaction.channel, vote_msg_list, members) 
        return
        
    else: #not timed
        memberids = [x.id for x in members]
        db.update_multiple([
            ({'vote_msg_list': vote_msg_list}, where('channel') == interaction.channel.id),
            ({'memberids': memberids}, where('channel') == interaction.channel.id),
            ])
        return
        
@bot.tree.command(name = "endtierlist", description='Ends voting for the Teir List')
async def endtierlist(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
    if not (interaction.user.guild_permissions.administrator or interaction.user.id == myID):
        try:
            await interaction.response.send_message(f"You don't have permission to do that {interaction.message.author.mention}", ephemeral = True, delete_after=5)
        except:
            pass
        return
    
    db = TinyDB('databases/tierlist.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    
    # Check if there is no query in the database
    if len(res) == 0 or (res[0]['channel'] == res[0]['vote_msg_list'] and res[0]['channel'] == res[0]['memberids']):
        try:
            await interaction.response.send_message(f"no tierlist to end, try /tierlist", ephemeral = True, delete_after=7)
        except:
            pass
        return
    
    try:
        await interaction.response.send_message(f"ending tierlist", ephemeral = True, delete_after=5)
    except:
        pass
    res = res[0]
    vote_msg_list = res['vote_msg_list']
    memberids = [await bot.fetch_user(x) for x in res['memberids']] #gets user objects from ids
    await createlist(interaction.channel, vote_msg_list, memberids)
    
    # Remove the query from the database
    db.remove(User.channel == interaction.channel.id)

@bot.tree.command(name = "play", description='Plays music, if the bot is in a vc it will add the song to the queue (links work too)')
@app_commands.describe(query = "song to look up")
@app_commands.describe(music = "uses the youtube music API instead of the regular youtube API if this option is selected")
@app_commands.describe(im_feeling_lucky = "pick the first option in the selection")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id))
async def play(interaction: discord.Interaction, query: str, music: bool = True, im_feeling_lucky: bool = False):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}\nquery: {query} - music: {music} - im_feeling_lucky: {im_feeling_lucky}')
        
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild) # This allows for more functionality with voice channels
    
    #gets the queue from the database
    res,queue = getQueueFromDB(interaction.guild.id)
        
    #removes old queue if the bot is not in a vc 
    if (os.path.exists(f'vids/{interaction.guild.id}_queue') or len(res[0]['queue']) >=1) and voice is None:
        # if (os.path.exists(f'vids/{interaction.guild.id}.webm')): os.remove(f'vids/{interaction.guild.id}.webm')
        if (os.path.exists(f'vids/{interaction.guild.id}_queue')): shutil.rmtree(f'vids/{interaction.guild.id}_queue')
        queue.update({'loop': False}, where('server') == interaction.guild.id)
        queue.update({'shuffle': False}, where('server') == interaction.guild.id)
        queue.update({'disabled': False}, where('server') == interaction.guild.id)
        queue.update({'queue': []}, where('server') == interaction.guild.id)
        disable_enableQueue(interaction.guild.id, False)
    
    #checks if the bot is busy downloading a song
    queue = TinyDB('databases/queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    if res[0]['disabled']:
        try:
            await interaction.response.send_message(f"A song is already downloading, songs can not be added to the queue at this time", ephemeral = True, delete_after=5)
        except:
            pass
        return
    
    #checks if the user is in a vc
    uservoice = interaction.user.voice
    if uservoice is None:
        try:
            await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True, delete_after=5)
        except:
            pass
        return
    
    #runs the command for a youtube link
    if "https://www.youtube.com/" in query or "https://youtube.com/" in query:
        await queryYouTubeLink(query, interaction, uservoice, voice)
        return
    
    #runs the command for a spotify link
    if  "https://open.spotify.com/track/" in query or "https://open.spotify.com/playlist/" in query:
        # try:
        #     await interaction.response.send_message(f'Spotify links are being worked on', ephemeral = True, delete_after=5)
        # except:
        #     pass
        await querySpotifyLink(query, interaction, uservoice, voice)
        return
    
    #youtube music search
    if music: 
        yt = YTMusic()
        s = yt.search(query,filter="songs",limit=10)[:10]
        videoObjList = [YoutubeSearchCustom(i) for i in s]
        videoObjList2 = Search(query).results[:10]
    else: 
        videoObjList = Search(query).results[:10]
        yt = YTMusic()
        s = yt.search(query,filter="songs",limit=10)[:10]
        videoObjList2 = [YoutubeSearchCustom(i) for i in s]

    # debug(s,"s.json")
    if (len(videoObjList) == 0 or len(videoObjList2) == 0):
        try:
            await interaction.response.send_message(f"no results found", ephemeral = True, delete_after=5)
        except:
            pass
        return
    
    #making too many unnessary calls to youtube api, easy way to get rate limited
    # videoObjList = [YoutubeSearchCustom(i) for i in s]
    
    if im_feeling_lucky:
        videoObj = videoObjList[0]
        #live video
        if videoObj.length is None or videoObj.vidlength is None or videoObj.length_seconds is None:
            try:
                await interaction.response.send_message(f'You can not play live videos on the bot, Try Again', ephemeral=True, delete_after=7)
            except:
                pass
            return
        
        #video too long
        if videoObj.length_seconds > MAXVIDEOLENGTH:
            try:
                await interaction.response.send_message(f"Video is too long, go fuck yourself.", ephemeral = True, delete_after=7)
            except:
                pass
            return
        
        await playVideoObj(videoObj,interaction,uservoice,voice)
        return
    try:
        await interaction.response.send_message(f"Searching!", ephemeral = True, delete_after=3)
    except:
        pass
    #build the selection and embed
    selectionmessage = [(" "if k!=9 else "") + f"{k+1} : {v.title}\n" for k,v in enumerate(videoObjList[0:10])]
    select = Select(options = [discord.SelectOption(label = f'{k+1} : {v.title}'[:99] if len(f'{k+1}: {v.title}') > 99 else f'{k+1} : {v.title}', description = f'{v.length} - {v.viewCountText}', value=k) for k,v in enumerate(videoObjList[0:10])])
    selectionmessage2 = [(" "if k!=9 else "") + f"{k+1} : {v.title}\n" for k,v in enumerate(videoObjList2[0:10])]
    select2 = Select(options = [discord.SelectOption(label = f'{k+1} : {v.title}'[:99] if len(f'{k+1}: {v.title}') > 99 else f'{k+1} : {v.title}', description = f'{v.length} - {v.viewCountText}', value=k) for k,v in enumerate(videoObjList2[0:10])])
    
    #callback for when an option is chosen
    async def my_mycallback(ints:Interaction[Client]):
        #user did not search this
        if ints.user.id != interaction.user.id: 
            await ints.response.send_message(f"You cant select this video, you did not search it", ephemeral = True, delete_after=7)
            return
        
        #live video
        videoObj = videoObjList[int(select.values[0])]
        await playVideoObj(videoObj,ints,uservoice,voice,newint)
        return
    
    #callback for when an option is chosen but for videoObjList2
    async def my_mycallback2(ints:Interaction[Client]):
        #user did not search this
        if ints.user.id != interaction.user.id: 
            try:
                await ints.response.send_message(f"You cant select this video, you did not search it", ephemeral = True, delete_after=7)
            except:
                pass
            return
        
        #live video
        videoObj2 = videoObjList2[int(select2.values[0])]
        await playVideoObj(videoObj2,ints,uservoice,voice,newint)
        return
    
    #button callback for switching to youtube
    async def buttoncallback(ints:Interaction[Client]):
        try:
            await ints.response.send_message(f"Switching to YouTube", ephemeral = True, delete_after=3)
        except:
            pass
        #user did not search this
        if ints.user.id != interaction.user.id: 
            try:
                await ints.response.send_message(f"You cant do this, you did not search this song", ephemeral = True, delete_after=7)
            except:
                pass
            return
        
        await newint.edit(content=f'{searchstring2}```'+''.join(map(str, selectionmessage2))+'```',view=view2)
    
    #button callback for switching to youtube music 
    async def buttoncallback2(ints:Interaction[Client]):
        try:
            await ints.response.send_message(f"Switching to YouTubeMusic", ephemeral = True, delete_after=3)
        except:
            pass
        #user did not search this
        if ints.user.id != interaction.user.id: 
            try:
                await ints.response.send_message(f"You cant do this, you did not search this song", ephemeral = True, delete_after=7)
            except:
                pass
            return
        
        await newint.edit(content=f'{searchstring}```'+''.join(map(str, selectionmessage))+'```',view=view)
    
    #button callback for switching to youtube music 
    async def deletebuttoncallback(ints:Interaction[Client]):
        try:
            await ints.message.delete()
        except:
            pass
        
            
    #removes the selection message
    async def remove():
        try:
            await newint.delete()
        except:
            pass
        return
    
    #adds the callback to the selection
    select.callback = my_mycallback
    select2.callback = my_mycallback2
    #creates both views
    view = View()
    view2 = View()
    #timeout functions
    view.on_timeout = remove
    view2.on_timeout = remove
    #adds the selection to the view
    view.add_item(select)
    view2.add_item(select2)
    
    #creates buttons and adds their callbacks
    button = discord.ui.Button(label='Switch To YouTube', style=discord.ButtonStyle.red, custom_id="Switch1")
    button.callback = buttoncallback
    button2 = discord.ui.Button(label='Switch To YouTubeMusic', style=discord.ButtonStyle.green, custom_id="Switch2")
    button2.callback = buttoncallback2
    deletebutton = discord.ui.Button(label='Delete', style=discord.ButtonStyle.red, custom_id="Delete")
    deletebutton.callback = deletebuttoncallback
    
    #adds the buttons to the view
    view.add_item(button)
    view.add_item(deletebutton)
    view2.add_item(button2)
    view2.add_item(deletebutton)
    
    # davidsid = 382271649724104705
    #if interaction.user.id != davidsid else f'{interaction.user.mention} Searched: "gay furry porn"\n'
    
    #creates the search string messsage
    searchstring = f'{interaction.user.mention} Searched: "*{query}*" on YouTubeMusic\n' 
    searchstring2 = f'{interaction.user.mention} Searched: "*{query}*" on YouTube\n' 

    #sends the message depending on the starting view
    if music:
        newint = await interaction.channel.send(f'{searchstring}```'+''.join(map(str, selectionmessage))+'```',view=view)
    else:
        newint = await interaction.channel.send(f'{searchstring2}```'+''.join(map(str, selectionmessage2))+'```',view=view2)

@bot.tree.command(name = "queue", description='Views the queue')
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id))
async def queue(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
    
    #gets the queue from the database
    res,queue = getQueueFromDB(interaction.guild.id)

    #queue is empty
    if len(res[0]['queue']) == 0:
        try:
            await interaction.response.send_message(f"no queue", ephemeral = True, delete_after=3)
        except:
            pass
        return
    
    await interaction.response.send_message(f"Searching queue:", ephemeral = True, delete_after=3)
    
    #gets the total pages in the queue
    total_items = len(res[0]["queue"])
    items_per_page = 10
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    #creates the embed and view
    qembed = createQueueEmbed(interaction,res,1,total_pages)
    async def remove():
        await queueembed.delete()
        return
    
    queue_view = queueView(qembed,res,total_pages)
    queue_view.on_timeout = remove
    queueembed = await interaction.channel.send(embed=qembed,view=queue_view)
    queue_view.queueembed = queueembed
        
        
bot.run(TOKEN)