"""handles processing a return"""
from tkinter import Entry, IntVar, Label, StringVar, Toplevel, messagebox
from tkinter.ttk import Button, Frame, Separator, Spinbox
from finalize_order_view import FinalizeOrderView

from app import App
from order_system import ItemQuantity


class ReturnScreen(Toplevel):
    """Return Screen GUI Window"""

    items: list[tuple[ItemQuantity, IntVar]]

    def __init__(self, app: App, parent: Toplevel, order_id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.title("Return Items")

        self.order = self.app.order_system.get_order_details_for_return(order_id)
        item_frame = Frame(self)
        self.items = []
        Label(item_frame, text="Name").grid(row=0, column=0)
        Label(item_frame, text="Quantity").grid(row=0, column=1)
        Label(item_frame, text="Subtotal").grid(row=0, column=2)
        Label(item_frame, text="GST").grid(row=0, column=3)
        Label(item_frame, text="PST").grid(row=0, column=4)
        Label(item_frame, text="Total").grid(row=0, column=5)
        Label(item_frame, text="Return Qty.").grid(row=0, column=6)

        Separator(item_frame, orient="horizontal").grid(
            row=1, column=0, columnspan=7, sticky="ew"
        )
        for i, item in enumerate(self.order.items, start=1):
            row = i * 2

            item_frame.rowconfigure(row, pad=5)
            Label(item_frame, text=item.name).grid(row=row, column=0)
            Label(item_frame, text=item.quantity).grid(row=row, column=1)
            Label(item_frame, text=f"{item.subtotal():.2f}").grid(row=row, column=2)
            Label(item_frame, text=f"{item.get_gst():.2f}").grid(row=row, column=3)
            Label(item_frame, text=f"{item.get_pst():.2f}").grid(row=row, column=4)
            Label(item_frame, text=f"{item.total():.2f}").grid(row=row, column=5)
            return_quantity = IntVar(value=0, name=f"QUANTITY_{i}")
            return_quantity.trace_add("write", self.update_totals)
            Spinbox(
                item_frame,
                from_=0,
                to=item.quantity,
                textvariable=return_quantity,
                width=8,
            ).grid(row=row, column=6)
            self.items.append((item, return_quantity))

            Separator(item_frame, orient="horizontal").grid(
                row=row + 1, column=0, columnspan=7, sticky="ew"
            )

        item_frame.pack()

        # Fields for subtotal, gst, pst, total
        self.total_frame = Frame(self)
        self.subtotal = StringVar()
        Label(self.total_frame, text="Subtotal").grid(row=0, column=0)
        Entry(self.total_frame, textvariable=self.subtotal, state="readonly").grid(
            row=0, column=1
        )

        self.gst = StringVar()
        Label(self.total_frame, text="GST").grid(row=1, column=0)
        Entry(self.total_frame, textvariable=self.gst, state="readonly").grid(
            row=1, column=1
        )

        self.pst = StringVar()
        Label(self.total_frame, text="PST").grid(row=2, column=0)
        Entry(self.total_frame, textvariable=self.pst, state="readonly").grid(
            row=2, column=1
        )

        self.total = StringVar()
        Label(self.total_frame, text="Total").grid(row=3, column=0)
        Entry(self.total_frame, textvariable=self.total, state="readonly").grid(
            row=3, column=1
        )

        self.total_frame.pack()
        Button(self, text="Finalize", command=self.process_return).pack()

    def update_totals(self, *_args):
        """Updates the subtotal, gst, pst, and total"""
        subtotal = 0.0
        gst = 0.0
        pst = 0.0
        for item, return_quantity in self.items:
            subtotal -= item.price * return_quantity.get()
            gst -= item.price * return_quantity.get() * item.gst * 0.05
            pst -= item.price * return_quantity.get() * item.pst * 0.06
        self.subtotal.set(f"{subtotal:.2f}")
        self.gst.set(f"{gst:.2f}")
        self.pst.set(f"{pst:.2f}")
        self.total.set(f"{subtotal + gst + pst:.2f}")

    def process_return(self):
        """Attempts to process the return"""
        # Get returned item ids and quantities
        returned_items = []
        for item, return_quantity in self.items:
            if return_quantity.get() > 0:
                returned_items.append((item.item_id, return_quantity.get()))

        # Check that at least one item is returned, otherwise show an error
        if len(returned_items) > 0:
            order_id = self.app.order_system.new_return_order(1, self.order.order_id)
            for item_id, quantity in returned_items:
                self.app.order_system.set_order_item(order_id, item_id, -quantity)
            FinalizeOrderView(self.app, order_id).bind("<<Finalized>>", self.handle_finalize)
        else:
            messagebox.showerror(
                "No Items To Return", "Please add items to the return!"
            )
    def handle_finalize(self, _evt):
        """Handles the finalized event

        Args:
            _evt (_type_): unused event parameter
        """
        self.destroy()
        self.parent.deiconify()
