"""Contains implementation of a view displaying an items sales report"""
from tkinter import ttk

from report_system import ItemSales


class ItemReportView(ttk.Treeview):
    """Treeview for displaying hourly sales data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config(
            columns=("Quantity", "Subtotal", "GST", "PST", "Total"),
        )

        self.heading(0, text="Quantity")
        self.heading(1, text="Subtotal")
        self.heading(2, text="GST")
        self.heading(3, text="PST")
        self.heading(4, text="Total")

        self.column(0, width=100)
        self.column(1, width=100)
        self.column(2, width=100)
        self.column(3, width=100)
        self.column(4, width=100)

    def clear_report(self):
        """Clears the treeview"""
        self.delete(*self.get_children())

    def display_new_report(self, items: list[ItemSales]):
        """Clears the treeview and displays a new report

        Args:
            items (list[ItemSales]): item sales records of the new report
        """
        self.clear_report()

        # Group item sales by category
        category_sales: dict[int, list[ItemSales]] = {}
        for row in items:
            category_sales[row.category_id] = category_sales.get(
                row.category_id, []
            ) + [row]

        for cashier in category_sales.values():
            identifier = self.insert("", "end", text=cashier[0].category_name)
            quantity = 0
            subtotal = 0.0
            gst_total = 0.0
            pst_total = 0.0
            for row in cashier:
                self.insert(
                    identifier,
                    "end",
                    text=row.item_name,
                    values=(
                        row.quantity,
                        f"{row.subtotal:.2f}",
                        f"{row.gst_total:.2f}",
                        f"{row.pst_total:.2f}",
                        f"{row.subtotal + row.gst_total + row.pst_total:.2f}",
                    ),
                )
                quantity += row.quantity
                subtotal += row.subtotal
                gst_total += row.gst_total
                pst_total += row.pst_total
            self.item(
                identifier,
                values=(
                    str(quantity),
                    f"{subtotal:.2f}",
                    f"{gst_total:.2f}",
                    f"{pst_total:.2f}",
                    f"{subtotal + gst_total + pst_total:.2f}",
                ),
            )
