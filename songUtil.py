from ast import List
import asyncio
from datetime import timedelta
import datetime
import glob
import json
import re
import shutil
from PIL import Image, ImageDraw, ImageFont
import io
from bs4 import BeautifulSoup
from discord import Client, File, Interaction, Message, TextChannel, VoiceClient, VoiceProtocol, VoiceState
import discord
import jsonpickle
import requests
from tinydb import Query, TinyDB
import yt_dlp
import os
import ffmpeg
from pytube import YouTube
# from pytube import YouTube
# from pytube import Search
import asyncio
from tinydb import TinyDB, Query, where
import os
from pathlib import Path
from buttonviews import SimpleView
from pytube.contrib.playlist import Playlist
from pytube.contrib.search import Search
from ytdlpUtil import MyLogger, my_hook

COOKIE_FILE = 'www.youtube.com_cookies.txt'
MAXVIDEOLENGTH = 3600

async def download(filepath: str, videourl: str) -> None:    
    '''
    downloads a given song to the given file path, waits for download to finish for other songs to be queued
    
    :param interaction: 
        discord interaction object
    :param filepath: 
        the file path where the song will be saved
    :param videourl: 
        the url of the video to be downloaded
    '''
    
    
    ydl_opts = {
        'format': 'webm/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'webm',
            'preferredquality': '320',#highest quality
        },{
            'key': 'FFmpegMetadata',
            'add_metadata': True,
        }],
        'ignoreerrors': True, #ignore errors
        'outtmpl': filepath, #save songs here .%(ext)s
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'cookiefile': COOKIE_FILE, #cookies for downloading age restricted videos
        }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videourl)
    
        
async def playtrack(interaction: Interaction[Client], queinfo, uservoice: VoiceState, vc: VoiceClient = None) -> tuple[VoiceClient, discord.Message]:
    '''
    Creates a queue embed which displays the next songs in the queue
    
    :param interaction: 
        discord interaction object
    :param res: 
        list of queue objects
    :param number: 
        the page number
    :param total_pages: 
        the total number of pages
        
    :rtype tuple[VoiceClient,discord.Message]:
    :returns:
        a tuple of the voice client and the message embed for the current song
    '''
    
    #gets the voice chanel the bot is in, if it is not in a voice channel, it joins the voice channel
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    if voice is None:
        vc = await uservoice.channel.connect(reconnect = False)
    
    #gets the user that requested the song
    userreq = interaction.client.get_user(queinfo['userid'])
    
    #wait untill the song exists
    while not os.path.exists(f'vids/{interaction.guild.id}.webm'):
        await asyncio.sleep(1)
    
    #create embed for the song
    embed=discord.Embed(title="🎶 Now Playing ▶️", url=queinfo['videourl'], color=0xff0000)
    embed.set_author(name=f'{interaction.client.application.name} Music', url="https://github.com/TC6IDM/TierListBot", icon_url=interaction.client.application.icon.url)
    embed.set_thumbnail(url=queinfo['thumbnail_url']) 
    embed.add_field(name="Track",value= queinfo['trackname'][:255],inline=True)
    embed.add_field(name="Requested By",value=userreq.mention,inline=True)
    embed.add_field(name="Duration",value=queinfo['duration'],inline=True)
    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    view = SimpleView(vc)
    
    #sends the embed
    musicembed = await interaction.channel.send(embed=embed, view=view)
    view.musicembed = musicembed
    view.embed = embed
    
    #loops this specific song if the user requests it
    debounce = 0 
    while debounce == 0 or view.LOOP:
        debounce=1
        
        #plays song
        vc.play(discord.FFmpegPCMAudio(f'vids/{interaction.guild.id}.webm'))
        
        #song is on
        while (vc.is_playing() or vc.is_paused()) and vc.is_connected():
            await asyncio.sleep(1)
        
        # disconnect after the player has finished or if the user forces the bot to leave
        if not vc.is_connected(): 
            print("someone forced the bot to leave the channel :(")
            view.LOOP = False
            vc.stop()
            await vc.disconnect(force = True)
            
            #reset the queue
            queue = TinyDB('queue.json')
            queue.update({'queue': []}, where('server') == interaction.guild.id)
            disable_enableQueue(interaction.guild.id, False)
            break
    
    return vc,musicembed
    
async def downloadAndPlay(interaction: Interaction[Client], filepath: str, videourl: str, uservoice: VoiceState) -> None:
    '''
    downloads a given song to the given file path and starts the queue
    
    :param interaction: 
        discord interaction object
    :param filepath: 
        the file path where the song will be saved
    :param videourl: 
        the url of the video to be downloaded
    :param uservoice: 
        the voice channel the user is in
    '''
    
    # user is not in a voice channel
    if uservoice.channel is None:
        await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True, delete_after=5)
        return

    #downloads and plays
    await download(interaction,filepath,videourl)
    await startqueue(interaction,uservoice)
    return
    
async def startqueue(interaction: Interaction[Client], uservoice: VoiceState) -> None:
    '''
    starts the queue in 
    
    :param interaction: 
        discord interaction object
    :param uservoice: 
        the voice channel the user is in
    '''
    # user is not in a voice channel
    if uservoice.channel is None:
        await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True, delete_after=5)
        return
    
    #gets the queue
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    
    vc = None
    
    #loops untill the queue is finished
    while (len(res[0]['queue']) >=1):
        
        # plays the song next in the queue
        queinfo = res[0]['queue'][0]
        print(f'Now playing: {queinfo["trackname"]} in {interaction.guild.name} - {interaction.channel.name}')
        vc,musicembed = await playtrack(interaction,queinfo,uservoice,vc)
        
        #cleans up
        vc.stop()
        await musicembed.delete()
        try:
            os.remove(f'vids/{interaction.guild.id}.webm')
        except:
            pass
        
        # Create a new queue directory if it does not exist
        dir_path = 'C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/'+str(interaction.guild.id)+"_queue/"
        isExist = os.path.exists(dir_path)
        if not isExist:
            os.makedirs(dir_path)

        #finds the songs in the queue
        paths = os.listdir(dir_path)
        os.chdir(dir_path)
        
        #sorts them by creation time
        paths.sort(key=os.path.getctime)
        os.chdir('C:/Users/Owner/Desktop/TierListBot/TierListBot')
        
        #renames the song to be played next, if the queue is over, then removes the queue directory
        if len(paths) >=1: 
            os.rename(f'vids/{interaction.guild.id}_queue/{paths[0]}', f'vids/{interaction.guild.id}.webm')
        else:
            shutil.rmtree(f'vids/{interaction.guild.id}_queue')

        #removes the song from the queue
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
        queue.update({'queue': res[0]['queue'][1:]}, where('server') == interaction.guild.id)
        queue = TinyDB('queue.json')
        User = Query()
        
        #gets the new queue
        res = queue.search(User.server == interaction.guild.id)
    
    #stops the bot from playing, disconnects and removes all queue files
    vc.stop()
    await vc.disconnect(force = True)
    if (os.path.exists(f'vids/{interaction.guild.id}.webm')): os.remove(f'vids/{interaction.guild.id}.webm')
    if (os.path.exists(f'vids/{interaction.guild.id}_queue')): shutil.rmtree(f'vids/{interaction.guild.id}_queue')
    queue = TinyDB('queue.json')
    queue.update({'queue': []}, where('server') == interaction.guild.id)
    disable_enableQueue(interaction.guild.id, False)
    return
           
def addtoQueue(interaction: Interaction[Client], videoObj: YouTube) -> str:
    '''
    adds the given video to the queue
    
    :param interaction: 
        discord interaction object
    :param videoObj: 
        the video object to be added to the queue
    :rtype str:
    :returns:
        the output directory of the song
    '''
    
    #gets the filepaths for the output and the queue directory
    output = 'C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/'+str(interaction.guild.id)+'.webm'
    outputExists = os.path.exists(output)
    dir_path = 'C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/'+str(interaction.guild.id)+"_queue/"
    folderExists = os.path.exists(dir_path)
    
    # Create a new queue directory if it does not exist
    if not folderExists:
        os.makedirs(dir_path)
        
    #if there is already one song in the queue, then we make the name of the next song equal to the last song in the queue's number plus one
    if outputExists:
        #gets files in the queue directory and sorts them
        files = os.listdir(dir_path)
        os.chdir(dir_path)
        files.sort(key=os.path.getctime)
        
        #gets the number of the last song in the queue and adds one to it
        queNumber = int(re.search(r'^(.*?)(?=\.)', files[-1]).group(0))+1 if len(files) >=1 else 0
        
        #output dir is is where the new song is to be downloaded into
        output = '/vids/'+str(interaction.guild.id)+'_queue/'+str(queNumber)+'.webm'
        os.chdir('C:/Users/Owner/Desktop/TierListBot/TierListBot')
        
    #adds the song to the queue
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    
    if len(res) == 0:
        queue.insert({'server': interaction.guild.id, 'queue': 
            [{'videourl':videoObj.watch_url,'userid':interaction.user.id,'thumbnail_url':videoObj.thumbnail_url,'trackname':videoObj.title,'duration':videoObj.vidlength, 'output':output}],
            # 'loop': False, 'shuffle': False, 
            'disabled': False})
    else:
        queue.update({'queue': res[0]['queue']+[{'videourl':videoObj.watch_url,'userid':interaction.user.id,'thumbnail_url':videoObj.thumbnail_url,'trackname':videoObj.title,'duration':videoObj.vidlength, 'output':output}]}, where('server') == interaction.guild.id)
    
    return output

async def queryLink(query:str, interaction: Interaction[Client], uservoice: VoiceState, voice: VoiceProtocol) -> None:
    '''
    this query will be ran when the user wants to play a song from a link
    works with playlists and videos
    
    :param query:
        the possible link that the user sends in
    :param interaction: 
        discord interaction object
    :param uservoice:
        the voice channel the user is in
    :param voice:
        the voice channel the bot is in
    '''
    
    #video ID from the query to check if the video exists, makes a video object from it if it is a real video
    video_id = re.search(r'(?<=watch\?v=)(.*?)(?=&|$)', query)
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    video_url = checker_url + (str(video_id.group(0)) if video_id is not None else "0")
    if video_id and requests.get(video_url).status_code == 200: 
        query = f'https://www.youtube.com/watch?v={str(video_id.group(0))}'
        videoObj = Search(query).results
        if len(videoObj) == 0: 
            await interaction.response.send_message(f"invalid youtube link", ephemeral = True, delete_after=5)
            return
        videoObj = videoObj[0]
        # videoObj = YouTube(query) #(TODO) FIX THIS
        # print(len(videoObj))
        await interaction.response.send_message(f'playing', ephemeral = True, delete_after=5)
        await playVideoObj(videoObj, interaction, uservoice, voice)
        return
    
    #returns if the given link is also not a playlist
    if ('&list=' not in query and '?list='not in query) or requests.get(query).status_code != 200: 
        await interaction.response.send_message(f"invalid youtube link", ephemeral = True, delete_after=5)
        return

    #gets the playlist object and checks if it is a real playlist
    playlist = Playlist(query)
    if len(playlist) == 0:
        await interaction.response.send_message(f"invalid youtube link", ephemeral = True, delete_after=5)
        return
    
    # Playlist is real, send out default message and stop people from adding more songs to the queue (TODO)
    await interaction.response.send_message(f'analysing playlist', ephemeral = True, delete_after=5)
    waitingmessage = await interaction.channel.send(f'analysing playlist from {interaction.user.mention} - {query} (?/?)')
    
    
    #disables people adding to the queue while the playlist is being downloaded
    disable_enableQueue(interaction.guild.id, True)
    
    endtext = ""
    #enumerates through the playlist object
    for v,i in enumerate(playlist):
        
        #edits the message to show where in the playlist we are at
        await waitingmessage.edit(content=f'analysing playlist from {interaction.user.mention} - {query} ({v+1}/{len(playlist)})\n{endtext}')
        
        #makes sure that the video is a working video
        video_id = re.search(r'(?<=watch\?v=)(.*?)(?=&|$)', i)
        checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
        video_url = checker_url + (str(video_id.group(0)) if video_id is not None else "0")
        if video_url == "0" or requests.get(video_url).status_code != 200: 
            endtext += f'song {v+1} - {i} was not added to the queue (invalid url)\n'
            continue
        
        #checks if the video is not a live video, and not too long
        newurl = f'https://www.youtube.com/watch?v={str(video_id.group(0))}'
        videoObj = Search(newurl).results
        if len(videoObj) == 0: 
            endtext += f'song {v+1} - {i} was not added to the queue (url broken)\n'
            continue
        videoObj = videoObj[0]
        # videoObj = YouTube(newurl) #(TODO) FIX THIS
        if videoObj.length is None or videoObj.vidlength is None or videoObj.length_seconds is None: 
            endtext += f'song {v+1} - {videoObj.title} was not added to the queue (possibly live video)\n'
            continue
        if videoObj.length_seconds > MAXVIDEOLENGTH: 
            endtext += f'song {v+1} - {videoObj.title} was not added to the queue (video too long)\n'
            continue
        
        #adds the video to the queue and downloads it
        output = addtoQueue(interaction,videoObj)
        await download(interaction,output,newurl)
    
    #downloading is done so the user can add back to the queue now
    disable_enableQueue(interaction.guild.id, False)
    
    #delete the message and start the queue when its done downloading
    await waitingmessage.delete()
    if voice is None: await startqueue(interaction,uservoice)
    return

async def playVideoObj(videoObj: YouTube, interaction: Interaction[Client], uservoice: VoiceState, voice: VoiceProtocol, newint: Message = None) -> None:
    '''
    the repsonce to when the user wants to play a video
    
    :param videoObj:
        the video object to be added to the queue
    :param interaction: 
        discord interaction object
    :param uservoice:
        the voice channel the user is in
    :param voice:
        the voice channel the bot is in
    :param newint: 
        a message object to be deleted if needed
    '''
    
    #live video
    if videoObj.length is None or videoObj.vidlength is None or videoObj.length_seconds is None:
        await interaction.response.send_message(f'You can not play live videos on the bot, Try Again', ephemeral=True, delete_after=7)
        return
    
    #video too long
    if videoObj.length_seconds > MAXVIDEOLENGTH:
        await interaction.response.send_message(f"Video is too long, go fuck yourself.", ephemeral = True, delete_after=7)
        return
    
    #delete old interaction if we need to
    if newint: await newint.delete() 
    
    #add to queue
    output = addtoQueue(interaction,videoObj)
    
    #bot is not in call so join the call and play
    if voice is None:
        # await interaction.response.send_message(f"playing", ephemeral = True, delete_after=3)
        await downloadAndPlay(interaction,output,videoObj.watch_url,uservoice)
    
    #bot is in call so just download the song
    else:
        # await interaction.response.send_message(f"adding to Queue", ephemeral = True, delete_after=3)
        await download(interaction,output,videoObj.watch_url)
    
    return
    
def getQueueFromDB(guildID: int) -> tuple[List,TinyDB]:
    '''
    gets the current queue from the guild id given
    
    :param guildID:
        the id of the guild the user is in
    :rtype tuple[List[object],TinyDB]:
    :returns:
        a tuple of a list of queue objects and the queue database object
    '''
    
    #gets the queue
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == guildID)
    
    #if there is no queue insert a blank queue
    if len(res) == 0:
        queue.insert({'server': guildID, 'queue': [], 'disabled': False})
        User = Query()
        res = queue.search(User.server == guildID)
    return res,queue

def disable_enableQueue(guildID: int, disable: bool = True) -> None:
    '''
    disables or enables the queue for the given guild
    
    :param guildID:
        the id of the guild the user is in
    :param disable:
        wheither to disable or enable the queue, Disables by default
            
    '''
    
    #gets the queue
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == guildID)
    
    #if server is not in the databse, add it
    if len(res) == 0:
        queue.insert({'server': guildID, 'queue': [], 'disabled': disable})
        return
    
    #disables or enables the queue
    queue.update({'disabled': disable}, where('server') == guildID)
    return