# app/tabs/tools_subtabs/topup_netzme_subtabs/topup_netzme_tab.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.topupNetzme import topupNetzme
from src.topupPOS import topupNetzmePOS
from app.tabs.popup import ResponseOpenAPI

class TopupNetzmeTabs(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding="20")
        self.create_widgets()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both")

        self.faspay_frame = ttk.Frame(self.notebook, padding="10")
        self.pos_frame = ttk.Frame(self.notebook, padding="10")

        self.notebook.add(self.faspay_frame, text="Faspay Topup")
        self.notebook.add(self.pos_frame, text="POS Topup")

        self.create_faspay_widgets()
        self.create_pos_widgets()

    def create_faspay_widgets(self):
        tk.Label(self.faspay_frame, text='No VA BCA:').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.no_va_bca = ttk.Entry(self.faspay_frame, width=30)
        self.no_va_bca.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.faspay_frame, text='Amount Topup:').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_bca = ttk.Entry(self.faspay_frame, width=30)
        self.amount_bca.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.faspay_frame, text='Post Faspay Topup', command=self.topup_netzme_balance).grid(row=2, column=0, columnspan=2, pady=10)

    def create_pos_widgets(self):
        tk.Label(self.pos_frame, text='No VA POS:').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.no_va_pos = ttk.Entry(self.pos_frame, width=30)
        self.no_va_pos.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.pos_frame, text='Nominal VA:').grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_pos = ttk.Entry(self.pos_frame, width=30)
        self.amount_pos.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.pos_frame, text='Admin Fee:').grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.admin_fee_pos = ttk.Entry(self.pos_frame, width=30)
        self.admin_fee_pos.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.pos_frame, text='Post POS Topup', command=self.topup_pos).grid(row=3, column=0, columnspan=2, pady=10)

    def topup_netzme_balance(self):
        get_va = self.no_va_bca.get()
        get_amount = self.amount_bca.get()
        try:
            hit_topup_netzme = topupNetzme.topup_netzme(get_va, get_amount)
            self.show_response("Faspay Topup Response", hit_topup_netzme)
        except Exception as e:
            self.show_error("Faspay Topup Error", str(e))

    def topup_pos(self):
        no_va_pos = self.no_va_pos.get()
        amount_pos = self.amount_pos.get()
        admin_fee_pos = self.admin_fee_pos.get()

        if no_va_pos.startswith("168"):
            no_va_pos = no_va_pos[3:]

        if admin_fee_pos in ['', 'FREE', 'free']:
            admin_fee_pos = "0"

        try:
            hit_topup_pos = topupNetzmePOS.topupPOS(no_va_pos, amount_pos, admin_fee_pos)
            self.show_response("POS Topup Response", hit_topup_pos)
        except Exception as e:
            self.show_error("POS Topup Error", str(e))

    def show_response(self, title, message):
        ResponseOpenAPI(str(message))

    def show_error(self, title, message):
        messagebox.showerror(title, str(message))