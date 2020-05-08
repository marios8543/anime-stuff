from aiohttp import ClientSession
from os import getenv
from Downloader import QB_URL, login_qb, web
from asyncio import sleep
import logging

notif_web = ClientSession()
URL = getenv("gotify_url")
downloading = {}

async def _send_notification(title,message):
    if not URL:
        logging.debug("Ignoring notification push because gotify url not set")
        return
    res = await notif_web.post(URL, data={
        "title": title,
        "message": message
    })
    if res.status == 200:
        return 1
    else:
        logging.warn("Could not push notification ({}: {})".format(res.status, await res.text()))

async def send_anime_notification(anime):
    logging.info("Finished downloading episode {} of {}".format(anime.last_episode, anime.title))
    title = anime.title
    message = "Episode {} has finished downloading".format(anime.last_episode)
    return await _send_notification(title, message)

async def dl_watchdog():
    await login_qb(client=web)
    logging.info("Starting download watchdog")
    while True:
        try:
            res = await web.get(QB_URL+"/query/torrents",params={'filter':'downloading', 'category':'Anime'})
            if res.status==200:
                res = await res.json()
                hashes = [i['hash'] for i in res]
                for i in downloading:
                    if i not in hashes:
                        anime = downloading.pop(i,None)
                        await send_anime_notification(anime)
            else:
                logging.warn("Something went wrong with fetching downloads ({}: {})".format(res.status,await res.text()))
        except Exception as e:
            logging.error(str(e))
            continue
        finally:
            await sleep(5)