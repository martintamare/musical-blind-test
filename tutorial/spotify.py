#!/usr/bin/env python

import os
import spotipy

from dotenv import load_dotenv
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
from time import sleep

load_dotenv()
scopes = [
    "user-library-read",
    "user-read-playback-state",
    "user-modify-playback-state",
    "streaming",
    "playlist-read-private",
    "playlist-read-collaborative",
]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=",".join(scopes)))
res = sp.devices()
wanted_id = None
for d in res["devices"]:
    pprint(d)
    if d["name"].startswith("MartinBook"):
        wanted_id = d["id"]
pprint(wanted_id)

# Change track
sp.start_playback(uris=["spotify:track:6gdLoMygLsgktydTQ71b15"], device_id=wanted_id)

# Change volume
sp.volume(100)
sleep(2)
sp.volume(50)
sleep(2)
sp.volume(100)
