import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
from discord import File
import discord
import yt_dlp
import os
async def createlist(channel, vote_msg_list, members):
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
        vote_msg = await channel.fetch_message(vote_msg)
        highest_reaction = ""
        highest_reaction_number = 0
        for reaction in vote_msg.reactions:
            if (reaction.count-1) > highest_reaction_number:
                highest_reaction = reaction.emoji
                highest_reaction_number = reaction.count-1
        # finalmessage += f"{members[val].global_name if members[val].global_name is not None else members[val].name} got placed in {highest_reaction} tier with {highest_reaction_number} votes!\n" if highest_reaction_number > 0 else f"{members[val].global_name if members[val].global_name is not None else members[val].name} did not get any votes!\n" 
        
        #if no one voted for this person, put them in the F tier
        highest_reaction = highest_reaction if highest_reaction != "" else "🇫"
        
        davidsid = 382271649724104705
        highest_reaction = "🆘" if members[val].id == davidsid else highest_reaction # fuck you david
        
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


async def downloadAndPlay(interaction, videourl,uservoice):
        await interaction.channel.send(f"Playing {videourl}")
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
            'outtmpl': '/vids/'+str(interaction.guild.id)+'.%(ext)s', #save songs here .%(ext)s

            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'cookiefile': COOKIE_FILE, #cookies for downloading age restricted videos
            }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(videourl)
        
        # create StreamPlayer
        if uservoice.channel is None:
            await interaction.response.send_message(f"you're not in a voice channel retard", ephemeral = True)
            return
        vc = await uservoice.channel.connect()
        while not os.path.exists(f'vids/{interaction.guild.id}.webm'):
            await asyncio.sleep(1)
        vc.play(discord.FFmpegPCMAudio(f'vids/{interaction.guild.id}.webm'), after=lambda e: print('done', e))
        # player = vc.create_ffmpeg_player('vuvuzela.webm', after=lambda: print('done'))
        # print(vc.is_playing())
        while vc.is_playing():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        vc.stop()
        await vc.disconnect(force = True)
        os.remove(f'vids/{interaction.guild.id}.webm')
        
        # await interaction.channel.send(s.results[ints[0]].watch_url)