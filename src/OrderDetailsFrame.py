from tkinter import Entry, Frame, Label, StringVar
from tkinter.ttk import Treeview

from orderSystem import Order


class OrderDetailsFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.order_details = Treeview(self, columns=("qty", "price"))
        self.order_details.column(0, width=75)
        self.order_details.column(1, width=75)
        self.order_details.heading("#0", text="Item")
        self.order_details.heading(0, text="Qty")
        self.order_details.heading(1, text="Price")
        self.order_details.grid(row=0, column=0, columnspan=2, sticky="nesw")

        Label(self, text="Subtotal").grid(row=1, column=0)
        self.subtotal = StringVar()
        Entry(self, textvariable=self.subtotal, state="readonly").grid(row=1, column=1)
        self.gst = StringVar()
        Label(self, text="GST").grid(row=2, column=0)
        Entry(self, textvariable=self.gst, state="readonly").grid(row=2, column=1)

        self.pst = StringVar()
        Label(self, text="PST").grid(row=3, column=0)
        Entry(self, textvariable=self.pst, state="readonly").grid(row=3, column=1)

        self.total = StringVar()
        Label(self, text="Total").grid(row=4, column=0)
        Entry(self, textvariable=self.total, state="readonly").grid(row=4, column=1)

    def update_order_details(self, order_details: Order):
        """Updates this order details frame

        Args:
            order_details (Order): order details to display
        """
        self.order_details.delete(*self.order_details.get_children())
        subtotal = 0.0
        gst = 0.0
        pst = 0.0
        for item in order_details.items:
            self.order_details.insert(
                "",
                "end",
                text=item.name,
                values=(item.quantity, f"${item.quantity * item.price:.2f}"),
            )
            subtotal += item.quantity * item.price
            gst += item.quantity * item.price * 0.05 * item.gst
            pst += item.quantity * item.price * 0.06 * item.gst
            print(item)
        self.subtotal.set(f"{subtotal:.2f}")
        self.gst.set(f"{gst:.2f}")
        self.pst.set(f"{pst:.2f}")
        self.total.set(f"{subtotal + gst + pst:.2f}")
