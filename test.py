import requests
import yt_dlp
from debug import debug

from songUtil import COOKIE_FILE, download


# def video_duration_to_seconds(duration_string):
#     components = duration_string.split(':')

#     if len(components) == 3: hours, minutes, seconds = map(int, components)
#     elif len(components) == 2: hours, minutes, seconds = 0, int(components[0]), int(components[1])
#     elif len(components) == 1: hours, minutes, seconds = 0, 0, int(components[0])
#     else: hours, minutes, seconds = 0, 0, 0  # Invalid format

#     total_seconds = hours * 3600 + minutes * 60 + seconds
#     return total_seconds

# Examples:
# duration_string_1 = "1:00:01"
# duration_string_2 = "2:56"
# duration_string_3 = "0:03"

# total_seconds_1 = video_duration_to_seconds(duration_string_1)
# total_seconds_2 = video_duration_to_seconds(duration_string_2)
# total_seconds_3 = video_duration_to_seconds(duration_string_3)

# print("Total duration in seconds (Example 1):", total_seconds_1)
# print("Total duration in seconds (Example 2):", total_seconds_2)
# print("Total duration in seconds (Example 3):", total_seconds_3)

# print(requests.get('https://www.youtube.com/playlist?list=PLQylghHje1b94Yfl5fx8ZHbN99K7gH1xz'))

# res = [
#     {"videourl": "https://youtube.com/watch?v=9Bx76EQZIew", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/9Bx76EQZIew/maxresdefault.jpg", "trackname": "Violent Crimes by Kanye West but it will change your life (ReUpload)", "duration": "8:52", "output": "C:/Users/Owner/Desktop/TierListBot/TierListBot/vids/523271445376401408.webm"}, 
#     {"videourl": "https://youtube.com/watch?v=w7hcMmC7I30", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/w7hcMmC7I30/maxresdefault.jpg", "trackname": "A$AP Rocky, Clams Casino - Demons x I'm God (Lyrics) \"I smoked away my brain\"", "duration": "3:12", "output": "/vids/523271445376401408_queue/0.webm"}, 
#     {"videourl": "https://youtube.com/watch?v=dQAsaY0pKhI", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/dQAsaY0pKhI/maxresdefault.jpg", "trackname": "Kanye West - Ghost Town but it will make you ascend to the fourth dimension", "duration": "8:46", "output": "/vids/523271445376401408_queue/1.webm"}, {"videourl": "https://youtube.com/watch?v=r6Zpd6AmBAk", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/r6Zpd6AmBAk/maxresdefault.jpg", "trackname": "unreleased kanye west songs that will take your soul to another dimension", "duration": "29:11", "output": "/vids/523271445376401408_queue/2.webm"}, {"videourl": "https://youtube.com/watch?v=Ml2qYfCnFMY", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/Ml2qYfCnFMY/maxresdefault.jpg", "trackname": "Follow God by Ye but it will change your life", "duration": "6:48", "output": "/vids/523271445376401408_queue/3.webm"}, {"videourl": "https://youtube.com/watch?v=ce17Ui_eqJ4", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/ce17Ui_eqJ4/maxresdefault.jpg", "trackname": "kanye - off the grid [HOLY x NARCISSIST GUITAR]", "duration": "8:26", "output": "/vids/523271445376401408_queue/4.webm"}, {"videourl": "https://youtube.com/watch?v=D5Gdu74lA80", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/D5Gdu74lA80/maxresdefault.jpg", "trackname": "Kanye West - Bittersweet Poetry (ft. John Mayer) [Graduation Bonus Track]", "duration": "4:03", "output": "/vids/523271445376401408_queue/5.webm"}, {"videourl": "https://youtube.com/watch?v=BflAl_n90Ow", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/BflAl_n90Ow/maxresdefault.jpg", "trackname": "Kanye West - Can u be feat. Travis Scott [V2]", "duration": "6:31", "output": "/vids/523271445376401408_queue/6.webm"}, {"videourl": "https://youtube.com/watch?v=BxtQ950i0N8", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/BxtQ950i0N8/maxresdefault.jpg", "trackname": "Frank Ocean - American Wedding", "duration": "5:00", "output": "/vids/523271445376401408_queue/7.webm"}, {"videourl": "https://youtube.com/watch?v=FK63kqgGCFQ", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/FK63kqgGCFQ/maxresdefault.jpg", "trackname": "KANYE WEST // CAN U BE // AS ACCURATE AS HUMANLY POSSIBLE", "duration": "2:12", "output": "/vids/523271445376401408_queue/8.webm"}, {"videourl": "https://youtube.com/watch?v=GIZGRE1FXWo", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/GIZGRE1FXWo/maxresdefault.jpg", "trackname": "Kanye West - Can you be (feat Travis Scott) (Leak)", "duration": "3:23", "output": "/vids/523271445376401408_queue/9.webm"}, {"videourl": "https://youtube.com/watch?v=V6k9jlIbt98", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/V6k9jlIbt98/maxresdefault.jpg", "trackname": "kanye west - can u be (best quality)", "duration": "2:25", "output": "/vids/523271445376401408_queue/10.webm"}, {"videourl": "https://youtube.com/watch?v=fR1c8Qw3wEA", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/fR1c8Qw3wEA/maxresdefault.jpg", "trackname": "Kanye West - Mama's Boyfriend", "duration": "3:38", "output": "/vids/523271445376401408_queue/11.webm"}, {"videourl": "https://youtube.com/watch?v=lsZRoypKIX8", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/lsZRoypKIX8/maxresdefault.jpg", "trackname": "White Dress", "duration": "3:36", "output": "/vids/523271445376401408_queue/12.webm"}, {"videourl": "https://youtube.com/watch?v=vN-wSNqVnwg", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/vN-wSNqVnwg/maxresdefault.jpg", "trackname": "Kanye West - Security (Best version)", "duration": "2:09", "output": "/vids/523271445376401408_queue/13.webm"}, {"videourl": "https://youtube.com/watch?v=FJAHJUu-9YQ", "userid": 281911981089226762, "thumbnail_url": "https://img.youtube.com/vi/FJAHJUu-9YQ/maxresdefault.jpg", "trackname": "A$AP Rocky - Demons x I'm God (Prod. Clams Casino)", "duration": "3:13", "output": "/vids/523271445376401408_queue/14.webm"}]
# number = 1

# print([f'{v["trackname"][:40]}\n' for v in res[(number*10)-10:(number*10)]])

from ytmusicapi import YTMusic

from ytdlpUtil import MyLogger, my_hook

# yt = YTMusic()
# # playlistId = yt.create_playlist('test', 'test description')
# search_results = yt.search('Oasis Wonderwall')
# # yt.add_playlist_items(playlistId, [search_results[0]['videoId']])

# debug(search_results)
# ydl_opts = {
#         'format': 'webm/bestaudio/best',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'webm',
#             'preferredquality': '320',#highest quality
#         },{
#             'key': 'FFmpegMetadata',
#             'add_metadata': True,
#         }],
#         'ignoreerrors': True, #ignore errors
#         'outtmpl': 'vids/test.webm', #save songs here .%(ext)s
#         'logger': MyLogger(),
#         'progress_hooks': [my_hook],
#         'cookiefile': COOKIE_FILE, #cookies for downloading age restricted videos
#         }
    
# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     ydl.download("https://www.youtube.com/watch?v=JqTK_1LReXc&ab_channel=ISAB")

import os
import shutil
import datetime

# now = str(datetime.datetime.now())[:19]
# now = now.replace(":","_")
file_names = [fn for fn in os.listdir("C:\\Users\\Owner\\Desktop\\lethal company mods\\LethalAudioFiles2\\Lethal Company\\ExportedProject\\Assets\\AudioClip")
              if (fn.endswith(".wav") or fn.endswith(".ogg"))]
print(file_names)
# os.listdir()
src_dir="D:\\Downloads\\THUD.wav"
for i,v in enumerate(file_names):
    dst_dir=f'C:\\Users\\Owner\\Desktop\\lethal company mods\\VineThud\\BepInEx\\plugins\\CustomSounds\\VineThud\\{v.replace(".ogg",".wav")}'
    print(i+1,v)
    shutil.copy(src_dir,dst_dir)

