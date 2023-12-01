import spotipy
from spotipy.oauth2 import SpotifyOAuth


class SpotifySong:
    def __init__(self, playlist, uri, name, album, release_date, artist):
        self.playlist = playlist
        self.manager = playlist.manager
        self.sp = playlist.sp
        self.uri = uri
        self.name = name
        self.album = album
        self.release_date = release_date
        self.artist = artist

    @property
    def details(self):
        return f"{self.artist} - {self.name} - {self.release_date}"


class SpotifyPlaylist:
    def __init__(self, manager, name, uri):
        self.manager = manager
        self.uri = uri
        self.sp = manager.sp
        self._songs = None
        self.name = name
        self.current_index = 0
        self.player_status = None
        self.device_id = manager.device_id

    @property
    def current_song_number(self):
        return self.current_index + 1

    @property
    def songs(self):
        if self._songs is not None:
            return self._songs

        limit = 50
        offset = 0
        stop = False
        ok_songs = []
        while not stop:
            songs = self.sp.playlist_items(
                self.uri, limit=limit, offset=offset, additional_types=["track"]
            )
            items = songs["items"]
            for item in items:
                if "track" not in item:
                    continue
                track = item["track"]
                uri = track["uri"]
                name = track["name"]
                album = track["album"]
                release_date = album["release_date"]
                artists = track["artists"]
                artist = " & ".join([x["name"] for x in artists])
                song = SpotifySong(
                    self,
                    uri,
                    name,
                    album,
                    release_date,
                    artist,
                )
                ok_songs.append(song)
            if len(items) == limit:
                offset += limit
            else:
                stop = True
        self._songs = ok_songs
        return ok_songs

    @property
    def number_of_songs(self):
        return len(self.songs)

    @property
    def current_song(self):
        return self.songs[self.current_index]

    @property
    def is_over(self):
        next_index = self.current_index + 1
        if next_index >= self.number_of_songs:
            return True
        else:
            return False

    def next_song(self):
        self.current_index += 1

    def play(self):
        uri = self.current_song.uri
        self.player_status = "play"
        self.sp.start_playback(device_id=self.device_id, uris=[uri])

    def pause(self):
        if self.player_status != "pause":
            self.sp.pause_playback(device_id=self.device_id)
            self.player_status = "pause"

    def resume(self):
        if self.player_status != "play":
            self.sp.start_playback(device_id=self.device_id)
            self.player_status = "play"


class SpotifyManager:
    def __init__(self):
        scopes = [
            "user-library-read",
            "user-read-playback-state",
            "user-modify-playback-state",
            "streaming",
            "playlist-read-private",
            "playlist-read-collaborative",
        ]
        scope = ",".join(scopes)
        self.auth_manager = SpotifyOAuth(scope=scope)
        self._sp = None
        self._user = None
        self._devices = None
        self.chosen_device = None
        self._playlists = None
        self.active_playlist = None
        self.player_status = None

    @property
    def sp(self):
        if self._sp is not None:
            return self._sp
        else:
            self._sp = spotipy.Spotify(auth_manager=self.auth_manager)
            return self._sp

    def get_device_list(self):
        devices = self.sp.devices()
        self._devices = devices["devices"]
        for device in self._devices:
            if device["is_active"]:
                self.chosen_device = device
        if self.chosen_device is None:
            if len(self._devices):
                self.chosen_device = self._devices[0]
        return self._devices

    def set_device(self, device):
        self.chosen_device = device

    @property
    def playlists(self):
        if self._playlists is not None:
            self._playlists

        limit = 50
        offset = 0
        stop = False
        ok_playlists = []
        while not stop:
            playlists = self.sp.current_user_playlists(limit, offset)
            items = playlists["items"]
            for item in items:
                name = item["name"]
                if name.lower().startswith("mbt_"):
                    uri = item["uri"]
                    ok_name = name[4:]
                    ok_playlists.append(SpotifyPlaylist(self, ok_name, uri))

            if len(items) == limit:
                offset += limit
            else:
                stop = True
        self._playlists = ok_playlists
        return ok_playlists

    @property
    def devices(self):
        if self._devices is not None:
            return self._devices

        devices = self.sp.devices()
        self._devices = devices["devices"]
        for device in self._devices:
            if device["is_active"]:
                self.chosen_device = device
        if self.chosen_device is None:
            if len(self._devices):
                self.chosen_device = self._devices[0]
        return self._devices

    def check_login_status(self):
        token_info = self.auth_manager.get_cached_token()

        if token_info:
            if not self.auth_manager.is_token_expired(token_info):
                return True
        return False

    def set_playlist(self, index):
        self.active_playlist = self.playlists[index]

    @property
    def device_id(self):
        if self.chosen_device:
            return self.chosen_device["id"]
        else:
            return None

    def play_track(self):
        item = self.active_items[self.active_index]
        track = item["track"]
        uri = track["uri"]
        name = track["name"]
        album = track["album"]
        album_name = album["name"]
        release_date = album["release_date"]
        artists = track["artists"]

        for a in artists:
            print(f"artist {a}")

        artist = " & ".join([x["name"] for x in artists])

        print(f"name={name}")
        print(f"album={album_name} - {release_date}")
        print(f"artist={artist}")
        self.player_status = "play"
        self.sp.start_playback(device_id=self.device_id, uris=[uri])

    @property
    def user(self):
        if self._user is not None:
            return self._user
        else:
            self._user = self.sp.current_user()
            return self._user
