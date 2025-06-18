#/src/date_picker.py
import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime

class DatePicker(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("Select Date")

        # Get the current year, month, and day
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.current_day = now.day

        self.calendar = calendar.TextCalendar(calendar.SUNDAY)
        self.year = tk.StringVar(value=str(self.current_year))
        self.month = tk.StringVar(value=str(self.current_month))

        tk.Label(self, text="Year:").grid(row=0, column=0, padx=5, pady=5)
        self.year_spinbox = ttk.Spinbox(self, from_=1900, to=2100, textvariable=self.year, width=5)
        self.year_spinbox.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Month:").grid(row=0, column=2, padx=5, pady=5)
        self.month_spinbox = ttk.Spinbox(self, from_=1, to=12, textvariable=self.month, width=5)
        self.month_spinbox.grid(row=0, column=3, padx=5, pady=5)

        self.update_calendar()

        # Bind update events
        self.year_spinbox.bind('<KeyRelease>', self.update_calendar_event)
        self.month_spinbox.bind('<KeyRelease>', self.update_calendar_event)
        self.year_spinbox.bind('<<Increment>>', self.update_calendar_event)
        self.year_spinbox.bind('<<Decrement>>', self.update_calendar_event)
        self.month_spinbox.bind('<<Increment>>', self.update_calendar_event)
        self.month_spinbox.bind('<<Decrement>>', self.update_calendar_event)

    def update_calendar_event(self, event):
        self.schedule_update_calendar()

    def schedule_update_calendar(self):
        self.after(10, self.update_calendar)

    def update_calendar(self):
        style = ttk.Style()
        style.configure('Highlight.TButton', background="yellow")
        year = int(self.year.get()) if self.year.get().isdigit() else self.current_year
        month = int(self.month.get()) if self.month.get().isdigit() else self.current_month
        month = max(1, min(12, month))  # Ensure month is between 1 and 12

        if hasattr(self, 'calendar_frame'):
            self.calendar_frame.destroy()

        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.grid(row=2, column=0, columnspan=7, padx=5, pady=5)

        # Display day names
        days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        for idx, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day).grid(row=0, column=idx)

        cal = self.calendar.monthdayscalendar(year, month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0:
                    day = ""
                if day == self.current_day and month == self.current_month and year == self.current_year:
                    btn = tk.Button(self.calendar_frame, text=str(day), width=3, bg="yellow", command=lambda d=day: self.set_date(d))
                else:
                    btn = tk.Button(self.calendar_frame, text=str(day), width=3, command=lambda d=day: self.set_date(d))
                btn.grid(row=r+1, column=c, padx=1, pady=1)

    def set_date(self, day):
        if day:
            selected_date = f"{self.year.get()}{self.month.get().zfill(2)}{str(day).zfill(2)}"
            self.callback(selected_date)
            self.destroy()