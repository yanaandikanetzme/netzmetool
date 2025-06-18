# app/tabs/qr_subtabs/refund_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.qr_subtabs.refund_subtabs.issuer_tab import IssuerTab
from app.tabs.qr_subtabs.refund_subtabs.acquirer_tab import AcquirerTab

class RefundTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Issuer Tab
        self.issuer_tab = IssuerTab(self.tab_control)
        self.tab_control.add(self.issuer_tab, text="Issuer")

        # Acquirer Tab
        self.acquirer_tab = AcquirerTab(self.tab_control)
        self.tab_control.add(self.acquirer_tab, text="Acquirer")

        self.tab_control.pack(expand=1, fill="both")