from tkinter import (
    Button,
    Checkbutton,
    Frame,
    IntVar,
    Tk,
    Toplevel,
    ttk,
)
from FinalizeOrderView import FinalizeOrderView
from OrderDetailsFrame import OrderDetailsFrame
from app import App


class OrderView(Toplevel):
    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("1000x500")
        self.title("New Order")
        self.parent = parent
        self.app = app

        self.add = True
        self.categories = self.app.get_all_categories()
        self.order_id = self.app.order_system.new_order(1)

        width = 6  # how many buttons across?
        self.category_tabs = ttk.Notebook(self)
        self.item_frames = []

        # Add all the category tabs
        for category_name, category_items in self.categories.items():
            category_frame = Frame(self.category_tabs)
            category_frame.pack(fill="both", expand=True)
            self.category_tabs.add(category_frame, text=category_name)
            for i in range(width):
                category_frame.grid_columnconfigure(i, weight=1)
            for i, item in enumerate(category_items):
                Button(
                    category_frame,
                    text=item.name,
                    command=lambda id=item.id: self.item_button(id),
                ).grid(row=i // width, column=i % width, sticky="nesw")
        self.category_tabs.pack(side="left", fill="both", expand=True)

        self.order_details = OrderDetailsFrame(self)
        self.order_details.pack(side="left", fill="both")

        self.remove_mode = IntVar()
        Checkbutton(
            self.order_details, text="Remove Mode", variable=self.remove_mode
        ).grid(row=5, column=0, columnspan=2)

        Button(
            self.order_details,
            text="Finalize",
            command=lambda: FinalizeOrderView(self.app, self, self.order_id),
        ).grid(row=6, column=0, columnspan=2)

        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def item_button(self, item_id: int):
        """Handle item button pressed, either adding or removing an item

        Args:
            item_id (int): id of item to modify
        """
        if self.remove_mode.get() == 0:
            self.app.order_system.add_order_item(self.order_id, item_id)
        else:
            self.app.order_system.remove_order_item(self.order_id, item_id)
        self.order_details.update_order_details(
            self.app.order_system.get_order_details(self.order_id)
        )

    def window_close(self):
        """Handles window close event"""
        self.parent.deiconify()
        self.destroy()
