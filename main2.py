import requests
import spotipy
import os
import Creds
import spotipy.util as util
from time import sleep
from datetime import datetime

# Get Credentials from Creds.py file
users = Creds.users
playlist_id = Creds.playlist_id
discord_webhook = Creds.discord_webhook


def get_track_info(track):
    info = dict()

    info["dt_added"] = datetime.strptime(track["added_at"].replace("Z", "UTC"), "%Y-%m-%dT%H:%M:%S%Z")
    info["who"] = [x for x in users if x[2] == track["added_by"]["id"]][0][0]

    return info


def request_add_on_discord(user_i):
    user_name, user_id, _ = users[user_i]
    data = {"content": f"<@{user_id}> Add a song to the playlist!!"}
    requests.post(discord_webhook, json=data)


# Used to get correct authorization and scope from Spotify
scope = 'playlist-modify-public user-library-modify playlist-modify-private user-top-read'
os.environ["SPOTIPY_CLIENT_ID"] = Creds.ClientID
os.environ["SPOTIPY_CLIENT_SECRET"] = Creds.SecretID
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost/"


def get_token():
    token = util.prompt_for_user_token(Creds.spotfiy_username, scope)
    if token:
        return token
    else:
        print("Failed at receiving token")


# 'logs in' to spotfiy and gets client
spotify = spotipy.Spotify(auth=get_token())

# Retrieves to total number of songs in playlist to be used in offset
items = spotify.playlist_items(playlist_id, limit=5)
total = items["total"]
sleep(1)

# Get the last 20 songs and extracts useful information from playlist
items = spotify.playlist_items(playlist_id, offset=total - 20)
songs = list(get_track_info(x) for x in items["items"])

# iterates over users to figure out who has not added a songs for the longest time
songs_rev_who = [x["who"] for x in songs[::-1]]
last = 0
next_i = 0
for i, name in enumerate([x[0] for x in users]):
    if songs_rev_who.index(name) > last:
        next_i = i
        last = songs_rev_who.index(name)

# Posts notification on Discord
request_add_on_discord(next_i)
