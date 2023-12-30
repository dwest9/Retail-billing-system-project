"""Contains functionality for for viewing reports"""
from tkinter import Tk, Toplevel, ttk
from daily_reports_frame import DailyReportsFrame
from date_range_reports_frame import DateRangeReportsFrame
from app import App


class ReportsView(Toplevel):
    """Report view GUI window"""

    def __init__(self, app: App, parent: Tk, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.parent = parent
        self.geometry("1000x600")
        self.title("Reports")

        self.report_period = ttk.Notebook(self)
        self.report_period.pack(fill="both", expand=True)

        self.daily_reports = DailyReportsFrame(self.app, self.report_period)
        self.daily_reports.pack(fill="both", expand=True)

        self.date_range_reports = DateRangeReportsFrame(self.app, self.report_period)
        self.date_range_reports.pack(fill="both", expand=True)

        self.report_period.add(self.daily_reports, text="Daily Reports")
        self.report_period.add(self.date_range_reports, text="Date Range Reports")

        self.protocol("WM_DELETE_WINDOW", self.window_close)

    def window_close(self):
        """Handles window close event"""
        self.parent.deiconify()
        self.destroy()
