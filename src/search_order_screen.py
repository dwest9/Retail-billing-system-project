"""Contains the search order window"""
from tkinter import (
    Event,
    Frame,
    StringVar,
    Tk,
    Toplevel,
    messagebox,
)
from tkinter import ttk
from typing import Optional
from order_details_frame import OrderDetailsFrame
from app import App
from customer_system import CustomerOrder
from return_screen import ReturnScreen


class SearchOrderScreen(Toplevel):
    """Window allowing a user to search for orders"""

    order_id: Optional[int]

    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.geometry("1000x600")
        self.title("Search Order")
        self.order_id = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # User inputs contained in their own frame
        self.input_frame = Frame(self)
        self.input_frame.grid(row=0, column=0)
        search_types = [
            "Order Number",
            "Customer Name",
            "Customer Email",
            "Customer Phone",
        ]
        self.search_type = StringVar(value=search_types[0])

        ttk.Label(self.input_frame, text="Search By").grid(row=0, column=0)
        ttk.OptionMenu(
            self.input_frame, self.search_type, search_types[0], *search_types
        ).grid(row=0, column=1)
        self.search_text = ttk.Entry(self.input_frame)
        self.search_text.grid(row=0, column=3)
        self.search_text.bind("<Return>", self.handle_search)

        ttk.Button(self.input_frame, text="Search", command=self.handle_search).grid(
            row=0, column=4
        )

        # Main order list
        self.order_list = ttk.Treeview(
            self,
            columns=(
                "name",
                "phone",
                "email",
                "payment_type",
                "cashier",
                "timestamp",
                "subtotal",
                "total",
            ),
            selectmode="browse",
        )
        self.order_list.heading("#0", text="#")
        self.order_list.heading(0, text="Name")
        self.order_list.heading(1, text="Email")
        self.order_list.heading(2, text="Phone")
        self.order_list.heading(3, text="Payment")
        self.order_list.heading(4, text="Cashier")
        self.order_list.heading(5, text="Time")
        self.order_list.heading(6, text="Subtotal")
        self.order_list.heading(7, text="Total")

        self.order_list.column("#0", width=50)
        self.order_list.column(0, width=80)
        self.order_list.column(1, width=100)
        self.order_list.column(2, width=75)
        self.order_list.column(3, width=50)
        self.order_list.column(4, width=50)
        self.order_list.column(5, width=100)
        self.order_list.column(6, width=50)
        self.order_list.column(7, width=50)

        self.order_list.bind("<<TreeviewSelect>>", self.handle_order_selection)

        self.order_list.grid(row=1, column=0, sticky="nesw")

        self.order_details = OrderDetailsFrame(self)
        self.order_details.grid(row=0, column=1, rowspan=2, sticky="nesw")

        self.return_button = ttk.Button(
            self.order_details,
            state="disabled",
            text="Return Items",
            command=self.open_return_screen,
        )
        self.return_button.grid(row=6, column=0, columnspan=2)

        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def open_return_screen(self):
        """Handles opening the return screen"""
        if self.order_id is not None:
            ReturnScreen(self.app, self, self.order_id)
        else:
            messagebox.showerror("No Order Selected", "Please select an order")

    def search_order_number(self):
        """Handles searching by order number"""
        try:
            order_number = int(self.search_text.get())
            order = self.app.customer_system.get_customer_order_by_id(order_number)
            if order is None:
                messagebox.showinfo(
                    "No Order Found",
                    f"No order with number '{order_number}' found.",
                )
            else:
                self.add_customer_orders([order])

        except ValueError as _e:
            messagebox.showerror(
                "Invalid Order Number",
                f"'{self.search_text.get()}' is not a valid order number.",
            )

    def handle_search(self, _evt: Optional[Event] = None):
        """Handles searching based on user input

        Args:
            _evt (Optional[Event], optional): Unused event parameter. Defaults to None.
        """
        self.reset_order_summaries()
        search_text = self.search_text.get()
        if self.search_type.get() == "Order Number":
            self.search_order_number()
        elif self.search_type.get() == "Customer Name":
            orders = self.app.customer_system.search_orders_by_name(
                self.search_text.get()
            )
            if len(orders) == 0:
                messagebox.showinfo(
                    "No Orders Found",
                    f"No orders found matching a customer name of '{self.search_text.get()}'.",
                )
            self.add_customer_orders(orders)
        elif self.search_type.get() == "Customer Email":
            orders = self.app.customer_system.search_orders_by_email(
                self.search_text.get()
            )
            if len(orders) == 0:
                messagebox.showinfo(
                    "No Orders Found",
                    f"No orders found matching a customer email of '{self.search_text.get()}'.",
                )
            self.add_customer_orders(orders)

        elif self.search_type.get() == "Customer Phone":
            orders = self.app.customer_system.search_orders_by_phone_number(search_text)
            if len(orders) == 0:
                messagebox.showinfo(
                    "No Orders Found",
                    f"No orders found matching a customer phone number of '{search_text}'.",
                )
            self.add_customer_orders(orders)

    def reset_order_summaries(self):
        """Empties the order list"""
        self.order_list.delete(*self.order_list.get_children())

    def add_customer_orders(self, customer_orders: list[CustomerOrder]):
        """Adds orders to the order list

        Args:
            customer_orders (list[CustomerOrder]): List of orders to add
        """
        for order in customer_orders:
            self.order_list.insert(
                "",
                "end",
                text=str(order.order_id),
                values=(
                    order.customer_name,
                    order.email,
                    order.phone_number,
                    order.payment_type,
                    order.cashier,
                    order.timestamp,
                    f"{order.subtotal:.2f}",
                    f"{order.subtotal + order.gst_total + order.pst_total:.2f}",
                ),
            )

    def handle_order_selection(self, _evt: Event):
        """Handles an order selection event by displaying order details

        Args:
            _evt (Event): unused event parameter
        """
        self.return_button.config(state="normal")
        self.order_id = int(self.order_list.item(self.order_list.focus())["text"])
        order = self.app.order_system.get_order_details(self.order_id)
        self.order_details.update_order_details(order)

    def window_close(self):
        """Handles window close event"""
        self.parent.deiconify()
        self.destroy()
