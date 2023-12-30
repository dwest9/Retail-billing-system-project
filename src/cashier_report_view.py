"""Contains implementation of a view displaying a cashier sales report"""
from tkinter import ttk

from report_system import CashierRow


class CashierReportView(ttk.Treeview):
    """Treeview for displaying cashier sales data"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(
            columns=("Num Orders", "Num Items", "Subtotal", "GST", "PST", "Total")
        )

        self.heading(0, text="Num Orders")
        self.heading(1, text="Num Items")
        self.heading(2, text="Subtotal")
        self.heading(3, text="GST")
        self.heading(4, text="PST")
        self.heading(5, text="Total")

        self.column(0, width=100)
        self.column(1, width=100)
        self.column(2, width=100)
        self.column(3, width=100)
        self.column(4, width=100)
        self.column(5, width=100)

    def clear_report(self):
        """Clears the treeview"""
        self.delete(*self.get_children())

    def display_new_report(self, cashier_sales_rows: list[CashierRow]):
        """Clears the treeview and displays a new report

        Args:
            cashier_sales_rows (list[CashierRow]): cashier sales records of the new report
        """
        self.clear_report()

        # Group item sales by category
        cashier_sales: dict[int, list[CashierRow]] = {}
        for row in cashier_sales_rows:
            cashier_sales[row.user_id] = cashier_sales.get(row.user_id, []) + [row]

        for cashier in cashier_sales.values():
            identifier = self.insert("", "end", text=cashier[0].username, open=True)
            num_orders = 0
            num_items = 0
            subtotal = 0.0
            gst_total = 0.0
            pst_total = 0.0
            for row in cashier:
                self.insert(
                    identifier,
                    "end",
                    text=row.payment_type,
                    values=(
                        row.num_orders,
                        row.num_items,
                        f"{row.subtotal:.2f}",
                        f"{row.gst_total:.2f}",
                        f"{row.pst_total:.2f}",
                        f"{row.subtotal + row.gst_total + row.pst_total:.2f}",
                    ),
                )
                num_orders += row.num_orders
                num_items += row.num_items
                subtotal += row.subtotal
                gst_total += row.gst_total
                pst_total += row.pst_total
            self.item(
                identifier,
                values=(
                    str(num_orders),
                    str(num_items),
                    f"{subtotal:.2f}",
                    f"{gst_total:.2f}",
                    f"{pst_total:.2f}",
                    f"{subtotal + gst_total + pst_total:.2f}",
                ),
            )
