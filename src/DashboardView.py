from tkinter import LEFT, RIDGE, TOP, Button, Frame, Label, PhotoImage, Tk
from typing import Optional
from LoginScreen import LoginScreen
from OrderView import OrderView
from InventoryView import InventoryView
from ReportsView import ReportsView
from app import App
from PIL import Image, ImageTk

from search_order_screen import SearchOrderScreen


class DashboardView(Tk):
    order_view: Optional[OrderView]
    search_screen: Optional[SearchOrderScreen]
    inventory_view: Optional[InventoryView]
    reports_view: Optional[ReportsView]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1200x700")
        self.app = App()

        self.title("Retail Billing System  |  By Team_23")
        self.config(bg="sienna")

        self.top_frame = Frame(self, bg="sienna")
        self.top_frame.pack(fill="both")
        # Create a title label with an image
        self.icon_title = PhotoImage(file="images/icons1.png")

        # Place the title label with text and image on the window
        Label(
            self.top_frame,
            text="Retail Billing System",
            image=self.icon_title,
            compound=LEFT,
            font=("algerian", 25, "bold"),
            bg="sienna",
            fg="white",
            anchor="w",
        ).pack(side="left")

        # Create a "SignOut" button
        Button(
            self.top_frame,
            text="SignOut",
            bg="white",
            font=("times new roman", 15, "bold"),
            cursor="hand2",
        ).pack(anchor="center", side="right", padx=20)

        self.clock_frame = Frame(self, bg="#4d636d")
        self.clock_frame.pack(fill="x")

        Label(
            self.clock_frame,
            text="Retail Billing System | By Team_23",
            font=("times new roman", 15, "bold"),
            bg="#4d636d",
            fg="white",
        ).pack()

        # Create a left frame for the menu
        self.retailLogo = Image.open("images/OIP.jpg")
        # resizes the image with height and width
        self.retailLogo = self.retailLogo.resize((1280, 330), Image.Resampling.LANCZOS)
        self.retailLogo = ImageTk.PhotoImage(self.retailLogo)

        leftmenu = Frame(self, bd=2, relief=RIDGE, bg="CORAL")
        # Place the left menu frame at the specified position and dimensions
        leftmenu.pack()

        # Create a label to display the menu image
        lbl_menu = Label(leftmenu, image=self.retailLogo)
        lbl_menu.pack(side=TOP, fill="x")

        # Create a label for the menu title
        self.icon2 = PhotoImage(file="images/icon2.png")
        Label(
            leftmenu, text="Welcome", font=("ALGERIAN", 20), bg="#4d636d", fg="white"
        ).pack(side=TOP, fill="x")

        self.button_frame = Frame(self, bg="sienna")
        self.button_frame.pack(fill="x", expand=True)
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.grid_columnconfigure(3, weight=1)

        order_button = Button(
            self.button_frame,
            text="New Order",
            command=self.open_order_view,
            background="#4d636d",
            relief="flat",
            image=self.icon2,
            compound=LEFT,
            anchor="w",
            font="algerian",
            width=170,
            height=41,
        )
        order_button.grid(row=0, column=0)

        search_button = Button(
            self.button_frame,
            text="Search Order",
            command=self.open_search_view,
            background="#4d636d",
            relief="flat",
            image=self.icon2,
            compound=LEFT,
            anchor="w",
            font="algerian",
            width=170,
            height=41,
        )
        search_button.grid(row=0, column=1)

        inventory_button = Button(
            self.button_frame,
            text="Inventory",
            command=self.open_inventory_view,
            background="#4d636d",
            relief="flat",
            image=self.icon2,
            compound=LEFT,
            anchor="w",
            font="algerian",
            width=170,
            height=41,
        )
        inventory_button.grid(row=0, column=2)

        reports_button = Button(
            self.button_frame,
            text="Reports",
            command=self.create_reports_view,
            background="#4d636d",
            relief="flat",
            image=self.icon2,
            compound=LEFT,
            anchor="w",
            font="algerian",
            width=170,
            height=41,
        )
        reports_button.grid(row=0, column=3)

        # Show the login screen and hide the dashboard
        self.login_view = LoginScreen(self.app, self)
        self.withdraw()

        # Register a callback for the login window being closed
        self.login_view.protocol("WM_DELETE_WINDOW", self.handle_login_window_close)

    def handle_login_window_close(self):
        """Handle the login window being closed without the use logging in"""
        # Allow the program to exit
        self.login_view.destroy()
        self.destroy()

    def open_order_view(self):
        """Opens an order view, and hides the dashboard"""
        self.withdraw()
        self.order_view = OrderView(self.app, self)

    def open_search_view(self):
        """Opens a search order screen, and hides the dashboard"""
        self.withdraw()
        self.search_screen = SearchOrderScreen(self.app, self)

    def open_inventory_view(self):
        """Opens an inventory view, and hides the dashboard"""
        self.withdraw()
        self.inventory_view = InventoryView(self.app, self)

    def create_reports_view(self):
        """Opens a reports view, and hides the dashboard"""
        self.withdraw()
        self.reports_view = ReportsView(self.app, self)


if __name__ == "__main__":
    root = DashboardView()
    root.mainloop()
