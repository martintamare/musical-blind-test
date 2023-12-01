import config
from tkinter import Tk, Frame, Grid, Button
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import datetime
from time import sleep
from playsound import playsound


def play_sound(name, block=False):
    playsound(name, False)


class CountDown:
    def __init__(self, element, actions, time=3):
        self.element = element
        self.init_time = time
        self.time = time
        self.actions = actions
        self.element.configure(text=f"{self.time}")

    def run(self):
        def count():
            new_time = self.time - 1
            if new_time < 0:
                self.element.after_cancel(self.after)
                for action in self.actions:
                    action()
            else:
                self.time = new_time
                self.element.configure(text=f"{self.time}")
                self.after = self.element.after(1000, count)

        count()

    def start(self):
        self.run()

    def reset(self):
        self.time = self.init_time


class Chronometer:
    def __init__(self, element):
        self.element = element
        self.duration_at_pause = None
        self.duration = None

    def ok_for_bonus(self):
        total_seconds = int(self.duration.total_seconds())
        print(f"ok_for_bonus {total_seconds}")
        if total_seconds < 4:
            return True
        return False

    def run(self):
        def count():
            self.duration = datetime.datetime.now() - self.start_time
            if self.duration_at_pause:
                self.duration += self.duration_at_pause
            total_seconds = self.duration.total_seconds()
            self.element.configure(text=f"{total_seconds:.1f} s")
            self.after = self.element.after(100, count)

        count()

    def pause(self):
        if self.duration_at_pause is None:
            self.duration_at_pause = datetime.datetime.now() - self.start_time
        else:
            duration = datetime.datetime.now() - self.start_time
            self.duration_at_pause += duration
        if self.after:
            self.element.after_cancel(self.after)

    def start(self):
        self.start_time = datetime.datetime.now()
        self.run()

    def resume(self):
        self.start()


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


class Page(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.spotify_manager = controller.spotify_manager

        self.buttons = []
        self.selected_button_index = 0

        self.button_dict = {
            "fg": "black",
            "font": ("Arial", 25, "bold"),
        }
        self.grid_dict = {"sticky": "nswe", "padx": 50, "pady": 50}
        self._setup = False

    def reset_setup(self):
        self._setup = False

    def setup(self):
        self._setup = True

        self.grid_columnconfigure(0, weight=1)
        for index in range(len(self.buttons)):
            self.grid_rowconfigure(index, weight=1)

    def navigate_up(self):
        self.selected_button_index = (self.selected_button_index - 1) % len(
            self.buttons
        )
        self.update_button_selection()

    def navigate_down(self):
        self.selected_button_index = (self.selected_button_index + 1) % len(
            self.buttons
        )
        self.update_button_selection()

    def update_button_selection(self):
        self.buttons[self.selected_button_index].focus_set()

    def hide(self):
        for button in self.buttons:
            button.grid_forget()

    def show(self):
        if not self._setup:
            self.setup()
        for index in range(len(self.buttons)):
            self.buttons[index].grid(column=0, row=index, **self.grid_dict)
        self.tkraise()
        self.buttons[0].focus_set()
        self.selected_button_index = 0

    def key_pressed(self, event):
        pass


class GamePage(Page):
    def setup(self):
        self.active_playlist = self.spotify_manager.active_playlist
        self.buttons = []
        self.player_buttons = []
        self.score_buttons = []
        self.player_color = {}

        for column in range(4):
            self.grid_columnconfigure(column, weight=1)
        for row in range(5):
            self.grid_rowconfigure(row, weight=1)

        current_song = self.active_playlist.current_song_number
        total_songs = self.active_playlist.number_of_songs
        button_text = f"Song {current_song}/{total_songs}"
        self.button1 = Button(root, text=button_text, **self.button_dict)
        self.buttons.append(self.button1)
        self.button1.grid(column=0, row=0, **self.grid_dict, columnspan=4)

        self.button2 = Button(root, text="Time", **self.button_dict)
        self.buttons.append(self.button2)
        self.button2.grid(column=0, row=1, **self.grid_dict, columnspan=4)

        self.player_button_dict = {
            "highlightbackground": "white",
            "highlightthickness": 10,
            "borderwidth": 0.9,
            "fg": "black",
            "font": ("Arial", 25, "bold"),
        }
        self.player_grid_dict = {"sticky": "nswe", "padx": 10, "pady": 10}
        index = 1
        for player in range(self.controller.players):
            button = Button(root, text=f"P{index}", **self.button_dict)
            button.grid(column=player, row=2, **self.player_grid_dict)
            self.player_buttons.append(button)
            self.player_color[player] = "white"
            index += 1

        for player in range(self.controller.players):
            score = self.controller.scores[player]
            button = Button(root, text=f"{score}", **self.button_dict)
            button.grid(column=player, row=3, **self.player_grid_dict)
            self.score_buttons.append(button)

        self.button3 = Button(root, text="Quit", **self.button_dict)
        self.button3.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.button3.grid(column=0, row=4, **self.grid_dict, columnspan=4)
        self.buttons.append(self.button3)

        self.chronometer = Chronometer(self.button2)

    def show(self):
        if not self._setup:
            self.setup()
        self.tkraise()
        self.buttons[0].focus_set()
        self.selected_button_index = 0
        self.chronometer.start()
        self.active_playlist.play()

    def hide(self):
        Page.hide(self)
        if hasattr(self, "player_buttons"):
            for button in self.player_buttons:
                button.grid_forget()
        if hasattr(self, "score_buttons"):
            for button in self.score_buttons:
                button.grid_forget()

    def pause(self):
        self.chronometer.pause()
        self.active_playlist.pause()

    def wrong_answer(self):
        if self.active_playlist.player_status == "play":
            return
        play_sound("./sounds/ko.mp3", True)
        sleep(1)
        self.reset_player_buttons()
        self.active_playlist.resume()
        self.chronometer.resume()

    def display_answer(self):
        button_text = self.active_playlist.current_song.details
        self.button2.configure(text=button_text)

    def update_scores(self):
        for index, player in enumerate(self.player_color):
            color = self.player_color[player]
            if color == "green":
                add_score = 1
                if self.chronometer.ok_for_bonus():
                    add_score = 2
                self.controller.scores[index] += add_score
        for player in range(self.controller.players):
            score = self.controller.scores[player]
            print(f"player {player+1} {score}")
            self.score_buttons[player].configure(text=f"{score}")

    def go_next(self):
        def next_action():
            if self.active_playlist.is_over:
                self.controller.show_frame("ScorePage")
            else:
                self.active_playlist.next_song()
                self.controller.show_frame("SplashPage")
                self.controller.frames["SplashPage"].reset()

        self.after(5000, next_action)

    def right_answer(self):
        if self.active_playlist.player_status == "play":
            return
        self.active_playlist.resume()
        self.display_answer()
        self.update_scores()
        play_sound("./sounds/ok.mp3", True)
        self.go_next()

    def skip(self):
        self.display_answer()
        self.go_next()

    def key_pressed(self, event):
        key = event.char.lower()
        mapping = {
            "a": 0,
            "z": 1,
            "e": 2,
            "r": 3,
        }
        if key in mapping:
            player = mapping[key]
            self.answer_from_player(player)
        elif key == "t":
            self.wrong_answer()

        elif key == "y":
            self.right_answer()

        elif key == "h":
            self.skip()

        elif key == "g":
            self.go_next()

    def answer_from_player(self, player):
        if self.active_playlist.player_status == "play":
            if self.player_color[player] != "red":
                self.player_color[player] = "green"
                self.update_player_buttons()
                self.pause()

    def reset_player_buttons(self):
        for player in range(self.controller.players):
            self.player_color[player] = "white"
        self.update_player_buttons()

    def update_player_buttons(self):
        for player in range(self.controller.players):
            color = self.player_color[player]
            self.player_buttons[player].configure(highlightbackground=color)


class SplashPage(Page):
    def setup(self):
        self.button1 = Button(root, text="", **self.button_dict)
        self.buttons.append(self.button1)

        def action_1():
            self.controller.show_frame("GamePage")

        actions = [action_1]

        self.countdown = CountDown(self.button1, actions, 6)
        Page.setup(self)
        self.countdown.start()

    def reset(self):
        self.countdown.reset()
        self.countdown.start()


class ScorePage(Page):
    def setup(self):
        self.button1 = Button(root, text="TODO", **self.button_dict)
        self.buttons.append(self.button1)
        Page.setup(self)


class StartPage(Page):
    def setup(self):
        self.button1 = Button(root, text="Start Game", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("PlaylistChoicePage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(root, text="Settings", **self.button_dict)
        self.button2.bind(
            "<Return>", lambda event: self.controller.show_frame("SettingPage")
        )
        self.buttons.append(self.button2)

        self.button3 = Button(root, text="Quit", **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.controller.root.destroy())
        self.buttons.append(self.button3)
        Page.setup(self)


class ReadyPage(Page):
    def setup(self):
        self.buttons = []
        self.ready = {"master": False}

        self.grid_columnconfigure(0, weight=1)

        self.button1 = Button(root, text="Ready ?", **self.button_dict)
        self.buttons.append(self.button1)

        index = 1
        for player in range(self.controller.players):
            self.ready[index] = False

            button_text = f"Player {index} - Waiting Validation"
            button = Button(root, text=button_text, **self.button_dict)
            self.buttons.append(button)

            index += 1

        self.button4 = Button(root, text="Back", **self.button_dict)
        self.button4.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.buttons.append(self.button4)
        self.grid_dict = {"sticky": "nswe", "padx": 10, "pady": 10}
        Page.setup(self)

    def show(self):
        Page.show(self)
        self.focus_set()

    def key_pressed(self, event):
        key = event.char.lower()
        mapping = {
            "a": 1,
            "z": 2,
            "e": 3,
            "r": 4,
        }
        if key in mapping:
            player = mapping[key]
            self.set_player_ready(player)
        elif key == "t":
            self.ready["master"] = True
            self.ready_to_run()

    def set_player_ready(self, index):
        if index in self.ready:
            self.ready[index] = True
            self.buttons[index].configure(text=f"Player {index} - Ready !")
            self.ready_to_run()
        else:
            print("Player {index} not present")

    def ready_to_run(self):
        ready = True
        for index, player_ready in self.ready.items():
            if not player_ready:
                ready = False
                break
        if ready and self.ready:
            self.controller.show_frame("SplashPage")


class PlaylistChoicePage(Page):
    def setup(self):
        self.grid_columnconfigure(0, weight=1)

        self.button1 = Button(root, text="Choose a playlist", **self.button_dict)
        self.buttons.append(self.button1)

        index = 1
        for index_playlist, playlist in enumerate(self.spotify_manager.playlists):
            self.grid_rowconfigure(index, weight=1)
            index += 1

            button_text = f"{playlist.name} - {playlist.number_of_songs} songs"
            button = Button(root, text=button_text, **self.button_dict)
            button.bind(
                "<Return>",
                lambda event, index_playlist=index_playlist: self.launch_ready_page(
                    index_playlist
                ),
            )
            self.buttons.append(button)

        # Back
        self.grid_rowconfigure(index, weight=1)

        self.button4 = Button(root, text="Back", **self.button_dict)
        self.button4.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.buttons.append(self.button4)
        Page.setup(self)

    def launch_ready_page(self, index):
        self.spotify_manager.set_playlist(index)
        self.controller.show_frame("ReadyPage")


class SettingPage(Page):
    def setup(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.button1 = Button(root, text="Players", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("PlayerPage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(root, text="Log in to Spotify", **self.button_dict)
        self.button2.bind("<Return>", lambda event: self.login_to_spotify())
        self.buttons.append(self.button2)

        button3_text = "Please choose device"
        self.button3 = Button(root, text=button3_text, **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.update_device_list())
        self.buttons.append(self.button3)

        self.button4 = Button(root, text="Back", **self.button_dict)
        self.button4.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.buttons.append(self.button4)
        Page.setup(self)

    def login_to_spotify(self):
        if self.spotify_manager.check_login_status():
            user = self.spotify_manager.user
            name = user["id"]
            self.button2.config(text=f"Logged in as - {name}")
        else:
            self.spotify_manager.login()
        self.spotify_manager.devices
        if self.spotify_manager.chosen_device:
            device_name = self.spotify_manager.chosen_device["name"]
            button3_text = f"Device : {device_name}"
            self.button3.config(text=button3_text)

    def update_device_list(self):
        self.spotify_manager.devices
        self.controller.show_frame("DevicePage")


class PlayerPage(Page):
    def setup(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)

        button1_text = f"Current Player : {self.controller.players}"
        self.button1 = Button(root, text=button1_text, **self.button_dict)
        self.buttons.append(self.button1)

        self.button2 = Button(root, text="+", **self.button_dict)
        self.button2.bind("<Return>", lambda event: self.add_player())
        self.buttons.append(self.button2)

        self.button3 = Button(root, text="-", **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.del_player())
        self.buttons.append(self.button3)

        self.button4 = Button(root, text="Back", **self.button_dict)
        self.button4.bind(
            "<Return>", lambda event: self.controller.show_frame("SettingPage")
        )
        self.buttons.append(self.button4)
        Page.setup(self)

    def add_player(self):
        current_players = self.controller.players
        if current_players + 1 < 5:
            self.controller.players = current_players + 1
        self.display_players()
        self.controller.reset_score()

    def del_player(self):
        current_players = self.controller.players
        if current_players - 1 > 1:
            self.controller.players = current_players - 1
        self.display_players()
        self.controller.reset_score()

    def display_players(self):
        button1_text = f"Current Player : {self.controller.players}"
        self.button1.configure(text=button1_text)


class DevicePage(Page):
    def setup(self):
        self.grid_columnconfigure(0, weight=1)
        index = 0
        for device in self.spotify_manager.devices:
            self.grid_rowconfigure(index, weight=1)
            index += 1

            name = device["name"]
            button = Button(root, text=name, **self.button_dict)
            button.bind(
                "<Return>", lambda event, device=device: self.set_device(device)
            )
            self.buttons.append(button)

        # Back
        self.grid_rowconfigure(index, weight=1)

        self.button4 = Button(root, text="Back", **self.button_dict)
        self.button4.bind(
            "<Return>", lambda event: self.controller.show_frame("SettingPage")
        )
        self.buttons.append(self.button4)
        Page.setup(self)

    def set_device(self, device):
        self.spotify_manager.set_device(device)
        device_name = device["name"]
        button3_text = f"Device : {device_name}"
        self.controller.frames["SettingPage"].button3.config(text=button3_text)
        self.controller.show_frame("SettingPage")


class App:
    def __init__(self, root):
        self.root = root
        self._padx = 50
        self._pady = 50
        self.spotify_manager = SpotifyManager()
        self.players = 2
        self.reset_score()

        container = Frame(self.root)
        Grid.columnconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 1, weight=1)
        Grid.rowconfigure(root, 2, weight=1)
        Grid.rowconfigure(root, 3, weight=1)
        Grid.rowconfigure(root, 4, weight=1)
        Grid.rowconfigure(root, 5, weight=1)
        Grid.rowconfigure(root, 6, weight=1)

        self.active_frame = None
        self.frames = {}
        for F in (
            StartPage,
            PlaylistChoicePage,
            SettingPage,
            DevicePage,
            PlayerPage,
            ReadyPage,
            GamePage,
            SplashPage,
            ScorePage,
        ):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

        root.bind("<Up>", lambda event: self.navigate_up())
        root.bind("<Down>", lambda event: self.navigate_down())
        root.bind("<KeyPress>", lambda event: self.key_pressed(event))

    def reset_score(self):
        scores = []
        for player in range(self.players):
            scores.append(0)
        self.scores = scores

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        self.active_frame = self.frames[page_name]
        for frame in self.frames.values():
            if frame != self.active_frame:
                frame.hide()
        if page_name == "ReadyPage":
            self.active_frame.reset_setup()
        self.active_frame.show()

    def navigate_up(self):
        play_sound("./sounds/navigation.wav")
        self.active_frame.navigate_up()

    def navigate_down(self):
        play_sound("./sounds/navigation.wav")
        self.active_frame.navigate_down()

    def key_pressed(self, event):
        self.active_frame.key_pressed(event)


if __name__ == "__main__":
    load_dotenv()
    root = Tk()
    root.geometry(
        f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}+10+10"
    )  # Default window size
    root.title = config.SCREEN_TITLE

    app = App(root)

    root.mainloop()
