import yaml
from datetime import datetime
import modules.c19norge as c19norge
from modules.twitter import create_api
from modules.rss import fetch_feed
from modules.utils import (
    file_open,
    file_write,
    get_messagetext,
    get_date_yesterday,
    file_open_json,
    file_write_json,
)
from modules.graphs import (
    graph_confirmed,
    graph_dead,
    graph_hospitalized,
    graph_tested_lab,
    graph_vaccine,
    graph_smittestopp,
)

with open("./config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

twitter = create_api()
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


def tested_lab():
    source_url = jobs["tested_lab"]["source"]["url"]

    curr_data = c19norge.timeseries("tested_lab")[-1]
    curr_total = curr_data.get("total")

    last_data = file_open_json("tested_lab")
    last_total = last_data.get("total")

    if curr_total - last_total > 0:
        graph_tested_lab()

        ret_str = "🔬 Antall testet (Laboratoriedata)"
        ret_str += "\nAntall personer testet og andelen positive blant disse i Norge siden epidemiens start."
        ret_str += "\nEn ny test på en person defineres som en test utført minst 7 dager etter forrige test av samme person."
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("tested_lab", curr_data)

        print(ret_str, "\n")

        file_tested_lab = "./graphs/no_tested_lab.png"
        tested_lab_graph = twitter.media_upload(file_tested_lab)

        twitter.update_status(ret_str, media_ids=[tested_lab_graph.media_id])


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


def confirmed_by_testdate():
    source_url = jobs["confirmed_by_testdate"]["source"]["url"]
    data = c19norge.timeseries("confirmed")

    curr_data = list(filter(lambda x: x["source"] == "fhi:git", data))[-1]
    curr_total = curr_data.get("total")

    last_data = file_open_json("confirmed_by_testdate")
    last_total = last_data.get("total")

    if curr_total - last_total > 0:
        graph_confirmed()

        ret_str = f"🦠 Antall meldte smittetilfeller"

        ret_str += "\nAntall meldte COVID-19 tilfeller etter prøvetakingsdato."
        ret_str += "\nDet er 1-2 dagers forsinkelse i tiden fra diagnose til registrering i MSIS."
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("confirmed_by_testdate", curr_data)

        print(ret_str, "\n")
        file_confirmed = "./graphs/no_confirmed.png"
        confirmed_graph = twitter.media_upload(file_confirmed)

        twitter.update_status(ret_str, media_ids=[confirmed_graph.media_id])


def dead():
    source_url = jobs["dead"]["source"]["url"]

    curr_data = c19norge.timeseries("dead")[-1]
    curr_total = curr_data.get("total")

    last_data = file_open_json("dead")
    last_total = last_data.get("total")

    diff_dead = curr_total - last_total

    if diff_dead > 0:
        graph_dead()
        messagetext = get_messagetext("dead", diff_dead)
        curr_new_today = curr_data.get("new")

        ret_str = "❗ COVID-19 assosierte dødsfall\n"
        ret_str += f"\n{diff_dead} {messagetext}"

        ret_str += f"\nTotalt: {curr_total:,} (Nye i dag: {curr_new_today:,})"
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("dead", curr_data)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")

        file_dead = "./graphs/no_dead.png"
        dead_graph = twitter.media_upload(file_dead)

        twitter.update_status(ret_str, media_ids=[dead_graph.media_id])


def hospitalized():
    source_url = jobs["hospitalized"]["source"]["url"]

    curr_data = c19norge.timeseries("hospitalized")[-1]
    curr_respiratory = int(curr_data.get("respiratory"))
    curr_admissions = int(curr_data.get("admissions"))
    curr_icu = int(curr_data.get("icu"))

    last_data = file_open_json("hospitalized")
    last_respiratory = int(last_data.get("respiratory"))
    last_admissions = int(last_data.get("admissions"))
    last_icu = int(last_data.get("icu"))

    if (
        curr_admissions != last_admissions
        or curr_respiratory != last_respiratory
        or curr_icu != last_icu
    ):
        graph_hospitalized()
        diff_admissions = curr_admissions - last_admissions
        diff_respiratory = curr_respiratory - last_respiratory
        diff_icu = curr_icu - last_icu
        respiratory_pct = curr_respiratory / curr_admissions
        icu_pct = curr_icu / curr_admissions

        ret_str = "🏥 Innlagte pasienter på sykehus\n"

        if diff_admissions != 0:
            ret_str += f"\nEndring i antall innlagte: {diff_admissions:+,}"

        if diff_icu != 0:
            ret_str += f"\nEndring i antall på intensivavdeling: {diff_icu:+,}"

        if diff_respiratory != 0:
            ret_str += f"\nEndring i antall på respirator: {diff_respiratory:+,}"

        ret_str += f"\n\n{curr_admissions:,} er innlagt på sykehus"
        ret_str += f"\n{curr_icu:,} er innlagt på intensivavdeling ({icu_pct:.01%})"
        ret_str += f"\n{curr_respiratory:,} er på respirator ({respiratory_pct:.01%})"

        ret_str += f"\n\nKilde: {source_url}"

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")

        file_write_json("hospitalized", curr_data)

        file_hospitalized = "./graphs/no_hospitalized.png"
        hospitalized_graph = twitter.media_upload(file_hospitalized)

        twitter.update_status(ret_str, media_ids=[hospitalized_graph.media_id])


def vaccine_doses():
    population = 5391369
    source_url = jobs["vaccine"]["source"]["url"]
    data = c19norge.timeseries("vaccine_doses")

    curr_data = list(filter(lambda x: x["granularity_geo"] == "nation", data))[-1]
    curr_total_doses = curr_data.get("total_doses")

    last_data = file_open_json("vaccine_doses")
    last_total_doses = last_data.get("total_doses")

    diff_total_doses = curr_total_doses - last_total_doses

    if diff_total_doses > 0:
        graph_vaccine()
        curr_total_dose_1 = curr_data.get("total_dose_1")
        curr_total_dose_2 = curr_data.get("total_dose_2")
        curr_total_dose_3 = curr_data.get("total_dose_3")

        last_total_dose_1 = last_data.get("total_dose_1")
        last_total_dose_2 = last_data.get("total_dose_2")
        last_total_dose_3 = last_data.get("total_dose_3")

        diff_total_dose_1 = curr_total_dose_1 - last_total_dose_1
        diff_total_dose_2 = curr_total_dose_2 - last_total_dose_2
        diff_total_dose_3 = curr_total_dose_3 - last_total_dose_3

        curr_total_dose_1_pct = curr_total_dose_1 / population
        curr_total_dose_2_pct = curr_total_dose_2 / population
        curr_total_dose_3_pct = curr_total_dose_3 / population

        ret_str = "💉 Antall vaksinerte\n"

        if diff_total_dose_1 != 0:
            ret_str += f"\n{diff_total_dose_1:,} nye personer vaksinert med 1. dose"

        if diff_total_dose_2 != 0:
            ret_str += f"\n{diff_total_dose_2:,} nye personer fullvaksinert"

        if diff_total_dose_3 != 0:
            ret_str += f"\n{diff_total_dose_3:,} nye personer vaksinert med 3. dose"

        ret_str += "\n\nTotal andel"
        ret_str += (
            f"\nDose 1: {curr_total_dose_1_pct:,.02%} ({curr_total_dose_1:,} pers)"
        )
        ret_str += (
            f"\nDose 2: {curr_total_dose_2_pct:,.02%} ({curr_total_dose_2:,} pers)"
        )
        ret_str += (
            f"\nDose 3: {curr_total_dose_3_pct:,.02%} ({curr_total_dose_3:,} pers)"
        )
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("vaccine_doses", curr_data)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")

        file_vaccine_doses = "./graphs/no_vaccine_doses.png"
        vaccine_graph = twitter.media_upload(file_vaccine_doses)

        twitter.update_status(ret_str, media_ids=[vaccine_graph.media_id])


def smittestopp():
    source_url = jobs["smittestopp"]["source"]["url"]

    curr_data = c19norge.timeseries("smittestopp")[-1]
    curr_total_downloads = int(curr_data.get("total_downloads"))
    curr_total_reported = int(curr_data.get("total_reported"))

    last_data = file_open_json("smittestopp")
    last_total_downloads = int(last_data.get("total_downloads"))
    last_total_reported = int(last_data.get("total_reported"))

    if (
        curr_total_downloads != last_total_downloads
        or curr_total_reported != last_total_reported
    ):
        graph_smittestopp()
        new_downloads = int(curr_data.get("new_downloads"))
        new_reported = int(curr_data.get("new_reported"))

        if new_downloads == 1:
            new_downloads_text = "ny nedlasting"
        else:
            new_downloads_text = "nye nedlastinger"

        if new_reported == 1:
            new_reported_text = "ny person meldt smittet i appen"
        else:
            new_reported_text = "nye personer meldt smittet i appen"

        ret_str = "📱 Smittestopp"

        if new_downloads != 0:
            ret_str += f"\n{new_downloads:,} {new_downloads_text}"

        if new_reported != 0:
            ret_str += f"\n{new_reported:,} {new_reported_text}"

        ret_str += f"\n\nTotalt antall nedlastinger: {curr_total_downloads:,}"
        ret_str += f"\nTotalt meldt smittet i appen: {curr_total_reported:,} personer"
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("smittestopp", curr_data)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")

        file_smittestopp = "./graphs/no_smittestopp.png"
        smittestopp_graph = twitter.media_upload(file_smittestopp)

        twitter.update_status(ret_str, media_ids=[smittestopp_graph.media_id])


def omicron():
    source_url = jobs["omicron"]["source"]["url"]

    curr_data = c19norge.timeseries("omicron")[-1]
    curr_total_confirmed = int(curr_data.get("total_confirmed"))

    last_data = file_open_json("omicron")
    last_total_confirmed = int(last_data.get("total_confirmed"))

    diff_total_confirmed = curr_total_confirmed - last_total_confirmed

    if diff_total_confirmed > 0:
        if diff_total_confirmed == 1:
            new_confirmed_text = "nytt bekreftet smittetilfelle"
        else:
            new_confirmed_text = "nye bekreftede smittetilfeller"

        ret_str = "🧬 Tilfeller av Omikron-viruset"

        if diff_total_confirmed > 0:
            ret_str += f"\n{diff_total_confirmed:,} {new_confirmed_text}"

        ret_str += f"\n\nTotalt bekreftede tilfeller: {curr_total_confirmed:,}"
        ret_str += f"\n\nKilde: {source_url}"

        file_write_json("omicron", curr_data)

        ret_str = ret_str.replace(",", " ")
        print(ret_str, "\n")

        twitter.update_status(ret_str)

    else:
        return None


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

    ret_str = ret_str.replace(",", " ")
    print(ret_str, "\n")
    twitter.update_status(ret_str)


def rss_feed():
    feed = fetch_feed()

    if feed:
        twitter.update_status(feed)
