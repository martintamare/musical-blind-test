import config
from pprint import pprint
from tkinter import *
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.button_dict = {
            "bg": "#22cbff",
            "fg": "black",
            "font": ("Arial", 25, "bold"),
        }
        self.grid_dict = {"sticky": "nswe", "padx": 50, "pady": 50}

        self.setup()

    def setup(self):
        pass

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
        for index in range(len(self.buttons)):
            self.buttons[index].grid(column=0, row=index, **self.grid_dict)
        self.tkraise()
        self.buttons[0].focus_set()
        self.selected_button_index = 0


class StartPage(Page):
    def setup(self):
        self.button1 = Button(root, text="Start Game", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("GamePage")
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


class GamePage(Page):
    def setup(self):
        self.button1 = Button(root, text="Yeah", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("GamePage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(root, text="Back", **self.button_dict)
        self.button2.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.buttons.append(self.button2)


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
        for F in (StartPage, GamePage, SettingPage, DevicePage, PlayerPage):
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

    def show_frame(self, page_name):
        """Show a frame for the given page name"""
        self.active_frame = self.frames[page_name]
        for frame in self.frames.values():
            if frame != self.active_frame:
                frame.hide()
        self.active_frame.show()

    def navigate_up(self):
        self.active_frame.navigate_up()

    def navigate_down(self):
        self.active_frame.navigate_down()


if __name__ == "__main__":
    load_dotenv()
    root = Tk()
    root.geometry(
        f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}+10+10"
    )  # Default window size
    root.title = config.SCREEN_TITLE

    app = App(root)

    root.mainloop()
