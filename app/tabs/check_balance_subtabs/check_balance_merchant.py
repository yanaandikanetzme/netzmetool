# app/tabs/tools_subtabs/check_balance_subtabs/check_balance_merchant.py
from tkinter import *
import tkinter as tk
from tkinter import ttk, messagebox
from src.modules import Modules
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview
from datetime import datetime
import threading

class BalanceMerchant(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.treeview_labels = ["old_data", "new_data", "difference"]
        self.show_totals = tk.BooleanVar(value=False)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Frame for balance type selection and input
        top_frame = ttk.Frame(self, padding="10 10 10 5")
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        # Balance type selection
        tk.Label(top_frame, text="Balance Type:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.balance_type = tk.StringVar(value="Balance biasa")
        ttk.Radiobutton(top_frame, text="Balance biasa", variable=self.balance_type, 
                        value="Balance biasa", command=self.on_balance_type_change).grid(row=0, column=1, sticky="w")
        ttk.Radiobutton(top_frame, text="AutoWithdraw", variable=self.balance_type, 
                        value="AutoWithdraw", command=self.on_balance_type_change).grid(row=0, column=2, sticky="w")

        # Show totals checkbox
        ttk.Checkbutton(top_frame, text="Lihat Jumlah", variable=self.show_totals, 
                       command=self.update_totals_display).grid(row=0, column=3, sticky="w", padx=(20, 0))

        # Input area
        tk.Label(top_frame, text="Input:").grid(row=1, column=0, sticky="nw", pady=(10, 0))
        self.input_text = CustomText(top_frame, height=5, width=50)
        self.input_text.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(10, 0))

        # Buttons
        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=2, column=1, columnspan=2, sticky="e", pady=(10, 0))
        self.get_new_data_button = ttk.Button(button_frame, text="Get Balance", command=self.start_thread_connection)
        self.get_new_data_button.pack(side=tk.LEFT, padx=(0, 10))
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT)

        # Notebook for data display
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Create tabs and treeviews
        self.create_data_tabs()

        # Create totals frame
        self.totals_frame = ttk.Frame(self)
        self.totals_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.create_totals_widgets()
        self.totals_frame.grid_remove()  # Initially hidden

        # Timestamp label
        self.timestamp_label = tk.Label(self, text="")
        self.timestamp_label.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.balance_timestamp = ""
        self.autowithdraw_timestamp = ""
    
    def update_totals_display(self):
        if self.show_totals.get() and self.balance_type.get() == "Balance biasa":
            diff_tree = self.treeviews["difference_balance"]
            total_unsettles = sum(float(diff_tree.item(item)["values"][1]) for item in diff_tree.get_children())
            total_settle = sum(float(diff_tree.item(item)["values"][2]) for item in diff_tree.get_children())
            total_balance = sum(float(diff_tree.item(item)["values"][3]) for item in diff_tree.get_children())

            self.total_unsettles_label.config(text=f"{total_unsettles:,.2f}")
            self.total_settle_label.config(text=f"{total_settle:,.2f}")
            self.total_balance_label.config(text=f"{total_balance:,.2f}")
            self.totals_frame.grid()
        else:
            self.totals_frame.grid_remove()

    def create_totals_widgets(self):
        # Create labels for totals
        ttk.Label(self.totals_frame, text="Total Balance Unsettles:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.total_unsettles_label = ttk.Label(self.totals_frame, text="0")
        self.total_unsettles_label.grid(row=0, column=1, sticky="w")

        ttk.Label(self.totals_frame, text="Total Balance Settle:").grid(row=1, column=0, sticky="w", padx=(0, 10))
        self.total_settle_label = ttk.Label(self.totals_frame, text="0")
        self.total_settle_label.grid(row=1, column=1, sticky="w")

        ttk.Label(self.totals_frame, text="Grand Total Balance:").grid(row=2, column=0, sticky="w", padx=(0, 10))
        self.total_balance_label = ttk.Label(self.totals_frame, text="0")
        self.total_balance_label.grid(row=2, column=1, sticky="w")

    def get_balance_config(self):
        return {
            "columns": ("user_id", "balance_unsettles", "balance_settle", "total_balance"),
            "column_widths": (200, 150, 150, 150),
            "column_anchors": (tk.W, tk.E, tk.E, tk.E),
            "column_headings": ("User ID", "Balance Unsettles", "Balance Settle", "Total Balance"),
        }

    def get_autowithdraw_config(self):
        return {
            "columns": ("seq", "merchant_id", "balance", "created_at", "updated_at"),
            "column_widths": (100, 200, 150, 200, 200),
            "column_anchors": (tk.W, tk.W, tk.E, tk.W, tk.W),
            "column_headings": ("Seq", "Merchant ID", "Balance", "Created At", "Updated At"),
        }
    
    def create_data_tabs(self):
        tab_names = ["Old Data", "New Data", "Difference"]
        self.treeviews = {}

        for tab_name in tab_names:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=tab_name)
            
            balance_frame = ttk.Frame(tab)
            balance_frame.pack(fill=tk.BOTH, expand=True)
            balance_tree = self.create_treeview(balance_frame, self.get_balance_config())
            self.treeviews[f"{tab_name.lower().replace(' ', '_')}_balance"] = balance_tree

            autowithdraw_frame = ttk.Frame(tab)
            autowithdraw_frame.pack(fill=tk.BOTH, expand=True)
            autowithdraw_tree = self.create_treeview(autowithdraw_frame, self.get_autowithdraw_config())
            self.treeviews[f"{tab_name.lower().replace(' ', '_')}_autowithdraw"] = autowithdraw_tree
            autowithdraw_frame.pack_forget()  # Initially hide AutoWithdraw TreeViews

    def create_treeview(self, parent, config):
        tree = CustomTreeview(parent)
        tree["columns"] = config["columns"]
        tree.column("#0", width=0, stretch=tk.NO)
        for i, col in enumerate(config["columns"]):
            tree.column(col, width=config["column_widths"][i], anchor=config["column_anchors"][i])
            tree.heading(col, text=config["column_headings"][i])
        tree.pack(fill=tk.BOTH, expand=True)
        return tree
    
    def on_balance_type_change(self):
        selected_type = self.balance_type.get()
        for tab_name in ["old_data", "new_data", "difference"]:
            if selected_type == "Balance biasa":
                self.treeviews[f"{tab_name}_balance"].master.pack(fill=tk.BOTH, expand=True)
                self.treeviews[f"{tab_name}_autowithdraw"].master.pack_forget()
            else:
                self.treeviews[f"{tab_name}_autowithdraw"].master.pack(fill=tk.BOTH, expand=True)
                self.treeviews[f"{tab_name}_balance"].master.pack_forget()
        self.update_timestamp_label()

            
    def show_treeviews(self, treeview_type):
        for attr in self.treeview_labels:
            frame = getattr(self, f"{attr}_{treeview_type}").master
            frame.grid()

    def hide_treeviews(self, treeview_type):
        for attr in self.treeview_labels:
            frame = getattr(self, f"{attr}_{treeview_type}").master
            frame.grid_remove()

    def start_thread_connection(self):
        self.get_new_data_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.get_new_data)
        thread.start()
        
    def get_new_data(self):
        # Mendapatkan input dari CustomText Input
        input_text = self.input_text.get("1.0", "end-1c")
        merchant_ids = [f"'{id_}'" for id_ in input_text.split('\n') if id_.strip()]

        # Menggabungkan merchant IDs untuk query
        merchant_ids_query = ", ".join(merchant_ids)

        selected_balance_type = self.balance_type.get()
        self.get_new_data_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)

        if selected_balance_type == "Balance biasa":
            # Query untuk Balance biasa
            query = f"""
            WITH merchant_ids AS (
                SELECT unnest(ARRAY[{merchant_ids_query}]) AS user_id
            )
            SELECT 
                m.user_id,
                COALESCE(SUM(mu.balance), 0) AS balance_unsettles,
                COALESCE(mb.balance, 0) AS balance_settle,
                COALESCE(SUM(mu.balance), 0) + COALESCE(mb.balance, 0) AS total_balance
            FROM 
                merchant_ids m
            LEFT JOIN 
                merchant_balance_unsettle mu ON m.user_id = mu.user_id
            LEFT JOIN 
                merchant_balance mb ON m.user_id = mb.user_id
            GROUP BY 
                m.user_id, mb.balance
            ORDER BY 
                m.user_id;
            """
        else:  # AutoWithdraw
            # Query untuk AutoWithdraw
            query = f"""
            SELECT *
            FROM merchant_auto_withdraw_balance mawb
            WHERE mawb.merchant_id IN ({merchant_ids_query})
            ORDER BY mawb.seq DESC;
            """

        # Mengeksekusi query PostgreSQL menggunakan ConnectDBMerchant
        merchant_data = Modules.ConnectDBMerchant(query)

        # Menentukan TreeView yang akan digunakan berdasarkan jenis balance
        treeview_type = "balance" if selected_balance_type == "Balance biasa" else "autowithdraw"
        old_data_treeview = self.treeviews[f"old_data_{treeview_type}"]
        new_data_treeview = self.treeviews[f"new_data_{treeview_type}"]
        diff_data_treeview = self.treeviews[f"difference_{treeview_type}"]

        # Logika untuk memperbarui TreeViews
        if not old_data_treeview.get_children() and not new_data_treeview.get_children():
            # Tampilkan data di TreeView Data Lama
            old_data_treeview.delete(*old_data_treeview.get_children())
            for row in merchant_data:
                old_data_treeview.insert("", "end", values=row)

        elif old_data_treeview.get_children() and not new_data_treeview.get_children():
            # Tampilkan data di TreeView Data Baru
            new_data_treeview.delete(*new_data_treeview.get_children())
            for row in merchant_data:
                new_data_treeview.insert("", "end", values=row)

            # Hitung selisih data
            old_data = [old_data_treeview.item(item)["values"] for item in old_data_treeview.get_children()]
            new_data = [new_data_treeview.item(item)["values"] for item in new_data_treeview.get_children()]

            diff_data = []
            for old_row, new_row in zip(old_data, new_data):
                if selected_balance_type == "Balance biasa":
                    user_id = old_row[0]
                    balance_unsettles_diff = float(new_row[1]) - float(old_row[1])
                    balance_settle_diff = float(new_row[2]) - float(old_row[2])
                    total_balance_diff = float(new_row[3]) - float(old_row[3])
                    diff_data.append((user_id, balance_unsettles_diff, balance_settle_diff, total_balance_diff))
                else:  # AutoWithdraw
                    seq = old_row[0]
                    merchant_id = old_row[1]
                    balance_diff = float(new_row[2]) - float(old_row[2])
                    created_at_diff = "N/A"
                    updated_at_diff = "N/A"
                    diff_data.append((seq, merchant_id, balance_diff, created_at_diff, updated_at_diff))

            # Menampilkan selisih data di TreeView "Selisih data baru - data lama"
            diff_data_treeview.delete(*diff_data_treeview.get_children())
            for row in diff_data:
                diff_data_treeview.insert("", "end", values=row)

        elif old_data_treeview.get_children() and new_data_treeview.get_children():
            # Hapus data di TreeView Data Lama
            old_data_treeview.delete(*old_data_treeview.get_children())

            # Copy data dari TreeView Data Baru ke TreeView Data Lama
            for item in new_data_treeview.get_children():
                values = new_data_treeview.item(item)["values"]
                old_data_treeview.insert("", "end", values=values)

            # Menjalankan query dan tampilkan di TreeView Data Baru
            new_data_treeview.delete(*new_data_treeview.get_children())
            for row in merchant_data:
                new_data_treeview.insert("", "end", values=row)

            # Hitung selisih data
            old_data = [old_data_treeview.item(item)["values"] for item in old_data_treeview.get_children()]
            new_data = [new_data_treeview.item(item)["values"] for item in new_data_treeview.get_children()]

            diff_data = []
            for old_row, new_row in zip(old_data, new_data):
                if selected_balance_type == "Balance biasa":
                    user_id = old_row[0]
                    balance_unsettles_diff = float(new_row[1]) - float(old_row[1])
                    balance_settle_diff = float(new_row[2]) - float(old_row[2])
                    total_balance_diff = float(new_row[3]) - float(old_row[3])
                    diff_data.append((user_id, balance_unsettles_diff, balance_settle_diff, total_balance_diff))
                else:  # AutoWithdraw
                    seq = old_row[0]
                    merchant_id = old_row[1]
                    balance_diff = float(new_row[2]) - float(old_row[2])
                    created_at_diff = "N/A"
                    updated_at_diff = "N/A"
                    diff_data.append((seq, merchant_id, balance_diff, created_at_diff, updated_at_diff))

            # Menampilkan selisih data di TreeView "Selisih data baru - data lama"
            diff_data_treeview.delete(*diff_data_treeview.get_children())
            for row in diff_data:
                diff_data_treeview.insert("", "end", values=row)

        current_time = datetime.now().strftime("%A, %d %B %Y %H:%M:%S")
        if selected_balance_type == "Balance biasa":
            self.balance_timestamp = current_time
        else:
            self.autowithdraw_timestamp = current_time
        if self.show_totals.get():
            self.update_totals_display()
        self.update_timestamp_label()
    
    def update_timestamp_label(self):
        selected_type = self.balance_type.get()
        if selected_type == "Balance biasa":
            timestamp = self.balance_timestamp
        else:
            timestamp = self.autowithdraw_timestamp
        
        if timestamp:
            self.timestamp_label.config(text=f"Data terakhir diambil pada: {timestamp}")
        else:
            self.timestamp_label.config(text="")
                
    def reset(self):
        selected_type = self.balance_type.get()
        treeview_type = "balance" if selected_type == "Balance biasa" else "autowithdraw"
        
        for label in self.treeview_labels:
            treeview = self.treeviews[f"{label}_{treeview_type}"]
            treeview.delete(*treeview.get_children())

        if selected_type == "Balance biasa":
            self.balance_timestamp = ""
        else:
            self.autowithdraw_timestamp = ""
        
        # Reset totals
        self.total_unsettles_label.config(text="0")
        self.total_settle_label.config(text="0")
        self.total_balance_label.config(text="0")
        
        self.start_thread_connection()
        self.update_timestamp_label()