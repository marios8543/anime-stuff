from Animebyter import get_airing
from asyncio import sleep, Queue, get_event_loop
from aiohttp import ClientSession
from pickledb import PickleDB
import logging
import os

INTERVAL = int(os.getenv("interval","5"))
web = ClientSession()
QB_URL = os.getenv("qbit_url")
store = PickleDB(os.getenv("database"), True, False)
dl_queue = Queue()
loop = get_event_loop()

if not store.exists("watching"):
    store.lcreate("watching")
if not store.exists("qbUser"):
    store.set("qbUser", "")
if not store.exists("qbPass"):
    store.set("qbPass", "")

class qbLoginException(Exception):
    pass

class NotLoggedInException(Exception):
    pass

class DownloadableItem:
    def __init__(self,anime):
        self.anime = anime

    def complete(self):
        watching = store.get("watching")
        for v in watching:
            if v['id'] == self.anime.id:
                store.lremvalue("watching",v)
                v["last_episode"] = self.anime.last_episode
                store.ladd("watching",v)
                return


async def login_qb(username=store.get("qbUser"),password=store.get("qbPass"), client=web):
    async with client.post(QB_URL+'/login',data={'username':username,'password':password}) as res:
        if res.status!=200:
            raise qbLoginException(await res.text())
        else:
            logging.info("Logged into qBittorrent")

async def add_anime_torrent(anime):
    logging.info("Adding episode {} of {}".format(anime.last_episode,anime.title))
    path = os.path.join(store.get('downloadPath'),anime.title)
    async with web.post(QB_URL+'/command/download',data={'urls':anime.torrent_link,'savepath':path,'category':store.get("downloadLabel")}) as res:
        if res.status==200:
            return 1
        elif res.status==403:
            raise NotLoggedInException()
        else:
            raise Exception(await res.text())

async def get_last_added():
    async with web.get(QB_URL+"/query/torrents",params={"category":"Anime","sort":"added_on","reverse":"true"}) as res:
        if res.status==200:
            res = await res.json()
            return res[0]

from Notifications import downloading
async def add_to_download_list(anime):
    last = await get_last_added()
    if last:
        downloading[last["hash"]] = anime

async def downloader():
    logging.info("Starting downloader")
    while True:
        item = await dl_queue.get()
        while True:
            try:
                await add_anime_torrent(item.anime)
                await add_to_download_list(item.anime)
                item.complete()
                logging.info("Added episode {} of {}".format(item.anime.last_episode,item.anime.title))
                break
            except NotLoggedInException:
                while True:
                    try:
                        await login_qb()
                        break
                    except Exception as e:
                        logging.warn("Could not log into qBittorrent ({})".format(str(e)))
                        await sleep(5)
                        continue
                continue
            except Exception as e:
                logging.error(str(e))
                await sleep(3)

async def checker():
    logging.info("Starting new episode checker")
    while True:
        try:
            logging.debug("Checking for new episodes")
            airing = await get_airing()
            watching = store.get("watching")
            for air in airing:
                for watch in watching:
                    if air.id == watch['id'] and air.resolution == watch["resolution"]:
                        if air.last_episode > watch['last_episode']:
                            logging.debug("Attempting to add episode {} of {}".format(air.last_episode,air.title))
                            item = DownloadableItem(air)
                            await dl_queue.put(item)
        except Exception as e:
            logging.error(str(e))
            continue
        finally:
            await sleep(INTERVAL)
