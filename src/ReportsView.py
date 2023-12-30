from tkinter import *

from app import App


class ReportsView(Toplevel):
    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.geometry("600x300")
        self.title("Reports")
        Label(self, text="Not Yet Implemented").pack()

        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def window_close(self):
        self.parent.deiconify()
        self.destroy()
