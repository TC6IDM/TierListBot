import io
from discord import TextChannel, File, TextChannel, User
import discord
from PIL import Image


async def createlist(channel: TextChannel, vote_msg_list: list[int], members: list[User]):
    '''
    Creates a tier list based on the votes and sends it to the channel
    
    :param channel: 
        discord channel object
    :param vote_msg_list: 
        list of message ids that correspond to the vote messages
    :param members: 
        list of member objects
    '''

    file_path = 'tierlist.png'
    image = Image.open(file_path)
    # IMAGE_WIDTH = image.size[0]
    IMAGE_HEIGHT = image.size[1]
    AVATAR_SIZE = int(IMAGE_HEIGHT/8)
    
    #the teir is the key, the value is a list of the original x position and the y position fraction relative to the image height
    distances = {"🆘": [125,1/8], "🇸": [125,2/8], "🇦": [125,3/8], "🇧": [125,4/8], "🇨": [125,5/8], "🇩": [125,6/8], "🇪": [125,7/8], "🇫": [125,8/8]}
    
    
    fulldebugstatement = f"Server: {channel.guild.name} - {channel.name}\n"
    
    
    #numerate through the members and vote messages
    for val, vote_msg in enumerate(vote_msg_list):
        try:
            vote_msg = await channel.fetch_message(vote_msg)
        except discord.errors.NotFound:
            await channel.send("Error fetching tier list messages, some retard probably deleted them.",delete_after=10)
            return
        
        #iterates over reactions and finds the one with the highest count
        highest_reaction = ""
        highest_reaction_number = 0
        
        fulldebugstatement+= f"{members[val].display_name}: "
        
        for reaction in vote_msg.reactions:
            fulldebugstatement+= f"{reaction.emoji}: {reaction.count-1}, "
            if (reaction.count-1) > highest_reaction_number:
                highest_reaction = reaction.emoji
                highest_reaction_number = reaction.count-1

        #if no one voted for this person, put them in the F tier
        highest_reaction = highest_reaction if highest_reaction != "" else "🇫"
        fulldebugstatement+= f"\n{members[val].display_name}: {highest_reaction}\n"
        ## code to fuck over david
        # davidsid = 382271649724104705
        # highest_reaction = "🆘" if members[val].id == davidsid else highest_reaction
        
        #find the avatar of the person
        avatar_asset = members[val].display_avatar if members[val].display_avatar is not None else members[val].default_avatar
        buffer_avatar = io.BytesIO()
        await avatar_asset.save(buffer_avatar)
        buffer_avatar.seek(0)
        avatar_image = Image.open(buffer_avatar)
        avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) # 
        
        #paste the avatar onto the image, X position is the original x position + the number of avatars already in that tier * the avatar size, the Y position corresponds to the height of the tier - the avatar size
        image.paste(avatar_image, (int(distances[highest_reaction][0]), int(IMAGE_HEIGHT*distances[highest_reaction][1] - AVATAR_SIZE)))
        distances[highest_reaction][0] += AVATAR_SIZE #move the next avatar over

        #save the image
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')    
        buffer_output.seek(0)

    print(fulldebugstatement)
    # send image
    await channel.send(file=File(buffer_output, 'myimage.png'))
   