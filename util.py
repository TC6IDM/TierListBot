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
from discord import Client, File, Interaction, TextChannel, VoiceClient, VoiceState
import discord
import jsonpickle
import requests
from tinydb import Query, TinyDB
import yt_dlp
import os
import ffmpeg
from pytube import YouTube
from pytube import Search
import asyncio
from tinydb import TinyDB, Query, where
import os
from pathlib import Path
# song_queue = []

# async def play_next(interaction: Interaction[Client], source):
#     vc = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
#     if len(song_queue) >= 1:
#         del song_queue[0]
#         vc.play(discord.FFmpegPCMAudio(source=source, after=lambda e: play_next(interaction)))
#     else:
#         await interaction.channel.send("No more songs in queue.")
#         # asyncio.sleep(90) #wait 1 minute and 30 seconds
#         # if not vc.is_playing():
#         #     asyncio.run_coroutine_threadsafe(vc.disconnect(interaction), interaction.client.loop)
#         #     asyncio.run_coroutine_threadsafe(interaction.send("No more songs in queue."), interaction.client.loop)
            
class SimpleView(discord.ui.View):
    
    def __init__(self, vc: discord.VoiceClient):
        super().__init__()
        self.vc = vc
        self.LOOP = 0
        
    @discord.ui.button(label='Pause', style=discord.ButtonStyle.grey, custom_id="Pause")
    async def Pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Pausing', ephemeral=True, delete_after=3)
        if self.vc.is_playing(): 
            self.vc.pause()
            print("PAUSED!")
    
    @discord.ui.button(label='Play', style=discord.ButtonStyle.green, custom_id="Play")
    async def Play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Playing', ephemeral=True, delete_after=3)
        if self.vc.is_paused(): 
            self.vc.resume()
            print("RESUMED!")
        
    @discord.ui.button(label='Skip', style=discord.ButtonStyle.blurple, custom_id="Skip")
    async def Skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Skipping', ephemeral=True, delete_after=3)
        self.vc.stop()
        
    @discord.ui.button(label='Stop', style=discord.ButtonStyle.red, custom_id="Stop")
    async def Stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Stopping', ephemeral=True, delete_after=3)
        queue = TinyDB('queue.json')
        queue.update({'queue': []}, where('server') == interaction.guild.id)
        self.vc.stop()
        
    @discord.ui.button(label='Loop', style=discord.ButtonStyle.blurple, custom_id="Loop")
    async def Loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.LOOP == 0:
            self.LOOP = 1 
            await interaction.response.send_message('Looping', ephemeral=True, delete_after=3)
        else:
            self.LOOP = 0
            await interaction.response.send_message('Unlooping', ephemeral=True, delete_after=3)
        # self.vc.stop()
        
    # @discord.ui.button(label='Shuffle', style=discord.ButtonStyle.blurple, custom_id="Shuffle")
    # async def Shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     if self.LOOP == 0:
    #         self.LOOP = 1 
    #         await interaction.response.send_message('Looping', ephemeral=True, delete_after=3)
    #     else:
    #         self.LOOP = 0
    #         await interaction.response.send_message('Unlooping', ephemeral=True, delete_after=3)
        # self.vc.stop()
# def visual_length(s):
#     # Calculate visual length considering variable-width characters
#     return sum(1 + (c > '\x7F') for c in s)

async def createlist(channel: TextChannel, vote_msg_list, members):
    '''
    Creates a tier list based on the votes and sends it to the channel
    
    channel: discord channel object
    vote_msg_list: list of message ids that correspond to the vote messages
    members: list of member objects
    '''

    file_path = 'tierlist.png'
    image = Image.open(file_path)
    IMAGE_WIDTH = image.size[0]
    IMAGE_HEIGHT = image.size[1]
    AVATAR_SIZE = int(IMAGE_HEIGHT/8)
    # print(IMAGE_HEIGHT)
    
    #the teir is the key, the value is a list of the original x position and the y position fraction relative to the image height
    distances = {"🆘": [125,1/8], "🇸": [125,2/8], "🇦": [125,3/8], "🇧": [125,4/8], "🇨": [125,5/8], "🇩": [125,6/8], "🇪": [125,7/8], "🇫": [125,8/8]}
    # finalmessage = ""
    
    #numerate through the members and vote messages
    for val, vote_msg in enumerate(vote_msg_list):
        try:
            vote_msg = await channel.fetch_message(vote_msg)
        except discord.errors.NotFound:
            await channel.send("Error fetching tier list messages, some retard probably deleted them.",delete_after=10)
            return
        highest_reaction = ""
        highest_reaction_number = 0
        for reaction in vote_msg.reactions:
            if (reaction.count-1) > highest_reaction_number:
                highest_reaction = reaction.emoji
                highest_reaction_number = reaction.count-1
        # finalmessage += f"{members[val].global_name if members[val].global_name is not None else members[val].name} got placed in {highest_reaction} tier with {highest_reaction_number} votes!\n" if highest_reaction_number > 0 else f"{members[val].global_name if members[val].global_name is not None else members[val].name} did not get any votes!\n" 
        
        #if no one voted for this person, put them in the F tier
        highest_reaction = highest_reaction if highest_reaction != "" else "🇫"
        
        # davidsid = 382271649724104705
        # highest_reaction = "🆘" if members[val].id == davidsid else highest_reaction # fuck you david
        
        #find the avatar of the person
        # print(members[val].avatar)
        avatar_asset = members[val].avatar if members[val].avatar is not None else members[val].default_avatar
        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)
        avatar_image = Image.open(buffer_avatar)
        avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) # 
        # print(int(IMAGE_HEIGHT/distances[highest_reaction][1] - AVATAR_SIZE))
        
        #paste the avatar onto the image, X position is the original x position + the number of avatars already in that tier * the avatar size, the Y position corresponds to the height of the tier - the avatar size
        image.paste(avatar_image, (int(distances[highest_reaction][0]), int(IMAGE_HEIGHT*distances[highest_reaction][1] - AVATAR_SIZE)))
        distances[highest_reaction][0] += AVATAR_SIZE #move the next avatar over

        #save the image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')    
        buffer_output.seek(0)

    # send image
    await channel.send(file=File(buffer_output, 'myimage.png'))
    # await channel.send(finalmessage[0:-1])
    
    
def my_hook(d):
    if d['status'] == 'finished':
        # print(d['filepath'])
        # print('Done downloading, now post-processing ...')
        pass

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

async def download(interaction: Interaction[Client], videourl: str, uservoice: VoiceState):
    # await interaction.channel.send(f"Playing {videourl}")
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    
    
    output = '/vids/'+str(interaction.guild.id)+'.%(ext)s'
    dir_path = 'C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/'+str(interaction.guild.id)+"_queue/"
    isExist = os.path.exists(dir_path)
    if not isExist:
    # Create a new directory because it does not exist
        os.makedirs(dir_path)
    
    # paths = sorted(Path(dir_path).iterdir(), key=os.path.getmtime)
    
    if voice is not None:
        files = os.listdir(dir_path)
        os.chdir(dir_path)
        files.sort(key=os.path.getctime)
        # if len(files) >=1: print(files[-1])
        queNumber = int(re.search(r'^(.*?)(?=\.)', files[-1]).group(0))+1 if len(files) >=1 else 0
        output = '/vids/'+str(interaction.guild.id)+'_queue/'+str(queNumber)+'.%(ext)s'
        os.chdir('C:/Users/Owner/Desktop/TierListBot/TierListBot')
        pass
    
    
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
        'outtmpl': output, #save songs here .%(ext)s
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'cookiefile': COOKIE_FILE, #cookies for downloading age restricted videos
        }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(videourl)
        
    
async def play(interaction: Interaction[Client], queinfo, uservoice: VoiceState, vc: VoiceClient = None):
    # videourl = queinfo['videourl']
    # userid = queinfo['userid']
    # thumbnailURL = queinfo['thumbnail_url']
    # trackname = queinfo['trackname']
    # duration = queinfo['duration']
    
    voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    if voice is None:
        vc = await uservoice.channel.connect(reconnect = False)
    
    userreq = interaction.client.get_user(queinfo['userid'])
    
    while not os.path.exists(f'vids/{interaction.guild.id}.webm'):
        await asyncio.sleep(1)
    
    #could put this in db
    # thumbnailURL = "https://img.youtube.com/vi/"+str(re.search(r'(?<=watch\?v=)(.*?)(?=&|$)', videourl).group(0))+"/maxresdefault.jpg"
    # sr = Search(videourl).results
    
    #could put this in db
    # trackname = sr[0].title[:255] if len(sr) > 0 else "Unknown"
    # track_info = {
    #     'Track': trackname, #slow as fuck but who cares lmao check if there is no results
    #     'Video_Url': videourl,
    #     'Requested_By': userreq.mention if userreq is not None else "Someone",
    #     'Duration': str(timedelta(seconds=int(float(ffmpeg.probe("vids/"+str(interaction.guild.id)+".webm")["format"]["duration"]))))
    # }
    
    #   this doesnt work :(
    # track_column_width = max(visual_length(track_info['Track']), len('Track'))
    # requested_by_column_width = max(visual_length(track_info['Requested By']), len('Requested By'))
    # duration_column_width = max(visual_length(track_info['Duration']), len('Duration'))

    embed=discord.Embed(title="🎶Now Playing", url=queinfo['videourl'], color=0xff0000)
    embed.set_author(name=f'{interaction.client.application.name} Music', url="https://github.com/TC6IDM/TierListBot", icon_url=interaction.client.application.icon.url)
    embed.set_thumbnail(url=queinfo['thumbnail_url']) #technicall does this twice but im too lazy to do it any other way
    embed.add_field(name="Track",value= queinfo['trackname'][:255],inline=True)
    embed.add_field(name="Requested By",value=userreq.mention,inline=True)
    embed.add_field(name="Duration",value=queinfo['duration'],inline=True)
    # embed.add_field(name=f"{'Track':{track_column_width}}   {'Requested By':<{requested_by_column_width}}   {'Duration':{duration_column_width}}", value= f"{track_info['Track']:{track_column_width}}   {track_info['Requested By']:<{requested_by_column_width}}   {track_info['Duration']}",inline=True)
    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    view = SimpleView(vc)
    
    #edit instead?????
    musicembed = await interaction.channel.send(embed=embed, view=view)
    
    # , after=lambda e: print('done', e)
    #, after=lambda e: play_next(interaction,f'vids/{interaction.guild.id}.webm')
    debounce = 0 
    while debounce == 0 or view.LOOP == 1:
        debounce=1
        vc.play(discord.FFmpegPCMAudio(f'vids/{interaction.guild.id}.webm'))
        # player = vc.create_ffmpeg_player('vuvuzela.webm', after=lambda: print('done'))
        # print(vc.is_playing())
        
        while (vc.is_playing() or vc.is_paused()) and vc.is_connected():
            await asyncio.sleep(1)
        # disconnect after the player has finished
    if not vc.is_connected(): 
        print("someone forced the bot to leave the channel :(")
        await vc.disconnect(force = True)
        queue = TinyDB('queue.json')
        queue.update({'queue': []}, where('server') == interaction.guild.id)
    
    return vc,musicembed
    
async def downloadAndPlay(interaction: Interaction[Client], videourl: str, uservoice: VoiceState):
    # create StreamPlayer
    if uservoice.channel is None:
        await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True, delete_after=5)
        return
    # voice = discord.utils.get(interaction.client.voice_clients, guild=interaction.guild)
    await download(interaction,videourl,uservoice)
    # print(voice)
    # if voice is not None: return
    
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    vc = None
    while (len(res[0]['queue']) >=1):
        # print(videourl)
        queinfo = res[0]['queue'][0]
        vc,musicembed = await play(interaction,queinfo,uservoice,vc)
        vc.stop()
        await musicembed.delete()
        
        os.remove(f'vids/{interaction.guild.id}.webm')
        dir_path = 'C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/'+str(interaction.guild.id)+"_queue/"
        isExist = os.path.exists(dir_path)
        if not isExist:
        # Create a new directory because it does not exist
            os.makedirs(dir_path)

        paths = os.listdir(dir_path)
        os.chdir(dir_path)
        paths.sort(key=os.path.getctime)
        os.chdir('C:/Users/Owner/Desktop/TierListBot/TierListBot')
        
        if len(paths) >=1: 
            os.rename(f'vids/{interaction.guild.id}_queue/{paths[0]}', f'vids/{interaction.guild.id}.webm')
        else:
            shutil.rmtree(f'vids/{interaction.guild.id}_queue')
                
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
        queue.update({'queue': res[0]['queue'][1:]}, where('server') == interaction.guild.id)
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
    
    vc.stop()
    await vc.disconnect(force = True)
    if (os.path.exists(f'vids/{interaction.guild.id}.webm')): os.remove(f'vids/{interaction.guild.id}.webm')
    if (os.path.exists(f'vids/{interaction.guild.id}_queue')): shutil.rmtree(f'vids/{interaction.guild.id}_queue')
    
        
def addtoQueue(interaction: Interaction[Client], videoObj: YouTube):
    queue = TinyDB('queue.json')
    User = Query()
    res = queue.search(User.server == interaction.guild.id)
    if len(res) == 0:
        queue.insert({'server': interaction.guild.id, 'queue': [{'videourl':videoObj.watch_url,'userid':interaction.user.id,'thumbnail_url':videoObj.thumbnail_url,'trackname':videoObj.title,'duration':videoObj.vidlength}]})
        return
    # print(res[0]['queue'])
    queue.update({'queue': res[0]['queue']+[{'videourl':videoObj.watch_url,'userid':interaction.user.id,'thumbnail_url':videoObj.thumbnail_url,'trackname':videoObj.title,'duration':videoObj.vidlength}]}, where('server') == interaction.guild.id)
    
    

