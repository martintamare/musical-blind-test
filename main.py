import config
from pprint import pprint
from tkinter import Tk, Frame, Grid, Button
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import time, datetime
from playsound import playsound


def play_sound(name):
    playsound(name, False)


class Chronometer:
    def __init__(self, element):
        self.element = element
        self.duration_at_pause = None

    def run(self):
        def count():
            duration = datetime.datetime.now() - self.start_time
            if self.duration_at_pause:
                duration += self.duration_at_pause
            total_seconds = duration.total_seconds()
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

    def get_playlists(self):
        limit = 50
        offset = 0
        stop = False
        ok_playlists = {}
        while not stop:
            playlists = self.sp.current_user_playlists(limit, offset)
            items = playlists["items"]
            for item in items:
                name = item["name"]
                if name.lower().startswith("mbt_"):
                    uri = item["uri"]
                    ok_playlists[name[4:]] = uri

            if len(items) == limit:
                offset += limit
            else:
                stop = True
        self._playlists = ok_playlists

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
        if self._playlists is None:
            self.get_playlists()
        return self._playlists

    @property
    def devices(self):
        if self._devices is None:
            self.get_device_list()
        return self._devices

    def check_login_status(self):
        token_info = self.auth_manager.get_cached_token()

        if token_info:
            if not self.auth_manager.is_token_expired(token_info):
                return True
        return False

    def set_playlist(self, name, uri):
        self.active_playlist = {"name": name, "uri": uri}

    def start_playlist(self):
        if not self.active_playlist:
            return
        uri = self.active_playlist["uri"]
        items = self.sp.playlist_items(uri)
        self.active_items = items["items"]
        self.active_index = 0
        self.play_track()

    @property
    def device_id(self):
        if self.chosen_device:
            return self.chosen_device["id"]
        else:
            return None

    def pause(self):
        if self.player_status != "pause":
            self.sp.pause_playback(device_id=self.device_id)
            self.player_status = "pause"

    def resume(self):
        if self.player_status != "play":
            self.sp.start_playback(device_id=self.device_id)
            self.player_status = "play"

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
        self.buttons = []
        self.player_buttons = []
        self.player_color = {}

        for column in range(4):
            self.grid_columnconfigure(column, weight=1)
        for row in range(4):
            self.grid_rowconfigure(row, weight=1)

        self.button1 = Button(root, text="Game", **self.button_dict)
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

        self.button3 = Button(root, text="Quit", **self.button_dict)
        self.button3.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.button3.grid(column=0, row=3, **self.grid_dict, columnspan=4)
        self.buttons.append(self.button3)

        self.chronometer = Chronometer(self.button2)

    def show(self):
        if not self._setup:
            self.setup()
        self.tkraise()
        self.buttons[0].focus_set()
        self.selected_button_index = 0
        self.chronometer.start()
        self.spotify_manager.start_playlist()

    def pause(self):
        self.chronometer.pause()
        self.spotify_manager.pause()

    def resume(self):
        self.reset_player_buttons()
        self.spotify_manager.resume()
        self.chronometer.resume()

    def next_song(self):
        print("TODO")

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
            self.resume()

        elif key == "y":
            self.next_song()

    def answer_from_player(self, player):
        if self.spotify_manager.player_status == "play":
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
            test = self.player_buttons[player]
            self.player_buttons[player].configure(highlightbackground=color)


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
            self.controller.show_frame("GamePage")


class PlaylistChoicePage(Page):
    def setup(self):
        self.grid_columnconfigure(0, weight=1)

        self.button1 = Button(root, text="Choose a playlist", **self.button_dict)
        self.buttons.append(self.button1)

        index = 1
        for name, uri in self.spotify_manager.playlists.items():
            self.grid_rowconfigure(index, weight=1)
            index += 1

            button = Button(root, text=name, **self.button_dict)
            button.bind(
                "<Return>",
                lambda event, name=name, uri=uri: self.launch_ready_page(name, uri),
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

    def launch_ready_page(self, name, uri):
        self.spotify_manager.set_playlist(name, uri)
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
        self.spotify_manager.get_device_list()
        if self.spotify_manager.chosen_device:
            device_name = self.spotify_manager.chosen_device["name"]
            button3_text = f"Device : {device_name}"
            self.button3.config(text=button3_text)

    def update_device_list(self):
        devices = self.spotify_manager.get_device_list()
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

    def del_player(self):
        current_players = self.controller.players
        if current_players - 1 > 1:
            self.controller.players = current_players - 1
        self.display_players()

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
        self.scores = {}

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
