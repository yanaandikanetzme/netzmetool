# app/tabs/tools_subtabs/topup_netzme_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.tools_subtabs.topup_netzme_subtabs.topup_netzme_tab import TopupNetzmeTabs
from app.tabs.tools_subtabs.topup_netzme_subtabs.topup_agent_balance import TopupAgent
from app.tabs.tools_subtabs.topup_netzme_subtabs.disburse import DisbursementAPIApp

class TopupNetzmeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Topup Netzme Tab
        self.topup_faspay_tab = TopupNetzmeTabs(self.tab_control)
        self.tab_control.add(self.topup_faspay_tab, text="Topup Netzme")

        #Topup Agent
        self.topup_agent_tab = TopupAgent(self.tab_control)
        self.tab_control.add(self.topup_agent_tab, text="Topup Agent")

        #Disburse
        self.disburs_tab = DisbursementAPIApp(self.tab_control)
        self.tab_control.add(self.disburs_tab, text="Disburse")

        self.tab_control.pack(expand=1, fill="both")