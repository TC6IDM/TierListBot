import asyncio
import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from unicodedata import lookup

# def run_discord_bot():
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
async def tierlist(interaction: discord.Interaction):
    print(f'Command: {interaction.command.name} was invoked by {interaction.user.name}')
    await interaction.response.send_message(f"kys!!!!", ephemeral = True)
    members = [x for x in interaction.channel.members if not x.bot]
    # print(members)
    vote_msg_list = []
    for member in members:
        vote_msg = await interaction.channel.send(f'Where should {member.global_name if member.global_name is not None else member.name} be placed?')
        await vote_msg.add_reaction('🆘')
        indicators = ["s", "a", "b", "c", "d", "e", "f"]
        for i in indicators:
            await vote_msg.add_reaction(lookup("REGIONAL INDICATOR SYMBOL LETTER %s" % i))
        
        vote_msg_list.append(vote_msg)
        
    await asyncio.sleep(5)
    # print(members)
    finalmessage = ""
    for val, vote_msg in enumerate(vote_msg_list):
        # print(members[val])
        vote_msg = await vote_msg.channel.fetch_message(vote_msg.id)
        highest_reaction = ""
        highest_reaction_number = 0
        for reaction in vote_msg.reactions:
            if (reaction.count-1) > highest_reaction_number:
                highest_reaction = reaction.emoji
                highest_reaction_number = reaction.count-1
        finalmessage += f"{members[val].global_name if members[val].global_name is not None else members[val].name} got placed in {highest_reaction} tier with {highest_reaction_number} votes!\n" if highest_reaction_number > 0 else f"{members[val].global_name if members[val].global_name is not None else members[val].name} did not get any votes!\n"
    await interaction.channel.send(finalmessage[0:-1])
    

bot.run(TOKEN)