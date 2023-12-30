"""Contains the functionality for displaying reports over a date range"""
from tkinter import messagebox, ttk
from tkcalendar import DateEntry

from app import App
from cashier_report_view import CashierReportView
from daily_report_view import DailyReportView
from hourly_report_view import HourlyReportView
from item_report_view import ItemReportView


class DateRangeReportsFrame(ttk.Frame):
    """Frame for selecting a date range and displaying reports over the date range"""

    def __init__(self, app: App, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.app = app

        reports_header = ttk.Frame(self)
        reports_header.pack(anchor="w")

        ttk.Label(reports_header, text="Start Date").grid(row=0, column=0)
        self.start_date_selector = DateEntry(reports_header)
        self.start_date_selector.grid(row=0, column=1)

        ttk.Label(reports_header, text="End Date").grid(row=0, column=2)
        self.end_date_selector = DateEntry(reports_header)
        self.end_date_selector.grid(row=0, column=3)

        ttk.Button(reports_header, text="Display", command=self.handle_display).grid(
            row=0, column=4
        )

        self.report_tabs = ttk.Notebook(self)
        self.report_tabs.pack(fill="both", expand=True)

        self.cashier_report = CashierReportView(self.report_tabs)

        self.hourly_report = HourlyReportView(self)

        self.daily_report = DailyReportView(self)

        self.item_report = ItemReportView(self.report_tabs)

        self.report_tabs.add(self.cashier_report, text="Cashier Report")
        self.report_tabs.add(self.hourly_report, text="Hourly Sales")
        self.report_tabs.add(self.daily_report, text="Daily Sales")
        self.report_tabs.add(self.item_report, text="Item Sales")

    def handle_display(self):
        """Handles displaying reports for the new date range"""
        start_date = self.start_date_selector.get_date()
        end_date = self.end_date_selector.get_date()
        if end_date < start_date:
            messagebox.showerror("Error", "End date cannot be earlier than start date")
            return

        cashier_sales = self.app.report_system.get_cashier_sales_for_date_range(
            start_date, end_date
        )
        self.cashier_report.display_new_report(cashier_sales)

        hourly_sales = self.app.report_system.get_hourly_sales_for_date_range(
            start_date, end_date
        )
        self.hourly_report.display_new_report(hourly_sales)

        daily_sales = self.app.report_system.get_daily_sales_for_date_range(
            start_date, end_date
        )
        self.daily_report.display_new_report(daily_sales)

        item_sales = self.app.report_system.get_item_sales_for_date_range(
            start_date, end_date
        )
        self.item_report.display_new_report(item_sales)
