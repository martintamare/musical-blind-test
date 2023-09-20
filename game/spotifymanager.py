import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

scopes = [
    "user-library-read",
    "user-read-playback-state",
    "user-modify-playback-state",
    "streaming",
    "playlist-read-private",
    "playlist-read-collaborative",
]
scope = ",".join(scopes)


class SpotifyManager:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    def get_device_list(self):
        devices = self.sp.devices()
        return devices["devices"]
