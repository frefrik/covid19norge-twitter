import logging
import tweepy
import yaml

logger = logging.getLogger()

with open("./config/config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

auth_cfg = cfg["twitter"]["auth"]


def create_api():
    auth = tweepy.OAuthHandler(auth_cfg["consumer_key"], auth_cfg["consumer_secret"])

    auth.set_access_token(auth_cfg["access_token"], auth_cfg["access_token_secret"])

    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e

    logger.info("API created")

    return api
