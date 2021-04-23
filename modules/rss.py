import feedparser
from modules.utils import file_open_json, file_write_json


def contains_wanted(in_str, key_words):
    for key_word in key_words:
        if key_word.lower() in in_str:
            return True
    return False


def fetch_feed():
    rssfile = file_open_json("rss")

    for i in rssfile:
        data = rssfile[i]
        header_name = data["name"]
        feed_url = data["feed_url"]
        hashtags = data["hashtags"]
        keywords = data["keywords"]
        seen_urls = data["seen_urls"]

        feed = feedparser.parse(feed_url)

        for post in feed.entries:
            title = post.title
            url = post.link

            if url not in seen_urls:
                if contains_wanted(title.lower(), keywords):
                    ret_str = f"📰 Nyhetsvarsel fra {header_name}:"
                    ret_str += f"\n{url}"
                    ret_str += f"\n\n{' '.join([str(elem) for elem in hashtags])}"
                    print(ret_str)

                    seen_urls.append(url)
                    file_write_json("rss", rssfile)

                    return ret_str
