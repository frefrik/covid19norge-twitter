import feedparser
from sqlitedict import SqliteDict

db = SqliteDict("./data/rss_database.sqlite", "rss", autocommit=True)

key_words = {
    "fhi": [
        "korona",
        "intensiv",
        "covid",
        "smitte",
        "app",
        "rød",
        "grøn",
        "hurtigrut",
        "utbrudd",
        "karantene",
        "reiser",
    ],
    "regjeringen": ["pressekonferanse"],
}


def select_all():
    for i in db.items():
        print(i)


def contains_wanted(feed, in_str):
    for key_word in key_words[feed]:
        if key_word.lower() in in_str:
            return True

    return False


def fhi():
    feed_url = "https://fhi.no/rss/nyheter/"
    feed = feedparser.parse(feed_url)

    for post in feed.entries:
        title = post.title
        url = post.link

        if post.link in db:
            break

        if contains_wanted("fhi", title.lower()):
            ret_str = "📰 Nyhetsvarsel fra FHI:"
            ret_str += "\n{}".format(title)
            ret_str += "\n{}".format(url)
            ret_str += "\n\n#covid19norge #koronaNorge #fhi"

            db[post.link] = True

        else:
            return None

        return ret_str


def regjeringen():
    feed_url = "https://www.regjeringen.no/no/rss/Rss/2581966/?topic=2692388&documentType=aktuelt/nyheter"
    feed = feedparser.parse(feed_url)

    for post in feed.entries:
        title = post.title
        url = post.link.split("?utm_source")[0]

        if url in db:
            break

        if contains_wanted("regjeringen", title.lower()):
            ret_str = "📰 Nyhetsvarsel fra Regjeringen:"
            ret_str += "\n{}".format(title)
            ret_str += "\n{}".format(url)
            ret_str += "\n\n#covid19norge #koronaNorge #regjeringen"

            db[url] = True

        else:
            return None

        return ret_str
