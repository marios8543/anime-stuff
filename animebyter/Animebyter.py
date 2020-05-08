from aiohttp import ClientSession
from feedparser import parse
from os import getenv
from json import dumps
import logging
import hashlib

web = ClientSession()

class Anime:
    def __eq__(self,other):
        return self.title == other.title
    def __hash__(self):
        return hash(self.title)
    
    def __init__(self,name,le,tl,res):
        self.title = name.replace("/","-")
        self.last_episode = le
        self.torrent_link = tl
        self.resolution = res.strip()
        self.id = str(int(hashlib.sha256(self.title.encode('utf-8')).hexdigest(), 16) % 10**8)

async def get_airing():
    r = []
    async with web.get("https://animebytes.tv/feed/rss_torrents_airing_anime/{}".format(getenv("ab_key"))) as res:
        if res.status==200:
            txt = await res.text()
            rss = parse(txt)
            for i in rss['entries']:
                try:
                    title = i['ab_grouptitle']
                    ep = int((''.join(x for x in i['ab_torrentproperty'].split("|")[6] if x.isdigit())).strip())
                    link = i['link']
                    r.append(Anime(title,ep,link,i['ab_torrentproperty'].split("|")[3]))
                except Exception as e:
                    logging.error(str(e))
        return r