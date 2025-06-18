# app/tabs/tools_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.tools_subtabs.json_parser_tab import ParserTab
from app.tabs.tools_subtabs.emv_beautify_tab import EMVBeautifyTab
from app.tabs.tools_subtabs.hash_tab import HashTab
from app.tabs.tools_subtabs.account_management_tab import AccountManagementTab
from app.tabs.tools_subtabs.generator_tab import GeneratorTab
from app.tabs.tools_subtabs.topup_netzme_tab import TopupNetzmeTab
from app.tabs.tools_subtabs.testcase_generator_tab import TestCaseGenerator
from app.tabs.tools_subtabs.compare_text_tab import CompareText
from app.tabs.tools_subtabs.curl_request_tab import HitCurl
from app.tabs.tools_subtabs.android_tab import AndroidTab

class ToolsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # JSON Parser Tab
        self.json_parser_tab = ParserTab(self.tab_control)
        self.tab_control.add(self.json_parser_tab, text="Parser")

        # EMV Beautify Tab
        self.emv_beautify_tab = EMVBeautifyTab(self.tab_control)
        self.tab_control.add(self.emv_beautify_tab, text="EMV Beautify")

        # Android Tab
        self.android_tab = AndroidTab(self.tab_control)
        self.tab_control.add(self.android_tab, text="Android")
        
        # SHA256 Tab
        self.sha256_tab = HashTab(self.tab_control)
        self.tab_control.add(self.sha256_tab, text="Hash")

        # Reset Login Tab
        self.reset_login_tab = AccountManagementTab(self.tab_control)
        self.tab_control.add(self.reset_login_tab, text="Check Akun")

        # Generator Tab
        self.generator_tab = GeneratorTab(self.tab_control)
        self.tab_control.add(self.generator_tab, text="Generator")

        # Topup Netzme Tab
        self.topup_netzme_tab = TopupNetzmeTab(self.tab_control)
        self.tab_control.add(self.topup_netzme_tab, text="Topup Netzme")

        # Testcase Generator
        self.testcase_generator_tab = TestCaseGenerator(self.tab_control)
        self.tab_control.add(self.testcase_generator_tab, text="Testcase Generator")

        # Compare Text
        self.compare_text_tab = CompareText(self.tab_control)
        self.tab_control.add(self.compare_text_tab, text="Compare Text")

        # Hit Curl Request
        self.curl_request_tab = HitCurl(self.tab_control)
        self.tab_control.add(self.curl_request_tab, text="Curl Request")

        self.tab_control.pack(expand=1, fill="both")