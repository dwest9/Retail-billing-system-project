"""Contains implementation of a view displaying an hourly sales report"""
from tkinter import ttk

from report_system import HourlySales


class HourlyReportView(ttk.Treeview):
    """Treeview for displaying hourly sales data"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(
            columns=("Num Orders", "Num Items", "Subtotal", "GST", "PST", "Total"),
        )

        self.heading("#0", text="Hour")
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

    def display_new_report(self, hourly_sales: list[HourlySales]):
        """Clears the treeview and displays a new report

        Args:
            hourly_sales (list[HourlySales]): hourly sales records of the new report
        """
        self.clear_report()

        for record in hourly_sales:
            self.insert(
                "",
                "end",
                text=record.hour,
                values=(
                    record.num_items,
                    record.num_orders,
                    f"{record.subtotal:.2f}",
                    f"{record.gst_total:.2f}",
                    f"{record.pst_total:.2f}",
                    f"{record.subtotal + record.gst_total + record.pst_total:.2f}",
                ),
            )
