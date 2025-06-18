# app/tabs/settlement_manual_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.settlement_manual_subtabs.settlement_invoice_tab import SettlementInvoiceTab
from app.tabs.settlement_manual_subtabs.settlement_qris_acquirer_tab import SettlementQRISAcquirerTab
from app.tabs.settlement_manual_subtabs.settlement_qris_issuer_tab import SettlementQRISIssuerTab

class SettlementManualTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Settlement Invoice Tab
        self.settlement_invoice_tab = SettlementInvoiceTab(self.tab_control)
        self.tab_control.add(self.settlement_invoice_tab, text="Settlement Invoice")

        # Settlement QRIS Acquirer Tab
        self.settlement_qris_acquirer_tab = SettlementQRISAcquirerTab(self.tab_control)
        self.tab_control.add(self.settlement_qris_acquirer_tab, text="Settlement QRIS Acquirer")

        # Settlement QRIS Issuer Tab
        self.settlement_qris_issuer_tab = SettlementQRISIssuerTab(self.tab_control)
        self.tab_control.add(self.settlement_qris_issuer_tab, text="Settlement QRIS Issuer")

        self.tab_control.pack(expand=1, fill="both")