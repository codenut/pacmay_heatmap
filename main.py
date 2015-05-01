import json
import time
from random import random
from redis import StrictRedis
from bson import json_util
from flask import Flask, Response, jsonify
from flask.ext.cors import CORS, cross_origin
from pymongo import MongoClient, CursorType
from threading import Thread

def connect():
  con = MongoClient()
  return con["pacmay"]

app = Flask(__name__)
cors = CORS(app)
handle = connect()
redis = StrictRedis()

def rand_loc():
  lat = random() * 180 - 90
  lng = random() * 360 - 180
  return [lat, lng]

def get_cursor(collection, condition, await_data=True):
  cursor_type = CursorType.TAILABLE
  if await_data:
    cursor_type = CursorType.TAILABLE_AWAIT
  cur = collection.find(condition, cursor_type=cursor_type)
  return cur

def get_tweets():
  cursor = get_cursor(handle.tweets, {"coordinates.type": "Point"})
  i = 0
  while cursor.alive:
    i += 1
    try:
      doc = cursor.next()
      if doc and "coordinates" in doc and doc["coordinates"]:
        coordinates = doc["coordinates"]["coordinates"]
      else:
        coordinates = rand_loc()

      if "text" in doc:
        text = doc["text"]

      if "user" in doc and "profile_image_url" in doc["user"]:
        profile_image = doc["user"]["profile_image_url"]

      redis.publish("chat", '{"coordinates": %s, "data": %s, "index": %i, "profile_image": %s}' 
                          %  (coordinates, json.dumps(text), i, json.dumps(profile_image)))
    except StopIteration:
      time.sleep(1)

def run_thread():
  th = Thread(target=get_tweets)
  th.start()

def event_stream():
  pubsub = redis.pubsub()
  pubsub.subscribe("chat")
  for message in pubsub.listen():
    yield "data: %s\n\n" % message["data"]

@app.route("/new_tweets")
@cross_origin()
def new_tweets():
  return Response(event_stream(), mimetype="text/event-stream")

@app.route("/tweets")
@cross_origin()
def tweets():
  cursor = handle.tweets.find({"coordinates.type": "Point"})
  tweets = [{"coordinates": doc["coordinates"]["coordinates"]} for doc in cursor]
  return json.dumps(tweets)

if __name__ == "__main__":
  app.before_first_request(run_thread)
  app.run(debug=True)
