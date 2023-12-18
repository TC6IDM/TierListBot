import asyncio
import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from unicodedata import lookup
from discord import File

from PIL import Image, ImageDraw, ImageFont
import io

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
@app_commands.describe(voting_time_seconds = "How long are we waiting for votes to come in? (seconds)")
async def tierlist(interaction: discord.Interaction, voting_time_seconds: int = 5):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.name}')
    await interaction.response.send_message(f"kys!!!!", ephemeral = True)
    members = [x for x in interaction.channel.members if not x.bot]
    vote_msg_list = []
    for member in members:
        vote_msg = await interaction.channel.send(f'Where should {member.global_name if member.global_name is not None else member.name} be placed?')
        await vote_msg.add_reaction('🆘')
        indicators = ["s", "a", "b", "c", "d", "e", "f"]
        for i in indicators:
            await vote_msg.add_reaction(lookup("REGIONAL INDICATOR SYMBOL LETTER %s" % i))
        
        vote_msg_list.append(vote_msg)
        
    await asyncio.sleep(voting_time_seconds)
    
    file_path = 'tierlist.png'
    image = Image.open(file_path)
    IMAGE_WIDTH = image.size[0]
    IMAGE_HEIGHT = image.size[1]
    AVATAR_SIZE = int(IMAGE_HEIGHT/8)
    print(IMAGE_HEIGHT)
    
    #the teir is the key, the value is a list of the original x position and the y position fraction relative to the image height
    distances = {"🆘": [125,1/8], "🇸": [125,2/8], "🇦": [125,4/8], "🇧": [125,5/8], "🇨": [125,6/8], "🇩": [125,3/8], "🇪": [125,7/8], "🇫": [125,8/8]}
    # finalmessage = ""
    
    #numerate through the members and vote messages
    for val, vote_msg in enumerate(vote_msg_list):
        vote_msg = await vote_msg.channel.fetch_message(vote_msg.id)
        highest_reaction = ""
        highest_reaction_number = 0
        for reaction in vote_msg.reactions:
            if (reaction.count-1) > highest_reaction_number:
                highest_reaction = reaction.emoji
                highest_reaction_number = reaction.count-1
        # finalmessage += f"{members[val].global_name if members[val].global_name is not None else members[val].name} got placed in {highest_reaction} tier with {highest_reaction_number} votes!\n" if highest_reaction_number > 0 else f"{members[val].global_name if members[val].global_name is not None else members[val].name} did not get any votes!\n" 
        
        #if no one voted for this person, put them in the F tier
        highest_reaction = highest_reaction if highest_reaction != "" else "🇫"
        
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
    await interaction.channel.send(file=File(buffer_output, 'myimage.png'))
    # await interaction.channel.send(finalmessage[0:-1])
    

bot.run(TOKEN)