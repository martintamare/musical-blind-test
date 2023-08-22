import arcade
import arcade.gui


class MainView(arcade.View):
    """Welcome Screen."""

    def __init__(self, window):
        super().__init__()

        self.window = window

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self._buttons = []
        self._active_button = None

        # BoxGroup for buttons
        self.v_box = arcade.gui.UIBoxLayout()

        start_new_game_button = arcade.gui.UIFlatButton(
            text="Start New Game", width=320
        )
        self._buttons.append(start_new_game_button)
        self.v_box.add(start_new_game_button.with_space_around(bottom=20))

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=320)
        self._buttons.append(settings_button)
        self.v_box.add(settings_button.with_space_around(bottom=20))

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=320)
        self._buttons.append(exit_button)
        self.v_box.add(exit_button)

        @exit_button.event("on_click")
        def on_click_exit(event):
            print(event)
            print(vars(event))
            arcade.exit()

        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", child=self.v_box
            )
        )

    def on_key_press(self, symbol, modifier):
        if symbol == arcade.key.UP:
            self.previous_button()
        elif symbol == arcade.key.DOWN:
            self.next_button()
        elif symbol == arcade.key.ENTER:
            self.enter_button()

    def previous_button(self):
        if self._active_button is None:
            self._active_button = 0
        else:
            self._active_button = (self._active_button - 1) % len(self._buttons)
        self.activate_button()

    def next_button(self):
        if self._active_button is None:
            self._active_button = 0
        else:
            self._active_button = (self._active_button + 1) % len(self._buttons)
        self.activate_button()

    def activate_button(self):
        for i in range(len(self._buttons)):
            hover = False
            if i == self._active_button:
                hover = True
            self._buttons[i].hovered = hover

    def enter_button(self):
        if self._active_button is None:
            return

        for i in range(len(self._buttons)):
            press = False
            if i == self._active_button:
                press = True
            self._buttons[i].pressed = press

        current_button = self._buttons[self._active_button]
        print(current_button)
        self.manager.dispatch_ui_event(
            "on_click",
            arcade.gui.UIMousePressEvent(0, 0, button=arcade.MOUSE_BUTTON_LEFT),
        )

    def on_show(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

    def on_draw(self):
        self.clear()
        self.manager.draw()
