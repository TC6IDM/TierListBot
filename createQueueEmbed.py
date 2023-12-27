from ast import List
import datetime
import discord


def createQueueEmbed(interaction: discord.Interaction,res: List,number:int,total_pages: int):
    # print(number)
    # print([f'{v["trackname"][:40]}\n' for v in res[0]["queue"][(number*10)-10:(number*10)]])
    embed=discord.Embed(title=f"🎶 Music Queue 🎶 - Page: {number}/{total_pages}", color=0x00FF00)
    embed.set_author(name=f'{interaction.client.application.name} Music', url="https://github.com/TC6IDM/TierListBot", icon_url=interaction.client.application.icon.url)
    # embed.set_thumbnail(url=queinfo['thumbnail_url']) #technicall does this twice but im too lazy to do it any other way
    embed.add_field(name="Position",value=''.join(map(str, [f'{(k+1)+(number-1)*10}\n' for k,v in enumerate(res[0]["queue"][(number*10)-10:(number*10)])])),inline=True)
    embed.add_field(name="Track",value=''.join(map(str, [f'{v["trackname"][:40]}\n' for v in res[0]["queue"][(number*10)-10:(number*10)]])),inline=True)
    embed.add_field(name="Requested By",value=''.join(map(str, [f'{interaction.client.get_user(v["userid"]).mention}\n' for v in res[0]["queue"][(number*10)-10:(number*10)]])),inline=True)
    # embed.add_field(name="Duration",value=''.join(map(str, [f'{v["duration"][:255]}\n' for v in res[0]["queue"][0:10]])),inline=True)
    # embed.add_field(name=f"{'Track':{track_column_width}}   {'Requested By':<{requested_by_column_width}}   {'Duration':{duration_column_width}}", value= f"{track_info['Track']:{track_column_width}}   {track_info['Requested By']:<{requested_by_column_width}}   {track_info['Duration']}",inline=True)
    embed.set_footer(text=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # view = SimpleView(vc)
    return embed