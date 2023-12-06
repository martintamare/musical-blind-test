from tkinter import Frame, Button
from .helpers import CountDown, Chronometer
from utils import play_sound
from time import sleep


class NavigationButton(Button):
    def __init__(self, page, **kwargs):
        Button.__init__(page.root, **kwargs)
        self.container.add_navigation_button(self)


class Page(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller
        self.root = controller.root
        self.spotify_manager = controller.spotify_manager

        self.navigation_buttons = []
        self.elements = []

        self.selected_button_index = None
        self._setup = False

    @property
    def button_dict(self):
        return {
            "fg": "black",
            "font": ("Arial", 25, "bold"),
        }

    @property
    def grid_dict(self):
        return {"sticky": "nswe", "padx": 50, "pady": 50}

    @property
    def columns(self):
        return max(map(len, self.elements))

    @property
    def rows(self):
        return len(self.elements)

    def add_row(self, elements):
        self.elements.append(elements)

    def add_navigation_button(self, button):
        self.navigation_buttons.append(button)

    def reset_setup(self):
        self._setup = False
        self.navigation_buttons = []
        self.elements = []

    def show(self):
        if not self._setup:
            self.setup()
            self._setup = True

        grid_columns, grid_rows = self.root.grid_size()
        rowspan = int(grid_rows / self.rows)

        for row in range(self.rows):
            ok_row = row * rowspan
            row_elements = self.elements[row]
            columnspan = int(grid_columns / len(row_elements))
            for column in range(self.columns):
                if column >= len(row_elements):
                    continue
                ok_column = column * columnspan
                element = row_elements[column]
                element.grid(
                    column=ok_column,
                    row=ok_row,
                    columnspan=columnspan,
                    rowspan=rowspan,
                    **self.grid_dict,
                )

        self.tkraise()
        if len(self.navigation_buttons):
            self.navigation_buttons[0].focus_set()
            self.selected_button_index = 0

    def hide(self):
        for row in self.elements:
            for element in row:
                element.grid_forget()

    def navigate_up(self):
        self.selected_button_index = (self.selected_button_index - 1) % len(
            self.navigation_buttons
        )
        self.update_button_selection()

    def navigate_down(self):
        self.selected_button_index = (self.selected_button_index + 1) % len(
            self.navigation_buttons
        )
        self.update_button_selection()

    def update_button_selection(self):
        self.navigation_buttons[self.selected_button_index].focus_set()

    def key_pressed(self, event):
        pass


class GamePage(Page):
    def setup(self):
        self.active_playlist = self.spotify_manager.active_playlist
        self.player_buttons = []
        self.score_buttons = []
        self.player_colors = []
        self.game_status = "waiting"

        current_song = self.active_playlist.current_song_number
        total_songs = self.active_playlist.number_of_songs
        button_text = f"Song {current_song}/{total_songs}"
        button = Button(self.root, text=button_text, **self.button_dict)
        self.add_row([button])

        button = Button(self.root, text="Time", **self.button_dict)
        self.chronometer = Chronometer(button)
        self.answer_button = button
        self.add_row([button])

        self.player_button_dict = {
            "highlightbackground": "black",
            "highlightthickness": 10,
            "borderwidth": 0.9,
            "fg": "black",
            "font": ("Arial", 25, "bold"),
        }
        self.player_grid_dict = {"sticky": "nswe", "padx": 10, "pady": 10}
        row = []
        for player in range(self.controller.players):
            button = Button(self.root, text=f"P{player+1}", **self.player_button_dict)
            row.append(button)
            self.player_buttons.append(button)
            self.player_colors.append("black")
        self.add_row(row)

        row = []
        for player in range(self.controller.players):
            score = self.controller.scores[player]
            button = Button(self.root, text=f"{score}", **self.button_dict)
            self.score_buttons.append(button)
            row.append(button)
        self.add_row(row)

        button = Button(self.root, text="Quit", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("StartPage"))
        self.add_navigation_button(button)
        self.add_row([button])

    def show(self):
        Page.show(self)
        self.game_status = "playing"
        self.active_playlist.play()
        self.chronometer.start()

    def pause(self):
        self.game_status = "pause"
        self.chronometer.pause()
        self.active_playlist.pause()

    def wrong_answer(self):
        if self.game_status != "pause":
            return
        play_sound("./sounds/ko.mp3", True)
        sleep(1)
        self.add_wrong_answer_score()
        self.reset_player_buttons()
        self.active_playlist.resume()
        self.chronometer.resume()
        self.game_status = "playing"

    def display_answer(self):
        button_text = self.active_playlist.current_song.details
        self.answer_button.configure(text=button_text)

    def add_right_answer_score(self, complete=False):
        add_score = 10
        if self.chronometer.bonus:
            play_sound("./sounds/ok.mp3", True)
            add_score += self.chronometer.bonus
        if complete:
            play_sound("./sounds/ok.mp3", True)
            add_score += 5
        else:
            play_sound("./sounds/ok.mp3", True)
        self.update_scores(add_score)

    def add_wrong_answer_score(self):
        add_score = -5
        self.update_scores(add_score)

    def update_scores(self, to_add):
        for index, color in enumerate(self.player_colors):
            if color == "green":
                current_score = self.controller.scores[index]
                self.controller.scores[index] = max(0, current_score + to_add)
        for player in range(self.controller.players):
            score = self.controller.scores[player]
            self.score_buttons[player].configure(text=f"{score}")

    def go_next(self):
        if self.game_status not in ["score", "skip"]:
            return

        def next_action():
            if self.active_playlist.is_over:
                self.controller.frames["ScorePage"].reset_setup()
                self.controller.show_frame("ScorePage")
                self.controller.frames["SplashPage"].reset()
            else:
                self.active_playlist.next_song()
                self.controller.show_frame("SplashPage")
                self.controller.frames["SplashPage"].reset()

        self.after(1000, next_action)

    def right_answer(self):
        if self.game_status != "pause":
            return
        self.game_status = "score"
        self.active_playlist.resume()
        self.display_answer()
        self.add_right_answer_score()
        play_sound("./sounds/ok.mp3", True)

    def complete_answer(self):
        if self.game_status != "pause":
            return
        self.game_status = "score"
        self.active_playlist.resume()
        self.display_answer()
        self.add_right_answer_score(complete=True)

    def skip(self):
        if self.game_status != "playing":
            return
        self.game_status = "skip"
        self.chronometer.pause()
        self.display_answer()

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

        elif key == "u":
            self.complete_answer()

        elif key == "h":
            self.skip()

        elif key == "g":
            self.go_next()

    def answer_from_player(self, player):
        if self.game_status == "playing":
            if self.player_colors[player] != "red":
                self.player_colors[player] = "green"
                self.update_player_buttons()
                self.pause()

    def reset_player_buttons(self):
        for player in range(self.controller.players):
            self.player_colors[player] = "black"
        self.update_player_buttons()

    def update_player_buttons(self):
        for player in range(self.controller.players):
            color = self.player_colors[player]
            self.player_buttons[player].configure(highlightbackground=color)


class SplashPage(Page):
    @property
    def button_dict(self):
        return {
            "fg": "black",
            "font": ("Arial", 250, "bold"),
        }

    def setup(self):
        button = Button(self.root, text="", **self.button_dict)
        self.add_row([button])

        def action_1():
            self.controller.show_frame("GamePage")

        actions = [action_1]
        self.countdown = CountDown(button, actions, 6)
        self.countdown.start()

    def reset(self):
        self.countdown.reset()
        self.countdown.start()


class ScorePage(Page):
    def setup(self):
        button = Button(self.root, text="Final Result !", **self.button_dict)
        self.add_row([button])

        for player in range(self.controller.players):
            score = self.controller.scores[player]
            button_text = f"Player {player+1} - Score {score}"
            button = Button(self.root, text=button_text, **self.button_dict)
            self.add_row([button])

        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("StartPage"))
        self.add_row([button])
        self.add_navigation_button(button)


class StartPage(Page):
    def setup(self):
        button = Button(self.root, text="Start Game", **self.button_dict)
        button.bind(
            "<Return>", lambda event: self.controller.show_frame("PlaylistChoicePage")
        )
        self.add_row([button])
        self.add_navigation_button(button)

        button = Button(self.root, text="Settings", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("SettingPage"))
        self.add_row([button])
        self.add_navigation_button(button)

        # Last row
        button = Button(self.root, text="Quit", **self.button_dict)
        button.bind("<Return>", lambda event: self.root.destroy())
        self.add_row([button])
        self.add_navigation_button(button)


class ReadyPage(Page):
    def setup(self):
        self.ready = {"master": False}
        self.player_buttons = []

        button = Button(self.root, text="Ready ?", **self.button_dict)
        self.add_row([button])

        for player in range(self.controller.players):
            self.ready[player] = False

            button_text = f"Player {player+1} - Waiting Validation"
            button = Button(self.root, text=button_text, **self.button_dict)
            self.add_row([button])
            self.player_buttons.append(button)

        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("StartPage"))
        self.add_row([button])
        self.add_navigation_button(button)

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
            self.set_player_ready(player)
        elif key == "g":
            self.ready["master"] = True
            self.ready_to_run()

    def set_player_ready(self, index):
        if index in self.ready:
            self.ready[index] = True
            self.player_buttons[index].configure(text=f"Player {index+1} - Ready !")
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
        button = Button(self.root, text="Choose a playlist", **self.button_dict)
        self.add_row([button])

        index = 1
        for index_playlist, playlist in enumerate(self.spotify_manager.playlists):
            index += 1

            button_text = f"{playlist.name} - {playlist.number_of_songs} songs"
            button = Button(self.root, text=button_text, **self.button_dict)
            button.bind(
                "<Return>",
                lambda event, index_playlist=index_playlist: self.launch_ready_page(
                    index_playlist
                ),
            )
            self.add_navigation_button(button)
            self.add_row([button])

        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("StartPage"))
        self.add_navigation_button(button)
        self.add_row([button])

    def launch_ready_page(self, index):
        self.spotify_manager.set_playlist(index)
        self.controller.show_frame("ReadyPage")


class SettingPage(Page):
    def setup(self):
        button = Button(self.root, text="Players", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("PlayerPage"))
        self.add_row([button])
        self.add_navigation_button(button)

        # Second row
        button = Button(self.root, text="Log in to Spotify", **self.button_dict)
        button.bind("<Return>", lambda event: self.login_to_spotify())
        self.spotify_button = button
        self.add_row([button])
        self.add_navigation_button(button)

        # Third row
        button = Button(self.root, text="Please choose device", **self.button_dict)
        button.bind("<Return>", lambda event: self.update_device_list())
        self.device_button = button
        self.add_row([button])
        self.add_navigation_button(button)

        # Last row
        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("StartPage"))
        self.add_row([button])
        self.add_navigation_button(button)

    def login_to_spotify(self):
        if self.spotify_manager.check_login_status():
            user = self.spotify_manager.user
            name = user["id"]
            self.spotify_button.config(text=f"Logged in as - {name}")
        else:
            self.spotify_manager.login()
        self.spotify_manager.devices
        if self.spotify_manager.chosen_device:
            device_name = self.spotify_manager.chosen_device["name"]
            button3_text = f"Device : {device_name}"
            self.device_button.config(text=button3_text)

    def update_device_list(self):
        self.spotify_manager.devices
        self.controller.show_frame("DevicePage")


class PlayerPage(Page):
    def setup(self):
        button_text = f"Current Player : {self.controller.players}"
        button = Button(self.root, text=button_text, **self.button_dict)
        self.player_button = button
        self.add_row([button])

        button = Button(self.root, text="+", **self.button_dict)
        button.bind("<Return>", lambda event: self.add_player())
        self.add_navigation_button(button)
        self.add_row([button])

        button = Button(self.root, text="-", **self.button_dict)
        button.bind("<Return>", lambda event: self.del_player())
        self.add_navigation_button(button)
        self.add_row([button])

        # Last row
        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("SettingPage"))
        self.add_navigation_button(button)
        self.add_row([button])

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
        self.player_button.configure(text=button1_text)


class DevicePage(Page):
    def setup(self):
        # One row per device
        for device in self.spotify_manager.devices:
            name = device["name"]
            button = Button(self.root, text=name, **self.button_dict)
            button.bind(
                "<Return>", lambda event, device=device: self.set_device(device)
            )
            self.add_navigation_button(button)
            self.add_row([button])

        # Last row
        button = Button(self.root, text="Back", **self.button_dict)
        button.bind("<Return>", lambda event: self.controller.show_frame("SettingPage"))
        self.add_navigation_button(button)
        self.add_row([button])

    def set_device(self, device):
        self.spotify_manager.set_device(device)
        device_name = device["name"]
        button_text = f"Device : {device_name}"
        self.controller.frames["SettingPage"].device_button.config(text=button_text)
        self.controller.show_frame("SettingPage")
