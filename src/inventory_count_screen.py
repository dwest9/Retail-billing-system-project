from tkinter import (
    Button,
    Entry,
    Frame,
    Label,
    IntVar,
    Tk,
    Toplevel,
    messagebox,
    Scrollbar,
    Canvas,
)

from app import App


class InventoryCountScreen(Toplevel):
    "Screen for inputting inventory count"

    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.geometry("250x350")
        self.title("Inventory Count")

        self.report = self.app.inventory_system.get_inventory_details()

        container = Frame(self)
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)

        frame = Frame(canvas)
        frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, width=100)

        label_frame = Frame(self)
        Label(label_frame, text="Item Name").grid(row=0, column=0)
        Button(label_frame, text="Submit", command=self.handle_submit).grid(
            row=0, column=1
        )

        self.items = []
        for i, item in enumerate(self.report, start=1):
            Label(frame, text=item.name).grid(row=i, column=0)
            count = IntVar(value=item.count_quantity, name=f"COUNT_{i}")
            Entry(frame, textvariable=count, width=6).grid(row=i, column=1)
            self.items.append((item, count))

        label_frame.pack()
        container.pack()
        canvas.pack(side="left", fill="both", expand=False)
        scrollbar.pack(side="right", fill="y")

    def handle_submit(self):
        "Handles the submission of the inventory count"
        count_id = self.app.inventory_system.create_count()
        for item, count in self.items:
            if count.get() < 0:
                messagebox.showerror("Error", "Negative values not accepted.")
                return
            self.app.inventory_system.set_item_in_count(
                count_id, item.item_id, count.get()
            )
        messagebox.showinfo("Success", "Item count successfully submitted.")
        self.window_close()

    def window_close(self):
        "Handles closing the window"
        self.parent.insert_data()
        self.parent.deiconify()
        self.destroy()
