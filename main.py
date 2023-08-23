import config
from tkinter import *


class App:
    def __init__(self, root):
        self.root = root
        self._padx = 50
        self._pady = 50

        self.main_frame = None
        self.setup_main_frame()

    def setup_main_frame(self):
        Grid.columnconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 0, weight=1)
        Grid.rowconfigure(root, 1, weight=1)
        Grid.rowconfigure(root, 2, weight=1)

        button_dict = {"bg": "#22cbff", "fg": "black", "font": ("Arial", 25, "bold")}
        grid_dict = {"sticky": "nswe", "padx": 50, "pady": 50}

        self.button1 = Button(root, text="Start Game", **button_dict)
        self.button1.grid(column=0, row=0, **grid_dict)

        self.button2 = Button(root, text="Settings", **button_dict)
        self.button2.grid(column=0, row=1, **grid_dict)

        self.button3 = Button(root, text="Quit", **button_dict)
        self.button3.grid(column=0, row=2, **grid_dict)

        root.bind("<Configure>", self.on_window_resize)

    def on_window_resize(self, event):
        width = event.width
        height = event.height
        padx = int(width / 4)
        pady = int(height / 4)
        self.button1.config(padx=padx, pady=pady)
        self.button2.config(padx=padx, pady=pady)
        self.button3.config(padx=padx, pady=pady)
        print(f"Window resized to {width}x{height} {padx}x{pady}")

    def show_settings_screen(self):
        self.main_frame.pack_forget()

        self.settings_frame = Frame(self.root)
        self.settings_frame.pack(fill=BOTH, expand=1)

        for i in range(1, 5):
            btn = Button(self.settings_frame, text=str(i))
            btn.pack(fill=X, pady=self.root.winfo_height() * 0.2)

        # Bind key to return to the main screen
        self.settings_frame.bind(
            "<Escape>", lambda e: self.return_to_main_screen(self.settings_frame)
        )

    def return_to_main_screen(self, frame):
        frame.pack_forget()
        self.main_frame.pack(fill=BOTH, expand=1)

    def navigate_up(self, event):
        self.selected_button_index = (self.selected_button_index - 1) % len(
            self.buttons
        )
        self.update_button_selection()

    def navigate_down(self, event):
        self.selected_button_index = (self.selected_button_index + 1) % len(
            self.buttons
        )
        self.update_button_selection()

    def select_option(self, event):
        self.buttons[self.selected_button_index].invoke()

    def update_button_selection(self):
        for btn in self.buttons:
            btn.config(relief=RAISED)
        self.buttons[self.selected_button_index].config(relief=SUNKEN)


if __name__ == "__main__":
    root = Tk()
    root.geometry(
        f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}"
    )  # Default window size
    root.title = config.SCREEN_TITLE

    app = App(root)

    root.mainloop()
