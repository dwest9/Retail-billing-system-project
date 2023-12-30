from tkinter import Tk, Toplevel
from tkinter.ttk import Treeview
from tkinter import *

from app import App
from inventory_count_screen import InventoryCountScreen
from inventory_adjustment_screen import InventoryAdjustmentScreen


class InventoryView(Toplevel):
    "Window for viewing inventory levels"

    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.geometry("1000x600")
        self.title("Inventory Management")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)

        self.report = self.app.inventory_system.get_inventory_details()

        button_frame = Frame(self)

        Button(button_frame, text="Input Count", command=self.open_count_screen).grid(
            row=0, column=0
        )
        Button(
            button_frame, text="Create Adjustment", command=self.open_adjustment_screen
        ).grid(row=0, column=1)

        button_frame.grid(row=0, column=0)

        self.headings = (
            "ID",
            "Sold Today",
            "Sold This Month",
            "Total Sold",
            "Theoretical Quantity",
            "Actual Quantity",
            "Difference"
        )
        self.item_list = Treeview(self, columns=self.headings, selectmode="browse")

        self.item_list.heading("#0", text="Item Name")
        self.item_list.heading(
            0, text="ID", command=lambda: self.sort_tree("ID")
        )
        self.item_list.heading(
            1, text="Sold Today", command=lambda: self.sort_tree("Sold Today")
        )
        self.item_list.heading(
            2, text="Sold This Month", command=lambda: self.sort_tree("Sold This Month")
        )
        self.item_list.heading(
            3, text="Sold since last count", command=lambda: self.sort_tree("Total Sold")
        )
        self.item_list.heading(
            4, text="Theoretical Quantity", command=lambda: self.sort_tree("Theoretical Quantity")
        )
        self.item_list.heading(
            5, text="Actual Quantity", command=lambda: self.sort_tree("Actual Quantity"),
        )
        self.item_list.heading(
            6, text="Difference", command=lambda: self.sort_tree("Difference"),
        )

        self.item_list.column("#0", width=100)
        self.item_list.column(0, width=75)
        self.item_list.column(1, width=75)
        self.item_list.column(2, width=75)
        self.item_list.column(3, width=75)
        self.item_list.column(4, width=75)
        self.item_list.column(5, width=75)
        self.item_list.column(6, width=75)

        # self.insert_data()

        self.item_list.grid(row=1, column=0, sticky="nesw")
        # create a dicitonary to store order for each colunmn
        self.sort_order = {
            "ID": None,
            "Item Name": None,
            "Sold Today": None,
            "Sold This Month": None,
            "Actual Quantity": None,
            "Theoretical Quantity": None,
            "Total Sold": None,
            "Difference": None
        }

        self.insert_data()

        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def insert_data(self):
        "Inserts data into the window in tabular form"
        report = self.app.inventory_system.get_inventory_details()
        counts = self.app.inventory_system.list_inventory_counts()
        counts = self.app.inventory_system.get_count_details(counts[-1].count_id)

        
        self.item_list.delete(*self.item_list.get_children())
        for i, item in enumerate(report, start=0):
            theoretical_inventory = counts[i].previous_quantity - item.quantity_sold +item.adjustment_quantity
            actual_inventory = item.count_quantity - item.quantity_sold + item.adjustment_quantity
            self.item_list.insert(
                "",
                "end",
                text=item.name,
                values=(
                    item.item_id,
                    item.day_quantity,
                    item.month_quantity,
                    item.quantity_sold,
                    theoretical_inventory,
                    actual_inventory,
                    theoretical_inventory - actual_inventory,
                )
            )
            

    def sort_tree(self, column):
        """Sort item in descending and ascending order"""

        # Get data and toggle sorting order
        data = [
            (self.item_list.set(child, column), child)
            for child in self.item_list.get_children("")
        ]

        if self.sort_order[column] is None or self.sort_order[column] == "asc":
            data.sort(key=lambda x: (self.sort_key(x[0]), x[0]), reverse=True)
            self.sort_order[column] = "desc"
        else:
            data.sort(key=lambda x: (self.sort_key(x[0]), x[0]))
            self.sort_order[column] = "asc"

        for index, item in enumerate(data):
            self.item_list.move(item[1], "", index)

    def sort_key(self, value):
        """Check the value is integer or not"""
        try:
            return int(value)
        except ValueError:
            return value

    def open_count_screen(self):
        "Opens the inventory count screen"
        InventoryCountScreen(self.app, self)

    def open_adjustment_screen(self):
        "Opens the inventory adjustment screen"
        InventoryAdjustmentScreen(self.app, self)

    def window_close(self):
        "Handles the closing of the inventory window"
        self.parent.deiconify()
        self.destroy()
