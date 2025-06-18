# app/tabs/tools_subtabs/check_balance_subtabs/check_balance_netzme.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from datetime import datetime
import threading

class BalanceNetzme(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.show_totals = tk.BooleanVar(value=False)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Input frame
        input_frame = ttk.Frame(self, padding="10 10 10 0")
        input_frame.grid(row=0, column=0, sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        # Show totals checkbox
        ttk.Checkbutton(input_frame, text="Lihat Jumlah", variable=self.show_totals, 
                       command=self.update_totals_display).grid(row=0, column=0, sticky="w")

        tk.Label(input_frame, text="Input:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.input_text = CustomText(input_frame, height=5, width=50)
        self.input_text.grid(row=1, column=1, sticky="ew")

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=1, sticky="e", pady=(10, 0))
        self.get_new_data_button = ttk.Button(button_frame, text="Get Balance", command=self.start_thread_connection)
        self.get_new_data_button.pack(side=tk.LEFT, padx=(0, 10))
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        # Notebook for data display
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs and treeviews
        self.create_data_tabs()

        # Create totals frame
        self.totals_frame = ttk.Frame(self)
        self.totals_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.create_totals_widgets()
        self.totals_frame.grid_remove()  # Initially hidden

        # Timestamp label
        self.timestamp_label = tk.Label(self, text="")
        self.timestamp_label.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
    
    def create_totals_widgets(self):
        ttk.Label(self.totals_frame, text="Total Balance Difference:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.total_balance_label = ttk.Label(self.totals_frame, text="0")
        self.total_balance_label.grid(row=0, column=1, sticky="w")

    def update_totals_display(self):
        if self.show_totals.get():
            diff_tree = self.treeviews["difference"]
            total_balance = sum(float(diff_tree.item(item)["values"][1]) for item in diff_tree.get_children())
            self.total_balance_label.config(text=f"{total_balance:,.2f}")
            self.totals_frame.grid()
        else:
            self.totals_frame.grid_remove()
    
    def create_data_tabs(self):
        tab_names = ["Old Data", "New Data", "Difference"]
        self.treeviews = {}

        for tab_name in tab_names:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tab_name)
            
            tree = self.create_treeview(tab)
            self.treeviews[tab_name.lower().replace(" ", "_")] = tree
    
    def create_treeview(self, parent):
        tree = CustomTreeview(parent)
        tree["columns"] = ("user_id", "balance")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("user_id", width=200, anchor=tk.W)
        tree.column("balance", width=150, anchor=tk.E)
        tree.heading("user_id", text="User ID")
        tree.heading("balance", text="Balance")
        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def start_thread_connection(self):
        self.get_new_data_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.get_new_data)
        thread.start()

    def get_new_data(self):
        input_text = self.input_text.get("1.0", "end-1c")
        merchant_ids = [f"'{id_}'" for id_ in input_text.split('\n') if id_.strip()]

        query = f"""
        WITH merchant_ids AS (
            SELECT unnest(ARRAY[{','.join(merchant_ids)}]) AS user_id
        )
        SELECT 
            b.user_id, 
            b.amount_value - COALESCE(SUM(pt.amount_value), 0) AS total 
        FROM 
            merchant_ids mi
        LEFT JOIN 
            balance b ON mi.user_id = b.user_id
        LEFT JOIN 
            pending_transaction pt ON pt.user_id = b.user_id 
        GROUP BY 
            b.user_id 
        ORDER BY 
            b.user_id;
        """

        merchant_data = Modules.ConnectDBLenjer(query)

        old_data = self.treeviews["old_data"]
        new_data = self.treeviews["new_data"]
        diff_data = self.treeviews["difference"]

        if not old_data.get_children() and not new_data.get_children():
            self.update_treeview(old_data, merchant_data)
        elif old_data.get_children() and not new_data.get_children():
            self.update_treeview(new_data, merchant_data)
            self.calculate_difference()
        elif old_data.get_children() and new_data.get_children():
            self.move_data(new_data, old_data)
            self.update_treeview(new_data, merchant_data)
            self.calculate_difference()

        if self.show_totals.get():
            self.update_totals_display()

        self.get_new_data_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        current_time = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
        self.timestamp_label.config(text=f"Data terakhir diambil pada: {current_time}")

    def update_treeview(self, treeview, data):
        treeview.delete(*treeview.get_children())
        for row in data:
            treeview.insert("", "end", values=row)

    def move_data(self, source, destination):
        destination.delete(*destination.get_children())
        for item in source.get_children():
            values = source.item(item)["values"]
            destination.insert("", "end", values=values)

    def calculate_difference(self):
        old_data = self.treeviews["old_data"]
        new_data = self.treeviews["new_data"]
        diff_data = self.treeviews["difference"]

        old_values = {self.treeviews["old_data"].item(item)["values"][0]: float(self.treeviews["old_data"].item(item)["values"][1]) for item in old_data.get_children()}
        new_values = {self.treeviews["new_data"].item(item)["values"][0]: float(self.treeviews["new_data"].item(item)["values"][1]) for item in new_data.get_children()}

        diff_data.delete(*diff_data.get_children())
        for user_id in old_values.keys():
            if user_id in new_values:
                diff = new_values[user_id] - old_values[user_id]
                diff_data.insert("", "end", values=(user_id, diff))

        if self.show_totals.get():
            self.update_totals_display()

    def reset(self):
        for treeview in self.treeviews.values():
            treeview.delete(*treeview.get_children())
        self.timestamp_label.config(text="")
        self.total_balance_label.config(text="0")
        self.start_thread_connection()
