import arcade
import config
from game.screens import StartScreen


class MusicalBlindTest(arcade.Window):
    def __init__(self):
        super().__init__(config.SCREEN_WIDTH, config.SCREEN_HEIGHT, config.SCREEN_TITLE)
        self.current_screen = None

    def setup(self):
        # Créer et montrer l'écran de démarrage
        self.current_screen = StartScreen(self)
        self.show_view(self.current_screen)

    def start_game(self):
        # Ici, vous pouvez ajouter le code pour démarrer le jeu, charger la musique, etc.
        pass


def main():
    game = MusicalBlindTest()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
