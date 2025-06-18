# app/tabs/open_api_tab.py
import tkinter as tk
from tkinter import ttk
from app.tabs.open_api_subtabs.merchant_open_api_tab import MerchantOpenAPITab
from app.tabs.open_api_subtabs.netzme_open_api_tab import NetzmeOpenAPITab
from app.tabs.open_api_subtabs.aggregator_manager import AggregatorConfig
from app.tabs.open_api_subtabs.aggregator_generator import AggregatorGenerator
from app.tabs.open_api_subtabs.ppob_tab import PPOBOpenAPITab

class OpenAPITab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # Merchant Open API Tab
        self.merchant_open_api_tab = MerchantOpenAPITab(self.tab_control)
        self.tab_control.add(self.merchant_open_api_tab, text="Merchant Open API")

        # Netzme Open API Tab
        self.netzme_open_api_tab = NetzmeOpenAPITab(self.tab_control)
        self.tab_control.add(self.netzme_open_api_tab, text="Netzme Open API")

        # PPOB Open API Tab
        self.ppob_open_api_tab = PPOBOpenAPITab(self.tab_control)
        self.tab_control.add(self.ppob_open_api_tab, text="PPOB Open API")

        # Aggregator Config Tab
        self.aggregator_config = AggregatorConfig(self.tab_control)
        self.tab_control.add(self.aggregator_config, text="Aggregator Config")

        # Aggregator Generator Tab
        self.aggregator_generator = AggregatorGenerator(self.tab_control)
        self.tab_control.add(self.aggregator_generator, text="Aggregator Generator")

        self.tab_control.pack(expand=1, fill="both")