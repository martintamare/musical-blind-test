from tkinter import Frame, Button
from .helpers import CountDown, Chronometer
from utils import play_sound
from time import sleep


class Page(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.root = controller.root
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
        self.button1 = Button(self.root, text=button_text, **self.button_dict)
        self.buttons.append(self.button1)
        self.button1.grid(column=0, row=0, **self.grid_dict, columnspan=4)

        self.button2 = Button(self.root, text="Time", **self.button_dict)
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
            button = Button(self.root, text=f"P{index}", **self.button_dict)
            button.grid(column=player, row=2, **self.player_grid_dict)
            self.player_buttons.append(button)
            self.player_color[player] = "white"
            index += 1

        for player in range(self.controller.players):
            score = self.controller.scores[player]
            button = Button(self.root, text=f"{score}", **self.button_dict)
            button.grid(column=player, row=3, **self.player_grid_dict)
            self.score_buttons.append(button)

        self.button3 = Button(self.root, text="Quit", **self.button_dict)
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
        self.active_playlist.play()
        self.chronometer.start()

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
        self.button1 = Button(self.root, text="", **self.button_dict)
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
        self.button1 = Button(self.root, text="TODO", **self.button_dict)
        self.buttons.append(self.button1)
        Page.setup(self)


class StartPage(Page):
    def setup(self):
        self.button1 = Button(self.root, text="Start Game", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("PlaylistChoicePage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(self.root, text="Settings", **self.button_dict)
        self.button2.bind(
            "<Return>", lambda event: self.controller.show_frame("SettingPage")
        )
        self.buttons.append(self.button2)

        self.button3 = Button(self.root, text="Quit", **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.root.destroy())
        self.buttons.append(self.button3)
        Page.setup(self)


class ReadyPage(Page):
    def setup(self):
        self.buttons = []
        self.ready = {"master": False}

        self.grid_columnconfigure(0, weight=1)

        self.button1 = Button(self.root, text="Ready ?", **self.button_dict)
        self.buttons.append(self.button1)

        index = 1
        for player in range(self.controller.players):
            self.ready[index] = False

            button_text = f"Player {index} - Waiting Validation"
            button = Button(self.root, text=button_text, **self.button_dict)
            self.buttons.append(button)

            index += 1

        self.button4 = Button(self.root, text="Back", **self.button_dict)
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

        self.button1 = Button(self.root, text="Choose a playlist", **self.button_dict)
        self.buttons.append(self.button1)

        index = 1
        for index_playlist, playlist in enumerate(self.spotify_manager.playlists):
            self.grid_rowconfigure(index, weight=1)
            index += 1

            button_text = f"{playlist.name} - {playlist.number_of_songs} songs"
            button = Button(self.root, text=button_text, **self.button_dict)
            button.bind(
                "<Return>",
                lambda event, index_playlist=index_playlist: self.launch_ready_page(
                    index_playlist
                ),
            )
            self.buttons.append(button)

        # Back
        self.grid_rowconfigure(index, weight=1)

        self.button4 = Button(self.root, text="Back", **self.button_dict)
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

        self.button1 = Button(self.root, text="Players", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("PlayerPage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(self.root, text="Log in to Spotify", **self.button_dict)
        self.button2.bind("<Return>", lambda event: self.login_to_spotify())
        self.buttons.append(self.button2)

        button3_text = "Please choose device"
        self.button3 = Button(self.root, text=button3_text, **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.update_device_list())
        self.buttons.append(self.button3)

        self.button4 = Button(self.root, text="Back", **self.button_dict)
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
        self.button1 = Button(self.root, text=button1_text, **self.button_dict)
        self.buttons.append(self.button1)

        self.button2 = Button(self.root, text="+", **self.button_dict)
        self.button2.bind("<Return>", lambda event: self.add_player())
        self.buttons.append(self.button2)

        self.button3 = Button(self.root, text="-", **self.button_dict)
        self.button3.bind("<Return>", lambda event: self.del_player())
        self.buttons.append(self.button3)

        self.button4 = Button(self.root, text="Back", **self.button_dict)
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
            button = Button(self.root, text=name, **self.button_dict)
            button.bind(
                "<Return>", lambda event, device=device: self.set_device(device)
            )
            self.buttons.append(button)

        # Back
        self.grid_rowconfigure(index, weight=1)

        self.button4 = Button(self.root, text="Back", **self.button_dict)
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
