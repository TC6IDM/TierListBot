import random
from debug import debug
from pytube import YouTube


class YoutubeSearchCustom():
    length: str
    vidlength: str
    length_seconds: int
    title: str
    viewCountText: str
    watch_url: str
    thumbnail_url: str
    
    def __init__(self, obj):
        self.obj = obj
        if type(obj) == dict:
            # debug(obj, f'{random.randint(1,500000)}.json') 
            self.length = obj['duration'] #find a way to convert this to hours minutes and seconds
            self.vidlength = obj['duration']
            self.length_seconds = obj['duration_seconds']
            self.title = f"{obj['title']} - {obj['artists'][0]['name']} - {('(explicit)' if obj['isExplicit'] else '(clean)')}"
            self.viewCountText = 'explicit' if obj['isExplicit'] else 'clean'
            self.watch_url = f"https://music.youtube.com/watch?v={obj['videoId']}"
            self.thumbnail_url = obj['thumbnails'][0]['url']
            
            # "length": "8 minutes, 8 seconds",
            # "vidlength": "8:08",
            # "length_seconds": 488,
            # "title": "Australia v Pakistan 2023-24 | Second Test | Day 4",
            # "viewCountText": "1,416,706 views",
            # "watch_url": "https://youtube.com/watch?v=SvKSwOIyIpw",
            # "thumbnail_url": "https://img.youtube.com/vi/SvKSwOIyIpw/maxresdefault.jpg",
            
        elif type(obj) == YouTube:
            self.length = obj.length
            self.vidlength = obj.vidlength
            self.length_seconds = obj.length_seconds
            self.title = obj.title
            self.viewCountText = obj.viewCountText
            self.watch_url = obj.watch_url
            self.thumbnail_url = obj.thumbnail_url
            
        # debug(self.obj, 'YoutubeSearchCustomList.json') 
            
            
        