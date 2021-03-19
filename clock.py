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
    bot.confirmed, trigger="cron", minute="*/" + str(jobs["confirmed"]["interval"])
)

sched.add_job(bot.dead, trigger="cron", minute="*/" + str(jobs["dead"]["interval"]))

sched.add_job(
    bot.admissions, trigger="cron", minute="*/" + str(jobs["admissions"]["interval"])
)

sched.add_job(
    bot.respiratory, trigger="cron", minute="*/" + str(jobs["respiratory"]["interval"])
)

# rss
sched.add_job(
    bot.rss_fhi, trigger="cron", minute="*/" + str(jobs["rss_fhi"]["interval"])
)

sched.add_job(
    bot.rss_regjeringen,
    trigger="cron",
    minute="*/" + str(jobs["rss_regjeringen"]["interval"]),
)

# daily jobs
sched.add_job(bot.daily_stats, trigger="cron", hour=0, minute=30)

sched.add_job(bot.daily_graphs, trigger="cron", hour=0, minute=31)

print("Starting scheduler!")
sched.start()
