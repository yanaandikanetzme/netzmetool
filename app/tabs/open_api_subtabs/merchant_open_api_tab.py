# app/tabs/open_api_subtabs/merchant_open_api_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.open_api_subtabs.merchant_open_api_subtabs.merchant_non_snap_tab import MerchantNonSnapTab
from app.tabs.open_api_subtabs.merchant_open_api_subtabs.merchant_snap_tab import MerchantSnapTab

class MerchantOpenAPITab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Non Snap Tab
        self.non_snap_tab = MerchantNonSnapTab(self.tab_control)
        self.tab_control.add(self.non_snap_tab, text="Non Snap")

        # Snap Tab
        self.snap_tab = MerchantSnapTab(self.tab_control)
        self.tab_control.add(self.snap_tab, text="Snap")

        self.tab_control.pack(expand=1, fill="both")
