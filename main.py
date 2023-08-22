import arcade
import config
from game.views import MainView


class MusicalBlindTest(arcade.Window):
    def __init__(self):
        super().__init__(
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,
            config.SCREEN_TITLE,
            resizable=True,
        )
        self.current_screen = None
        self.setup()

    def setup(self):
        self.current_screen = MainView(self)
        self.show_view(self.current_screen)

    def start_game(self):
        # Ici, vous pouvez ajouter le code pour démarrer le jeu, charger la musique, etc.
        pass


def main():
    game = MusicalBlindTest()
    arcade.run()


if __name__ == "__main__":
    main()
