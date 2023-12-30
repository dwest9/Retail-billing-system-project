"""Contains the functionality for displaying daily reports"""
from tkinter import ttk
from tkcalendar import DateEntry

from app import App
from cashier_report_view import CashierReportView
from hourly_report_view import HourlyReportView
from item_report_view import ItemReportView


class DailyReportsFrame(ttk.Frame):
    """Frame for selecting a date and displaying daily reports"""

    def __init__(self, app: App, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.app = app

        daily_reports_header = ttk.Frame(self)
        daily_reports_header.pack(anchor="w")

        ttk.Label(daily_reports_header, text="Date").grid(row=0, column=0)
        self.date_selector = DateEntry(daily_reports_header)
        self.date_selector.grid(row=0, column=1)

        self.report_tabs = ttk.Notebook(self)
        self.report_tabs.pack(fill="both", expand=True)

        self.cashier_report = CashierReportView(self.report_tabs)

        self.hourly_sales = HourlyReportView(self)

        self.item_report = ItemReportView(self.report_tabs)

        self.report_tabs.add(self.cashier_report, text="Cashier Report")
        self.report_tabs.add(self.hourly_sales, text="Hourly Sales")
        self.report_tabs.add(self.item_report, text="Item Sales")

        self.date_selector.bind("<<DateEntrySelected>>", self.date_selected)

    def date_selected(self, *_args):
        """Handles displaying reports for the newly selected date"""
        new_date = self.date_selector.get_date()

        cashier_report = self.app.report_system.get_cashier_sales_for_date(new_date)
        self.cashier_report.display_new_report(cashier_report)

        hourly_sales = self.app.report_system.get_hourly_sales_for_date(new_date)
        self.hourly_sales.display_new_report(hourly_sales)

        item_sales = self.app.report_system.get_item_sales_for_date(new_date)
        self.item_report.display_new_report(item_sales)
