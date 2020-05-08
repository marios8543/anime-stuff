from flask import Flask, render_template, request, redirect, jsonify, make_response
from os import listdir, getenv, path
from requests import post
from random import randint

JELLYFIN_DIRECTORY = getenv("JF_DIR")
FLAG_DIRECTORY = getenv("FLAG_DIR")
GOTIFY_URL = getenv("GOTIFY_URL")
BASE_URL = getenv("BASE_URL")

app = Flask(__name__)
pending = {}

class PendingNaming:
    def __init__(self, dl_path):
        self.dl_path = dl_path
        self.id = str(randint(100000, 999999))

    def resolve(self):
        pending.pop(self.id, None)

@app.route("/")
def index():
    return render_template("index.html", pending=[pending[i] for i in pending], BASE_URL=BASE_URL)

@app.route("/<int:id>")
def index_with_id(id):
    id = str(id)
    if id in pending:
        item = pending[id]
        return render_template("resolve.html", item=item, BASE_URL=BASE_URL)
    else:
        return make_response("Pending item not found", 404)

@app.route("/addPending", methods=["POST", "GET"])
def add_pending():
    dl_path = request.args.get("title")
    if not dl_path:
        dl_path = request.form.get("title")
    if not dl_path:
        return make_response("Title not provided", 400)
    p = PendingNaming(dl_path)
    pending[p.id] = p

    url = "{}/{}".format(BASE_URL, p.id)
    post(GOTIFY_URL, json={
        "extras": {
            "client::display": {
                "contentType": "text/markdown"
            },
            "client::android": {
                "autoLink": "web"
            }
        },
        "title": "Intervention needed",
        "message": "[{} could not be named]({})".format(dl_path, url),
        "priority": 9
    })
    return str(p.id)

@app.route("/resolve", methods=["POST"])
def resolve():
    id = request.form.get("id")
    title = request.form.get("title")
    season = request.form.get("season")
    if not id in pending:
        return make_response("Pending item not found", 404)
    item = pending[id]
    with open(path.join(FLAG_DIRECTORY, id), "w+") as f:
        f.write("{0}|{0}|{1}".format(title, season))
    item.resolve()
    return redirect(BASE_URL)

@app.route("/delete/<int:id>", methods=["GET"])
def delete(id):
    id = str(id)
    if not id in pending:
        return make_response("Pending item not found", 404)
    item = pending[id]
    with open(path.join(FLAG_DIRECTORY, id), "w+") as f:
        f.write("delete")
    item.resolve()
    return redirect(BASE_URL)

@app.route("/autocomplete")
def autocomplete():
    dirs = listdir(JELLYFIN_DIRECTORY)
    query = request.args.get("term").lower()
    if len(query) >= 2:
        return jsonify([i for i in dirs if query in i.lower()])
    return jsonify([])


if __name__=='__main__':
    app.run("0.0.0.0", getenv("PORT"))
