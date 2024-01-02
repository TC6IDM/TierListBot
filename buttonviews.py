from ast import List
import datetime
import discord
from tinydb import Query, TinyDB, where
from YoutubeSearchCustom import YoutubeSearchCustom
from discord.ui import Select, View
from createQueueEmbed import createQueueEmbed
from pytube.__main__ import YouTube
# from callbacks import my_mycallback,remove
# from songUtil import playVideoObj

class deleteView(discord.ui.View):
    '''
    Adds a delete button to the view
    '''
    
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red, custom_id="Delete")
    async def Delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        deletes the attached message
        '''
        try:
            await interaction.message.delete()
        except:
            pass
    
class queueView(deleteView):
    '''
    the view for the queue embed, has a previous, and next button
    
    :param embed:
        the embed the buttons are attached to
    :param res: 
        the list of Queue objects
    :param total_pages:
        the total number of pages in the queue
    '''
    
    embed: discord.Embed
    res: List
    listnumber: int
    queueembed: discord.Message
    total_pages: int
    
    def __init__(self, embed: discord.Embed, res:list, total_pages:int):
        super().__init__()
        self.embed = embed
        self.res = res
        self.listnumber = 1
        self.queueembed = None
        self.total_pages = total_pages
        
        
    @discord.ui.button(label='<', style=discord.ButtonStyle.grey, custom_id="previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The previous button, goes to the previous page in the queue
        '''
        print(f'Previous button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        #if the page number is in range, go to the previous page
        if 1 <= self.listnumber-1 <= self.total_pages:
            self.listnumber-=1
            try:
                await interaction.response.send_message('previous', ephemeral=True, delete_after=0)
            except:
                pass
            await self.queueembed.edit(embed=createQueueEmbed(interaction,self.res,self.listnumber,self.total_pages))
            return
        
        #otherwise, send an error message
        try:
            await interaction.response.send_message('out of range', ephemeral=True, delete_after=3)
        except:
            pass    
    @discord.ui.button(label='>', style=discord.ButtonStyle.grey, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The next button, goes to the next page in the queue
        '''
        print(f'Next button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        #if the page number is in range, go to the previous page
        if 1 <= self.listnumber+1 <= self.total_pages:
            self.listnumber+=1
            try:
                await interaction.response.send_message('next', ephemeral=True, delete_after=0)
            except:
                pass
            await self.queueembed.edit(embed=createQueueEmbed(interaction,self.res,self.listnumber,self.total_pages))
            return
        
        #otherwise, send an error message
        try:
            await interaction.response.send_message('out of range', ephemeral=True, delete_after=3)
        except:
            pass
                     
class SimpleView(discord.ui.View):
    '''
    the view for the song embed, contains a pause, play, skip, stop, loop, and shuffle button
    
    :param vc:
        the voice client of the bot
    '''
    
    vc: discord.VoiceClient
    embed: discord.Embed
    musicembed: discord.Message
    guildid: int
    
    def __init__(self, vc: discord.VoiceClient, interaction: discord.Interaction):
        super().__init__()
        self.vc = vc
        self.embed = None
        self.musicembed = None
        self.guildid = interaction.guild.id
        
    async def updatetitle(self):
        '''
        updates the title depending on if the bot is playing, paused, looped, or shuffling
        '''
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == self.guildid)
        
        if self.vc.is_playing():
            #playing and not looping
            self.embed.title = "🎶 Now Playing ▶️"
            
            if res[0]['loop']:
                #playing and looping
                self.embed.title = "🎶 Now Playing 🔁"
        else:
            #paused and not looping
            self.embed.title = "🎶 Paused ⏸️"
            if res[0]['loop']:
                #paused and looping
                self.embed.title = "🎶 Paused 🔁"
        
        if res[0]['shuffle']:
            self.embed.title += " 🔀"
            
        await self.musicembed.edit(embed=self.embed)
        return self.embed.title
        
    @discord.ui.button(label='Pause', style=discord.ButtonStyle.grey, custom_id="Pause")
    async def Pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Pause button, pauses the currently playing song
        '''
        print(f'Pause button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        try:
            await interaction.response.send_message('Pausing', ephemeral=True, delete_after=1)
        except:
            pass
        #if not paused, pause
        if self.vc.is_playing(): 
            self.vc.pause()
            await self.updatetitle()
    
    @discord.ui.button(label='Play', style=discord.ButtonStyle.green, custom_id="Play")
    async def Play(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Play button, plays the currently playing song
        '''
        print(f'Play button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        # await interaction.response.send_message('Playing', ephemeral=True, delete_after=1)
        
        #if not playing, play
        if self.vc.is_paused(): 
            self.vc.resume()
            await self.updatetitle()
        
    @discord.ui.button(label='Skip', style=discord.ButtonStyle.blurple, custom_id="Skip")
    async def Skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Skip button, skips the current song in the queue
        '''
        print(f'Skip button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        try:
            await interaction.response.send_message('Skipping', ephemeral=True, delete_after=3)
        except:
            pass
        #skips song via MAGIC!!!!! (idk how it works but it just does)
        self.vc.stop()
        
    @discord.ui.button(label='Stop', style=discord.ButtonStyle.red, custom_id="Stop")
    async def Stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Stop button, Stops the bot's music and clears the queue
        '''
        print(f'Stop button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        try:
            await interaction.response.send_message('Stopping', ephemeral=True, delete_after=3)
        except:
            pass
        #clears the queue and stops the bot (also stops looping)
        self.LOOP = False
        queue = TinyDB('queue.json')
        queue.update({'loop': False}, where('server') == interaction.guild.id)
        queue.update({'shuffle': False}, where('server') == interaction.guild.id)
        queue.update({'queue': []}, where('server') == interaction.guild.id)
        self.vc.stop()
        
    @discord.ui.button(label='Loop', style=discord.ButtonStyle.blurple, custom_id="Loop")
    async def Loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Loop button, Loops the current song
        '''
        print(f'Loop button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
    
        if not res[0]['loop']:
            queue.update({'loop': True}, where('server') == interaction.guild.id)
            await self.updatetitle()
            try:
                await interaction.response.send_message('Looping', ephemeral=True, delete_after=3)
            except:
                pass
        else:
            #if looping, unloop
            queue.update({'loop': False}, where('server') == interaction.guild.id)
            await self.updatetitle()
            try:
                await interaction.response.send_message('Unlooping', ephemeral=True, delete_after=3)
            except:
                pass
            
    @discord.ui.button(label='Shuffle', style=discord.ButtonStyle.blurple, custom_id="Shuffle")
    async def Shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        '''
        The Shuffleoop button, Shuffles the current song
        '''
        print(f'Shuffle button pressed by {interaction.user.display_name} in {interaction.guild.name} - {interaction.channel.name}')
        queue = TinyDB('queue.json')
        User = Query()
        res = queue.search(User.server == interaction.guild.id)
    
        if not res[0]['shuffle']:
            queue.update({'shuffle': True}, where('server') == interaction.guild.id)
            await self.updatetitle()
            try:
                await interaction.response.send_message('Shuffleing', ephemeral=True, delete_after=3)
            except:
                pass
        else:
            #if Shuffleing, UnShuffle
            queue.update({'shuffle': False}, where('server') == interaction.guild.id)
            await self.updatetitle()
            try:
                await interaction.response.send_message('UnShuffleing', ephemeral=True, delete_after=3)
            except:
                pass
    