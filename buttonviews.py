from ast import List
import datetime
import discord
from tinydb import TinyDB, where

from createQueueEmbed import createQueueEmbed

class deleteView(discord.ui.View):
        
    def __init__(self):
        super().__init__()
        
    @discord.ui.button(label='Delete', style=discord.ButtonStyle.red, custom_id="Delete")
    async def Delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.send_message('deleting', ephemeral=True, delete_after=3)
        await interaction.message.delete()
        
class queueView(deleteView):
    embed: discord.Embed
    res: List
    listnumber: int
    queueembed: discord.Message
    total_pages: int
    
    def __init__(self,embed: discord.Embed,res:list,total_pages:int):
        super().__init__()
        self.embed = embed
        self.res = res
        self.listnumber = 1
        self.queueembed = None
        self.total_pages = total_pages
        
        
    @discord.ui.button(label='<', style=discord.ButtonStyle.grey, custom_id="previous")
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if 1 <= self.listnumber-1 <= self.total_pages:
            self.listnumber-=1
            await interaction.response.send_message('previous', ephemeral=True, delete_after=3)
            await self.queueembed.edit(embed=createQueueEmbed(interaction,self.res,self.listnumber,self.total_pages))
        else:
            await interaction.response.send_message('out of range', ephemeral=True, delete_after=3)
            
    @discord.ui.button(label='>', style=discord.ButtonStyle.grey, custom_id="next")
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if 1 <= self.listnumber+1 <= self.total_pages:
            self.listnumber+=1
            await interaction.response.send_message('next', ephemeral=True, delete_after=3)
            await self.queueembed.edit(embed=createQueueEmbed(interaction,self.res,self.listnumber,self.total_pages))
        else:
            await interaction.response.send_message('out of range', ephemeral=True, delete_after=3)
    
        

    
                    
class SimpleView(discord.ui.View):
    
    vc: discord.VoiceClient
    LOOP: bool
    embed: discord.Embed
    musicembed: discord.Message
    
    
    def __init__(self, vc: discord.VoiceClient):
        super().__init__()
        self.vc = vc
        self.LOOP = False
        self.embed = None
        
    async def updatetitle(self):
        if self.vc.is_playing():
            self.embed.title = "🎶 Now Playing ▶️"
            if self.LOOP:
                self.embed.title = "🎶 Now Playing 🔁"
        else:
            self.embed.title = "🎶 Paused ⏸️"
            if self.LOOP:
                self.embed.title = "🎶 Paused 🔁"
            
        await self.musicembed.edit(embed=self.embed)
        
    @discord.ui.button(label='Pause', style=discord.ButtonStyle.grey, custom_id="Pause")
    async def Pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Pausing', ephemeral=True, delete_after=3)
        if self.vc.is_playing(): 
            self.vc.pause()
            await self.updatetitle()
            print("PAUSED!")
    
    @discord.ui.button(label='Play', style=discord.ButtonStyle.green, custom_id="Play")
    async def Play(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Playing', ephemeral=True, delete_after=3)
        if self.vc.is_paused(): 
            self.vc.resume()
            await self.updatetitle()
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
        if not self.LOOP:
            self.LOOP = True
            await self.updatetitle()
            await interaction.response.send_message('Looping', ephemeral=True, delete_after=3)
        else:
            self.LOOP = False
            await self.updatetitle()
            await interaction.response.send_message('Unlooping', ephemeral=True, delete_after=3)
        # self.vc.stop()