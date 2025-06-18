#lokasi file app/tabs/query_tab.py
import tkinter as tk
from tkinter import ttk
from automation.src.base import query_and_get_rows
from app.tabs.query_subtabs.query_result_tab import QueryResultWindow
import json
from app.tabs.query_subtabs.query_manager import QueryManager
from app.custom.custom_text import CustomText
import threading

class QueryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager_window = None
        self.query_manager = None
        self.saved_queries = self.load_saved_queries()

        self.create_widgets()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        # Left column for controls
        control_frame = ttk.LabelFrame(self, text="Query Controls")
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        tk.Label(control_frame, text="Database:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.combo_environment = ttk.Combobox(control_frame, width=30, state='readonly')
        self.combo_environment.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        self.combo_environment.bind('<<ComboboxSelected>>', self.update_saved_query_combo)

        tk.Label(control_frame, text="Group Query:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.combo_saved_query = ttk.Combobox(control_frame, width=30, state='readonly')
        self.combo_saved_query.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.combo_saved_query.bind('<<ComboboxSelected>>', self.load_selected_queries)

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, pady=10)
        self.run_button = ttk.Button(button_frame, text="Run Query", command=self.start_thread_connection)
        self.run_button.pack(side=tk.LEFT, padx=5)
        self.manager_button = ttk.Button(button_frame, text="Query Manager", command=self.open_query_manager)
        self.manager_button.pack(side=tk.LEFT, padx=5)

        # Right column for query input
        query_frame = ttk.LabelFrame(self, text="Query Input")
        query_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        query_frame.grid_columnconfigure(0, weight=1)
        query_frame.grid_rowconfigure(0, weight=1)

        self.query_text_input = CustomText(query_frame, wrap=tk.WORD)
        self.query_text_input.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(query_frame, orient="vertical", command=self.query_text_input.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.query_text_input.configure(yscrollcommand=scrollbar.set)

        # Initialize comboboxes
        self.combo_environment['values'] = list(self.saved_queries.keys())
        if self.saved_queries:
            self.combo_environment.current(0)
            self.update_saved_query_combo(None)

    def update_combos(self):
        self.saved_queries = self.load_saved_queries()
        self.combo_environment['values'] = list(self.saved_queries.keys())
        
        current_environment = self.combo_environment.get()
        
        self.update_saved_query_combo(None)
        
        if current_environment:
            self.combo_environment.set(current_environment)
            self.load_selected_queries(None)
    
    def start_thread_connection(self):
        self.run_button.config(state=tk.DISABLED)
        # Memulai thread baru untuk koneksi database
        thread = threading.Thread(target=self.run_query)
        thread.start()

    def load_saved_queries(self):
        try:
            with open('config/saved_query.json', 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return {}

    def update_saved_query_combo(self, event):
        selected_environment = self.combo_environment.get()
        self.query_text_input.delete('1.0', tk.END)  # Menghapus nilai query_text_input
        self.combo_saved_query.set('')  # Menghapus nilai combo_saved_query
        if selected_environment:
            queries = self.saved_queries.get(selected_environment, [])
            query_names = [query['Group'] for query in queries]
            self.combo_saved_query['values'] = query_names
    
    def load_selected_queries(self, event):
        selected_query_name = self.combo_saved_query.get()
        selected_environment = self.combo_environment.get()
        if selected_query_name and selected_environment:
            queries = self.saved_queries.get(selected_environment, [])
            selected_query = next((q for q in queries if q['Group'] == selected_query_name), None)
            if selected_query:
                formatted_queries = []
                for query in selected_query['Query']:
                    if not query.endswith(';'):
                        query += ';'
                    formatted_queries.append(query)
                query_text = '\n'.join(formatted_queries) + '\n'
                self.query_text_input.delete('1.0', tk.END)
                self.query_text_input.insert('1.0', query_text)

    def run_query(self):
        queries = self.query_text_input.get("1.0", tk.END).strip().split(';')
        queries = [query.strip() for query in queries if query.strip()]

        if not queries:
            return

        result_window = QueryResultWindow(self)

        for query in queries:
            result_data, column_names = query_and_get_rows(query=query, connection_key='Merchant')
            result_window.set_query_text(query)
            result_window.set_result_data(result_data, column_names, query)
        self.run_button.config(state=tk.NORMAL)

    def open_query_manager(self):
        if self.manager_window is None or not self.manager_window.winfo_exists():
            self.manager_window = tk.Toplevel(self)
            self.manager_window.title("Query Manager")
            self.manager_window.protocol("WM_DELETE_WINDOW", self.update_combos)
            self.query_manager = QueryManager(self.manager_window, self)
        else:
            self.manager_window.focus_set()

    def update_combos(self):
        self.saved_queries = self.load_saved_queries()
        self.combo_environment['values'] = list(self.saved_queries.keys())
        
        current_environment = self.combo_environment.get()
        
        self.update_saved_query_combo(None)
        
        if current_environment:
            self.combo_environment.set(current_environment)
            self.load_selected_queries(None)
        
        if self.manager_window:
            self.manager_window.destroy()
            self.manager_window = None
            self.query_manager = None  # Tambahkan baris ini