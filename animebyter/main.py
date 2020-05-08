from quart import Quart, request, make_response, render_template, redirect
from Animebyter import get_airing
from Downloader import downloader, store, login_qb, qbLoginException, checker
from Notifications import dl_watchdog
from asyncio import get_event_loop,gather
import os
from sys import stdout
import logging

logging.basicConfig(level=logging.DEBUG)
app = Quart(__name__,"/static")
base_url = os.getenv("base_url")

class LastAiring:
    airing = []
    def get(self):
        return self.airing
    def sett(self,a):
        self.airing = a
last_airing = LastAiring()

class FakeObj:
    def __init__(self,dc):
        for i in dc.keys():
            setattr(self,i,dc[i])

@app.route("/")
async def home():
    airing = await get_airing()
    last_airing.sett(airing)
    watching = store.get("watching")
    dl_path = store.get("downloadPath")
    dl_label = store.get("downloadLabel")
    return await render_template('index.html', airing=airing, watching=[FakeObj(i) for i in watching], dl_path=dl_path, dl_label=dl_label)

@app.route("/addAnime")
async def add_show():
    id = request.args.get("id")
    la = last_airing.get()
    show = None
    for i in la:
        if i.id == id:
            show = i
            break
    if show:
        show.last_episode -=1
        store.ladd("watching",vars(show))
        return redirect(base_url)
    else:
        return await render_template("error.html", message="Show does not exist", base_url=base_url)

@app.route("/removeAnime")
async def remove_show():
    id = request.args.get("id")
    watching = store.get("watching")
    for i in watching:
        if id == i['id']:
            store.lremvalue("watching",i)
            return redirect(base_url)
    return await render_template("error.html",message="Show does not exist", base_url=base_url)

@app.route("/updatePath", methods=["POST"])
async def set_path():
    path = (await request.form).get("path")
    if os.path.isdir(path):
        store.set("downloadPath", path)
        return redirect(base_url)
    else:
        return await render_template("error.html", message="{} is not a valid path".format(path))

@app.route("/updateLabel", methods=["POST"])
async def set_label():
    label = (await request.form).get("label")
    store.set("downloadLabel", label)
    return redirect(base_url)

@app.route("/updateCreds", methods=["POST"])
async def update_creds():
    form = await request.form
    username = form.get("user")
    password = form.get("password")
    try:
        await login_qb(username, password)
        store.set("qbUser", username)
        store.set("qbPass", password)
        return redirect(base_url)
    except qbLoginException:
        return await render_template("error.html", message="Invalid credentials. Try again", base_url=base_url)


if __name__ == '__main__':
    server_task = app.run_task("0.0.0.0")
    loop = get_event_loop()

    loop.run_until_complete(gather(server_task,downloader(),checker(),dl_watchdog()))
