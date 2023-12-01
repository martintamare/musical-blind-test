from tkinter import Frame
from .spotify import SpotifyManager
from .views import (
    StartPage,
    PlaylistChoicePage,
    SettingPage,
    DevicePage,
    PlayerPage,
    ReadyPage,
    GamePage,
    SplashPage,
    ScorePage,
)
from utils import play_sound


class App:
    def __init__(self, root):
        self.root = root
        self._padx = 50
        self._pady = 50
        self.spotify_manager = SpotifyManager()
        self.players = 2
        self.reset_score()

        container = Frame(self.root)
        for column in range(3 * 4):
            root.columnconfigure(column, weight=1)
        for row in range(3 * 4):
            root.rowconfigure(row, weight=1)

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

        self.root.bind("<Up>", lambda event: self.navigate_up())
        self.root.bind("<Down>", lambda event: self.navigate_down())
        self.root.bind("<KeyPress>", lambda event: self.key_pressed(event))

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
        if page_name in ["ReadyPage", "GamePage"]:
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
