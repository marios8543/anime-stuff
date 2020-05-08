#!/usr/bin/env python3

from requests import post
from datetime import datetime
from sys import argv

BASE_URL = "https://graphql.anilist.co"

class BaseShowNotInList(Exception):
    def __init__(self, items):
        self.items = items
        super().__init__("Base show not in sequel/prequel list.")

class SortableAnime:
    def __init__(self, id, year, month, day, reltype, title, frmt):
        self.id = id
        self.timestamp = datetime(year if year else 9999, month if month else 12, day if day else 28)
        self.type = reltype
        self.frmt = frmt
        self.title = title

    def dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.strftime("%d-%m-%Y"),
            "type": self.type,
            "title":  self.title,
            "format": self.frmt
        }

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.title)


def search(query):
    response = post(BASE_URL, json={
        'query': """
            query ($q: String) {
                Media (search: $q) {
                    id
                }
            }
        """,
        'variables': {"q": query}
    })
    if response.ok:
        return response.json()["data"]["Media"]["id"]
    raise ValueError("Show does not exist")

def get_show(id):
    response = post(BASE_URL, json={
        'query': """
            query ($id: Int) {
                Media (id: $id) {
                    id
                    title {
                        english
                        romaji
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    format
                    relations {
                        nodes {
                            id
                            format
                            startDate {
                                year
                                month
                                day
                            }
                            title {
                                english
                                romaji
                            }
                        }
                        edges{
                            relationType
                        }
                    }
                }
            }
        """,
        'variables': {"id": id}
    })
    if response.ok:
        return response.json()
    raise ValueError("Bad show")

def get_base_show(res):
    base = res["data"]["Media"]
    return SortableAnime(base["id"], base["startDate"]["year"], base["startDate"]["month"], base["startDate"]["day"], "BASE", base["title"], base["format"])

def process_shows(res):
    ls = []
    ls.append(get_base_show(res))
    for i,v in enumerate(res["data"]["Media"]["relations"]["nodes"]):
        ls.append(SortableAnime(v["id"], v["startDate"]["year"], v["startDate"]["month"], v["startDate"]["day"], res["data"]["Media"]["relations"]["edges"][i]["relationType"], v["title"], v["format"]))
        pass
    return ls

def main(query):
    items = []
    show_id = search(query)
    res = get_show(show_id)
    items.extend(process_shows(res))
    base_show = get_base_show(res)

    if "PREQUEL" not in [i.type for i in items]:
        season = 1
        final_items = items
    else:
        ignore = []
        while True:
            f = False
            for i in items:
                if i.type == "PREQUEL" and i not in ignore:
                    fi = [i for i in process_shows(get_show(i.id)) if i not in items]
                    items.extend(fi)
                    ignore.append(i)
                    f = True
            if not f:
                break
        final_items = [i for i in items if i.frmt == "TV" and (i.type == "PREQUEL" or i.type == "SEQUEL" or i.type == "BASE")]
        if not base_show in final_items:
            final_items = [i for i in items if (i.type == "PREQUEL" or i.type == "SEQUEL" or i.type == "BASE")]
        final_items.sort(key=lambda i: i.timestamp)
        if base_show in final_items:
            season = final_items.index(base_show) + 1
        else:
            raise BaseShowNotInList(final_items)
    return season, base_show, final_items

if __name__ == "__main__":
    season, show, items = main(argv[1])
    base_title = items[0].title
    print("{}|{}|{}".format(base_title["romaji"], base_title["english"], season))
