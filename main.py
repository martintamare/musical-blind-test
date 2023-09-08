import config
from tkinter import *


class Page(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        self.parent = parent
        self.controller = controller

        self.buttons = []
        self.selected_button_index = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

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
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

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
        self.button1 = Button(root, text="S1", **self.button_dict)
        self.button1.bind(
            "<Return>", lambda event: self.controller.show_frame("GamePage")
        )
        self.buttons.append(self.button1)

        self.button2 = Button(root, text="Back", **self.button_dict)
        self.button2.bind(
            "<Return>", lambda event: self.controller.show_frame("StartPage")
        )
        self.buttons.append(self.button2)


class App:
    def __init__(self, root):
        self.root = root
        self._padx = 50
        self._pady = 50

        container = Frame(self.root)

        self.active_frame = None
        self.frames = {}
        for F in (StartPage, GamePage, SettingPage):
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
    root = Tk()
    root.geometry(
        f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}"
    )  # Default window size
    root.title = config.SCREEN_TITLE

    app = App(root)

    root.mainloop()
