# app/tabs/tools_subtabs/android_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.tools_subtabs.android_subtabs.android_install_tab import AndroidInstallTab
from app.tabs.tools_subtabs.android_subtabs.logcat_manager_tab import LogcatManager
from app.tabs.tools_subtabs.android_subtabs.element_tab import AndroidElementExplorer


class AndroidTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Add your elements here

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Install Tab
        self.android_install_tab = AndroidInstallTab(self.tab_control)
        self.tab_control.add(self.android_install_tab, text="Install")

        #Logcat Tab
        self.logcat_tab = LogcatManager(self.tab_control, min_height=600)
        self.logcat_tab.pack(fill=tk.BOTH, expand=True)
        self.tab_control.add(self.logcat_tab, text="Logcat")

        #Inspect Element Tab
        #self.element_tab = AndroidElementExplorer(self.tab_control)
        #self.tab_control.add(self.element_tab, text="Inspect Element")

        self.tab_control.pack(expand=1, fill="both")