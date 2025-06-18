# app/tabs/qr_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.tabs.qr_subtabs.merchant_tab import MerchantTab
from app.tabs.qr_subtabs.refund_tab import RefundTab
from app.tabs.qr_subtabs.dispute_tab import DisputeTab

class QRTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Load Tab
        self.load_tab = MerchantTab(self.tab_control)
        self.tab_control.add(self.load_tab, text="Merchant")

        # Refund Tab
        self.refund_tab = RefundTab(self.tab_control)
        self.tab_control.add(self.refund_tab, text="Refund")

        # Dispute Tab
        self.dispute_tab = DisputeTab(self.tab_control)
        self.tab_control.add(self.dispute_tab, text="Dispute")

        self.tab_control.pack(expand=1, fill="both")