from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.utils import import_simplejson
from pymongo import MongoClient
import logging
import yaml
import os

with open("config.yml", "r") as ymlfile:
  cfg = yaml.load(ymlfile)

cwd = os.path.dirname(os.path.realpath(__file__))
logger = logging.getLogger("twitter_stream")

handler = logging.FileHandler(cwd + "/logs/twitter_stream.log")
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("test")
logger.debug("test")

access_token = cfg["twitter"]["access_token"]
access_token_secret = cfg["twitter"]["access_token_secret"]
consumer_key = cfg["twitter"]["consumer_key"]
consumer_secret = cfg["twitter"]["consumer_secret"]

def connect():
  con = MongoClient()
  return con["pacmay"]

def create_collection(db, name):
  if name not in db.collection_names():
    db.create_collection(name, capped=True, await_data=True, size=25000000000)
  return db[name]

handle = connect()
col = create_collection(handle, "tweets")
json = import_simplejson()

class PacMayStreamListener(StreamListener):

  def on_data(self, data):
    print data
    logger.info(data)
    col.insert(json.loads(data))
    return True

  def on_error(self, status):
    print status


if __name__ == "__main__":
  listener = PacMayStreamListener()
  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)
  stream = Stream(auth, listener)
  stream.filter(track=["mayweatherpacquiao", "pacquiaomayweather", "pacquiao", "mayweather", "floydmayweather", "mannypacquiao"])
