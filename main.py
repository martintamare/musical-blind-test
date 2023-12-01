import config
from tkinter import Tk
from dotenv import load_dotenv
from models import App


if __name__ == "__main__":
    load_dotenv()
    root = Tk()
    root.geometry(
        f"{config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}+10+10"
    )  # Default window size
    root.title = config.SCREEN_TITLE

    app = App(root)

    root.mainloop()
