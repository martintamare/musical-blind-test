import arcade


class StartScreen(arcade.View):
    def on_show(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        arcade.start_render()
        # Affichez ici le texte ou les images pour l'écran de démarrage

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        # Vous pouvez utiliser ceci pour gérer les clics sur les boutons de démarrage
        pass
