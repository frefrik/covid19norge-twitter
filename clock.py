import sys
import logging
import yaml
import bot
from apscheduler.schedulers.blocking import BlockingScheduler
from modules.utils import update_data

with open("./config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

logging.basicConfig()
logging.getLogger("apscheduler").setLevel(logging.WARN)

jobs = cfg["twitter"]["jobs"]
sched = BlockingScheduler()

if "update" in sys.argv[1:]:
    print("Updating datasources")
    update_data()

# general stats
sched.add_job(bot.tested, trigger="cron", minute="*/" + str(jobs["tested"]["interval"]))
sched.add_job(
    bot.tested_lab, trigger="cron", minute="*/" + str(jobs["tested_lab"]["interval"])
)

sched.add_job(
    bot.confirmed, trigger="cron", minute="*/" + str(jobs["confirmed"]["interval"])
)
sched.add_job(
    bot.confirmed_by_testdate,
    trigger="cron",
    minute="*/" + str(jobs["confirmed_by_testdate"]["interval"]),
)

sched.add_job(bot.dead, trigger="cron", minute="*/" + str(jobs["dead"]["interval"]))

sched.add_job(
    bot.vaccine_doses, trigger="cron", minute="*/" + str(jobs["vaccine"]["interval"])
)

sched.add_job(
    bot.hospitalized,
    trigger="cron",
    minute="*/" + str(jobs["hospitalized"]["interval"]),
)

sched.add_job(
    bot.smittestopp, trigger="cron", minute="*/" + str(jobs["smittestopp"]["interval"])
)

# rss
sched.add_job(
    bot.rss_feed, trigger="cron", minute="*/" + str(jobs["rss_feed"]["interval"])
)

# daily jobs
sched.add_job(bot.daily_stats, trigger="cron", hour=0, minute=30)

print("Starting scheduler!")
sched.start()
