# app/tabs/tools_subtabs/check_balance.py
import tkinter as tk
from tkinter import ttk
from app.tabs.check_balance_subtabs.check_balance_netzme import BalanceNetzme
from app.tabs.check_balance_subtabs.check_balance_merchant import BalanceMerchant

class CheckBalance(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Topup Faspay Tab
        self.merchant_tab = BalanceMerchant(self.tab_control)
        self.tab_control.add(self.merchant_tab, text="Merchant")

        # Topup POS Tab
        self.netzme_tab = BalanceNetzme(self.tab_control)
        self.tab_control.add(self.netzme_tab, text="Netzme")

        self.tab_control.pack(expand=1, fill="both")
