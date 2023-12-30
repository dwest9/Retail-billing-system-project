"""Handles the login screen"""
from tkinter import Button, Entry, Frame, Label, StringVar, Tk, Toplevel

from app import App


class LoginScreen(Toplevel):
    """Window implementing login functionality"""

    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, background="RoyalBlue", **kwargs)
        self.title("Login")
        self.geometry("960x540")
        self.app = app
        self.parent = parent

        self.content_frame = Frame(self, padx=20, pady=20)
        self.content_frame.pack(expand=True, side="bottom")

        # Main Welcome label
        Label(self.content_frame, text="Sign In", font=("TkDefaultFont", 20)).pack()

        self.err_label = StringVar()
        self.error_label = Label(self.content_frame, textvariable=self.err_label)
        self.error_label.pack()

        # Username entry
        self.usr = StringVar()
        self.usr.set("")
        Label(self.content_frame, text="Username:").pack(pady=5)
        self.user_entry = Entry(self.content_frame, textvariable=self.usr, width=30)
        self.user_entry.pack(pady=5)

        # Password entry
        self.pw = StringVar()
        self.pw.set("")
        Label(self.content_frame, text="Password:").pack(pady=5)
        self.pw_entry = Entry(
            self.content_frame, textvariable=self.pw, width=30, show="*"
        )
        self.pw_entry.pack(pady=5)
        self.pw_entry.bind("<Return>", self.handle_login)

        Button(
            self.content_frame,
            text="Sign In",
            padx=10,
            pady=5,
            command=self.handle_login,
        ).pack(pady=5)

    def handle_login(self, _evt=None):
        """Handles the user login attempt

        Args:
            _evt (_type_, optional): unused event parameter. Defaults to None.
        """
        if not self.usr.get() and not self.pw.get():
            self.err_label.set("Missing username and password")
            self.bell()
        elif not self.usr.get():
            self.err_label.set("Missing username")
            self.bell()
        elif not self.pw.get():
            self.err_label.set("Missing password")
            self.bell()
        else:
            user = self.app.login(self.usr.get(), self.pw.get())
            if user is not None:
                self.destroy()
                self.parent.deiconify()
            else:
                self.err_label.set("Incorrect user or password")
                self.bell()
                self.usr.set("")
                self.pw.set("")
