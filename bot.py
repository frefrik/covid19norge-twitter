import yaml
from datetime import datetime
import modules.c19norge as c19norge
from modules.twitter import create_api
from modules.rss import fhi, regjeringen
from modules.utils import (
    file_open,
    file_write,
    get_messagetext,
    get_datetimestr,
    get_date_yesterday,
)
from modules.graphs import (
    graph_confirmed,
    graph_dead,
    graph_hospitalized,
    graph_tested_lab,
)

with open("./config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

twitter = create_api()
auth = cfg["twitter"]["auth"]
jobs = cfg["twitter"]["jobs"]


def tested():
    data = c19norge.metadata("tested")
    newToday = data.get("newToday")
    total = data.get("total")

    last_data = file_open("tested")

    tested_diff = total - int(last_data)

    if tested_diff > 0:
        messagetext = get_messagetext("tested", tested_diff)

        ret_str = f"🔬 {tested_diff:,} {messagetext}"
        ret_str += f"\nTotalt: {total:,} (Nye i dag: {newToday:,})"
        ret_str += f"\n\nKilde: {jobs['tested']['source']['url']}"

        file_write("tested", total)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")
        twitter.update_status(ret_str)


def confirmed():
    data = c19norge.metadata("confirmed")
    total = data.get("total")
    updated_by = data.get("updated", {}).get("source")

    last_data = file_open("confirmed")

    confirmed_diff = total - int(last_data)

    if confirmed_diff > 0:
        messagetext = get_messagetext("confirmed", confirmed_diff)

        ret_str = f"🦠 {confirmed_diff} {messagetext}"

        if updated_by == "correction_script":
            source = jobs["confirmed"]["source"]["alt_url"]
        else:
            source = jobs["confirmed"]["source"]["url"]

        if datetime.now().hour in range(0, 3):
            newYesterday = data.get("newYesterday")

            ret_str += f"\nTotalt: {total:,} (Nye siste døgn: {newYesterday:,})"
            ret_str += f"\n\nKilde: {source}"
        else:
            newToday = data.get("newToday")

            ret_str += f"\nTotalt: {total:,} (Nye i dag: {newToday:,})"
            ret_str += f"\n\nKilde: {source}"

        file_write("confirmed", total)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")
        twitter.update_status(ret_str)


def dead():
    data = c19norge.metadata("dead")
    total = data.get("total")

    last_data = file_open("dead")

    dead_diff = total - int(last_data)

    if dead_diff > 0:
        newToday = data.get("newToday")

        messagetext = get_messagetext("dead", dead_diff)

        ret_str = f"❗ {dead_diff} {messagetext}"
        ret_str += f"\nTotalt: {total} (Nye i dag: {newToday})"
        ret_str += f"\n\nKilde: {jobs['dead']['source']['url']}"

        file_write("dead", total)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")
        twitter.update_status(ret_str)


def admissions():
    datetimestr = get_datetimestr()
    total = c19norge.metadata("admissions", "total")

    last_data = file_open("admissions")

    diff = total - int(last_data)

    if diff != 0:
        if total == 1:
            messagetext = "innlagt pasient på sykehus"
        else:
            messagetext = "innlagte pasienter på sykehus"

        ret_str = f"🏥 Endring i antall innlagt på sykehus: {diff:+}"
        ret_str += f"\n\nStatus {datetimestr}:"
        ret_str += f"\n{total} {messagetext}"
        ret_str += f"\n\nKilde: {jobs['admissions']['source']['url']}"

        file_write("admissions", total)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")
        twitter.update_status(ret_str)


def respiratory():
    datetimestr = get_datetimestr()
    total = c19norge.metadata("respiratory", "total")

    last_data = file_open("respiratory")

    diff = total - int(last_data)

    if diff != 0:
        if total == 1:
            messagetext = "innlagt pasient som får respiratorbehandling"
        else:
            messagetext = "innlagte pasienter som får respiratorbehandling"

        ret_str = f"😷 Endring i antall innlagt med respiratorbehandling: {diff:+}"
        ret_str += f"\n\nStatus {datetimestr}:"
        ret_str += f"\n{total} {messagetext}"
        ret_str += f"\n\nKilde: {jobs['respiratory']['source']['url']}"

        file_write("respiratory", total)

        print(ret_str, "\n")
        twitter.update_status(ret_str)


def daily_stats():
    # metadata
    tested = c19norge.metadata("tested")
    confirmed = c19norge.metadata("confirmed")
    dead = c19norge.metadata("dead")
    admissions = c19norge.metadata("admissions")
    respiratory = c19norge.metadata("respiratory")

    # totals
    tested_total = tested.get("total")
    confirmed_total = confirmed.get("total")
    dead_total = dead.get("total")
    admissions_total = admissions.get("total")
    respiratory_total = respiratory.get("total")

    # newYesterday
    tested_newYesterday = tested.get("newYesterday", 0)
    confirmed_newYesterday = confirmed.get("newYesterday", 0)
    dead_newYesterday = dead.get("newYesterday", 0)

    # newSince
    confirmed_newSince_d7 = confirmed.get("newSince_d8", 0)
    confirmed_newSince_d14 = confirmed.get("newSince_d15", 0)

    ret_str = f"🔢 Nøkkeltall - {get_date_yesterday()}"

    ret_str += f"\n\n🦠 Smittetilfeller siste døgn: {confirmed_newYesterday:,}"
    ret_str += f"\nSiste 7d: {confirmed_newSince_d7:,}"
    ret_str += f"\nSiste 14d: {confirmed_newSince_d14:,}"
    ret_str += f"\nTotalt: {confirmed_total:,}"

    ret_str += f"\n\n❗ Dødsfall siste døgn: {dead_newYesterday:,}"
    ret_str += f"\nTotalt: {dead_total:,}"

    ret_str += f"\n\n🔬 Testede siste døgn: {tested_newYesterday:,}"
    ret_str += f"\nTotalt: {tested_total:,}"

    ret_str += "\n\n🏥 Pasienter på sykehus"
    ret_str += f"\nInnlagt: {admissions_total:,}"
    ret_str += f"\nTilkoblet respirator: {respiratory_total:,}"

    ret_str += "\n#covid19norge"

    ret_str = ret_str.replace(",", " ")
    print(ret_str, "\n")
    twitter.update_status(ret_str)


def daily_graphs():
    graph_tested_lab()
    graph_confirmed()
    graph_dead()
    graph_hospitalized()

    file_tested_lab = "./graphs/no_tested_lab.png"
    file_confirmed = "./graphs/no_confirmed.png"
    file_dead = "./graphs/no_dead.png"
    file_hospitalized = "./graphs/no_hospitalized.png"

    tested_lab = twitter.media_upload(file_tested_lab)
    confirmed = twitter.media_upload(file_confirmed)
    dead = twitter.media_upload(file_dead)
    hospitalized = twitter.media_upload(file_hospitalized)

    message = "📊 Statistikk - {}".format(get_date_yesterday())
    message += "\n#covid19norge"

    print(message, "\n")
    twitter.update_status(
        message,
        media_ids=[
            tested_lab.media_id,
            confirmed.media_id,
            dead.media_id,
            hospitalized.media_id,
        ],
    )


def rss_fhi():
    feed = fhi()

    if feed:
        twitter.update_status(feed)


def rss_regjeringen():
    feed = regjeringen()

    if feed:
        twitter.update_status(feed)
