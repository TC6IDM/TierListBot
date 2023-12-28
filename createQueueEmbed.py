from ast import List
import datetime
import discord


def createQueueEmbed(interaction: discord.Interaction,res: List,number:int,total_pages: int) -> discord.Embed:
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
        
    :rtype discord.Embed:
    :returns:
        the embed object
    '''
    
    embed=discord.Embed(title=f"🎶 Music Queue 🎶 - Page: {number}/{total_pages}", color=0x00FF00)
    embed.set_author(name=f'{interaction.client.application.name} Music', url="https://github.com/TC6IDM/TierListBot", icon_url=interaction.client.application.icon.url)
    embed.add_field(name="Position",value=''.join(map(str, [f'{(k+1)+(number-1)*10}\n' for k,v in enumerate(res[0]["queue"][(number*10)-10:(number*10)])])),inline=True)
    embed.add_field(name="Track",value=''.join(map(str, [f'{v["trackname"][:40]}\n' for v in res[0]["queue"][(number*10)-10:(number*10)]])),inline=True)
    embed.add_field(name="Requested By",value=''.join(map(str, [f'{interaction.client.get_user(v["userid"]).mention}\n' for v in res[0]["queue"][(number*10)-10:(number*10)]])),inline=True)
    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return embed