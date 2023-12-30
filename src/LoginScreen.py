from tkinter import Button, Entry, Label, StringVar, Tk, Toplevel

from app import App


class LoginScreen(Toplevel):
    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent

        # Main Welcome label
        Label(self, text="Welcome!").grid(row=0, column=0, columnspan=2)

        self.err_label = StringVar()
        self.error_label = Label(self, textvariable=self.err_label)
        self.error_label.grid(row=1, column=0, columnspan=2)

        # Username entry
        self.usr = StringVar()
        self.usr.set("")
        Label(self, text="Username:").grid(row=2, column=0)
        Entry(self, textvariable=self.usr, width=30).grid(row=2, column=1)

        # Password entry
        self.pw = StringVar()
        self.pw.set("")
        Label(self, text="Password:").grid(row=3, column=0)
        self.pw_entry = Entry(self, textvariable=self.pw, width=30, show="*")
        self.pw_entry.grid(row=3, column=1)
        self.pw_entry.bind("<Return>", self.handle_login)

        Button(self, text="sign In", command=self.handle_login).grid(
            row=4, column=0, columnspan=2
        )

    def handle_login(self, _evt=None):
        """Handles the user login attempt

        Args:
            _evt (_type_, optional): unused event parameter. Defaults to None.
        """
        user = self.app.login(self.usr.get(), self.pw.get())
        if user is not None:
            self.destroy()
            self.parent.deiconify()
        else:
            self.err_label.set("Incorrect user or password")
            self.bell()
            self.usr.set("")
            self.pw.set("")
