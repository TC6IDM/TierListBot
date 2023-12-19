import asyncio
import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from unicodedata import lookup
from discord import File
from tinydb import TinyDB, Query, where

from PIL import Image, ImageDraw, ImageFont
import io
from util import createlist

load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.tree.command(name = "ping", description='Returns latency')
async def ping(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick}')
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms", ephemeral = True)

@bot.tree.command(name = "hello", description='Says hello')
async def hello(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick}')
    await interaction.response.send_message(f"Hey {interaction.user.mention}!", ephemeral = True)

@bot.tree.command(name = "say", description='Repeats what you say')
@app_commands.describe(thing_to_say = "what should i say")
@app_commands.describe(secret = "is this a secret?")
async def say(interaction: discord.Interaction, thing_to_say: str, secret: bool = False):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.nick}')
    await interaction.response.send_message(f"{interaction.user.mention} said: {thing_to_say}" if not secret else f"{thing_to_say}")
    
@bot.tree.command(name = "tierlist", description='Starts voting for the Teir List')
@app_commands.describe(timer = "is this timed? (true: timer, false: command to end)")
@app_commands.describe(voting_time_seconds = "How long are we waiting for votes to come in? (seconds)")
async def tierlist(interaction: discord.Interaction, timer: bool = False, voting_time_seconds: int = 5):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.name}')
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
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.name}')
    db = TinyDB('db.json')
    User = Query()
    res = db.search(User.channel == interaction.channel.id)
    
    if len(res) == 0:
        await interaction.response.send_message(f"no tierlist to end", ephemeral = True)
        return
    
    await interaction.response.send_message(f"KYS!!!!", ephemeral = True)
    
    res = res[0]
    vote_msg_list = res['vote_msg_list']
    memberids = [await bot.fetch_user(x) for x in res['memberids']]
    await createlist(interaction.channel, vote_msg_list, memberids)
    
    # Remove the query from the database
    db.remove(User.channel == interaction.channel.id)
    
bot.run(TOKEN)