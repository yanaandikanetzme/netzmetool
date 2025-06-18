# app/tabs/invoice_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.invoice_subtabs.qris_tab import QRISTab
from app.tabs.invoice_subtabs.xendit_va_tab import XenditVATab
from app.tabs.invoice_subtabs.indomaret_tab import IndomaretTab
from app.tabs.invoice_subtabs.dki_tab import DKITab
from app.tabs.invoice_subtabs.bca_faspay_tab import BCAFaspayTab

class InvoiceTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # QRIS Tab
        self.qris_tab = QRISTab(self.tab_control)
        self.tab_control.add(self.qris_tab, text="QRIS")

        # Xendit VA Tab
        self.xendit_va_tab = XenditVATab(self.tab_control)
        self.tab_control.add(self.xendit_va_tab, text="Xendit VA")

        # Indomaret Tab
        self.indomaret_tab = IndomaretTab(self.tab_control)
        self.tab_control.add(self.indomaret_tab, text="Indomaret")

        # DKI Tab
        self.dki_tab = DKITab(self.tab_control)
        self.tab_control.add(self.dki_tab, text="DKI")

        # BCA Faspay Tab
        self.bca_faspay_tab = BCAFaspayTab(self.tab_control)
        self.tab_control.add(self.bca_faspay_tab, text="BCA Faspay")

        self.tab_control.pack(expand=1, fill="both")