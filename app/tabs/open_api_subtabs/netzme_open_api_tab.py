# app/tabs/open_api_subtabs/netzme_open_api_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.open_api_subtabs.netzme_open_api_subtabs.netzme_non_snap_tab import NetzmeNonSnapTab
from app.tabs.open_api_subtabs.netzme_open_api_subtabs.netzme_snap_tab import NetzmeSnapTab
from app.tabs.open_api_subtabs.netzme_open_api_subtabs.netzme_webview_tab import NetzmeWebviewTab

class NetzmeOpenAPITab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Non Snap Tab
        self.non_snap_tab = NetzmeNonSnapTab(self.tab_control)
        self.tab_control.add(self.non_snap_tab, text="Non Snap")

        # Snap Tab
        self.snap_tab = NetzmeSnapTab(self.tab_control)
        self.tab_control.add(self.snap_tab, text="Snap")

        # Web View Tab
        self.webview_tab = NetzmeWebviewTab(self.tab_control)
        self.tab_control.add(self.webview_tab, text="Web View")

        self.tab_control.pack(expand=1, fill="both")