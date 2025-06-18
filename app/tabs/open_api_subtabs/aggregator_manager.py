#lokasi /app/tabs/open_api_subtabs/aggregator_manager.py
import json
import tkinter as tk
from tkinter import ttk, messagebox
from src.modules import Modules
from app.custom.custom_treeview import CustomTreeview

file_path = 'config/config_aggregator.json'

class AggregatorConfig(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        with open(file_path, 'r') as file:
            self.data = json.load(file)

        self.selected_category = tk.StringVar()
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Main layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top frame for category selection
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.columnconfigure(1, weight=1)

        tk.Label(top_frame, text="Select Category:").grid(row=0, column=0, padx=(0, 5))
        self.category_combobox = ttk.Combobox(top_frame, textvariable=self.selected_category, 
                                              values=["Merchant", "Netzme", "PPOB"], state="readonly")
        self.category_combobox.grid(row=0, column=1, sticky="ew")
        self.category_combobox.bind("<<ComboboxSelected>>", self.populate_tree)

        # Treeview
        self.tree = CustomTreeview(self)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Define columns
        self.tree["columns"] = ("clearPassword", "aggregatorToken", "privateKey", "clientSecret")
        self.tree.column("#0", width=150, anchor=tk.W)
        self.tree.column("clearPassword", width=150, anchor=tk.W)
        self.tree.column("aggregatorToken", width=200, anchor=tk.W)
        self.tree.column("privateKey", width=150, anchor=tk.W)
        self.tree.column("clientSecret", width=150, anchor=tk.W)

        # Create headings
        self.tree.heading("#0", text="ID", anchor=tk.W)
        self.tree.heading("clearPassword", text="Clear Password", anchor=tk.W)
        self.tree.heading("aggregatorToken", text="Aggregator Token", anchor=tk.W)
        self.tree.heading("privateKey", text="Private Key", anchor=tk.W)
        self.tree.heading("clientSecret", text="Client Secret", anchor=tk.W)

        # Bottom frame for buttons
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        bottom_frame.columnconfigure((0, 1, 2, 3), weight=1)

        ttk.Button(bottom_frame, text="Add Entry", command=self.add_entry).grid(row=0, column=0, padx=5)
        ttk.Button(bottom_frame, text="Edit Entry", command=self.edit_entry).grid(row=0, column=1, padx=5)
        ttk.Button(bottom_frame, text="Remove Entry", command=self.remove_entry).grid(row=0, column=2, padx=5)
        ttk.Button(bottom_frame, text="Save Changes", command=self.save_changes).grid(row=0, column=3, padx=5)

        # Bindings
        self.tree.bind("<Double-1>", self.edit_entry)
        self.tree.bind("<Delete>", self.remove_entry)

    def load_data(self):
        self.selected_category.set("Merchant")  # Set default category
        self.populate_tree()

    def populate_tree(self, event=None):
        self.tree.delete(*self.tree.get_children())
        selected_category = self.selected_category.get()
        
        if selected_category == "PPOB":
            for entry in self.data[0][selected_category]:
                values = (
                    entry.get('clientKeyPattern', ''),
                    entry.get('clientCallbackKey', ''),
                    entry.get('privateKey', ''),
                    entry.get('clientKey', '')
                )
                self.tree.insert("", "end", text=entry['clientId'], values=values)
        else:
            for entry in self.data[0][selected_category]:
                values = (
                    entry['clearPassword'],
                    entry['aggregatorToken'],
                    entry['privateKey'],
                    entry['clientSecret']
                )
                self.tree.insert("", "end", text=entry['aggregatorId'], values=values)

    def add_entry(self):
        self.open_entry_window("Add Entry", {})

    def edit_entry(self, event=None):
        selected_item = self.tree.focus()
        if selected_item:
            item_data = self.tree.item(selected_item)
            entry = self.get_entry_dict(item_data)
            self.open_entry_window("Edit Entry", entry)

    def get_entry_dict(self, item_data):
        selected_category = self.selected_category.get()
        if selected_category == "PPOB":
            return {
                'clientId': item_data['text'],
                'clientKeyPattern': item_data['values'][0],
                'clientCallbackKey': item_data['values'][1],
                'privateKey': item_data['values'][2],
                'clientKey': item_data['values'][3]
            }
        else:
            return {
                'aggregatorId': item_data['text'],
                'clearPassword': item_data['values'][0],
                'aggregatorToken': item_data['values'][1],
                'privateKey': item_data['values'][2],
                'clientSecret': item_data['values'][3]
            }

    def open_entry_window(self, title, entry):
        entry_window = tk.Toplevel(self)
        entry_window.title(title)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.3)

        entry_window.geometry(f"{window_width}x{window_height}")
        entry_window.minsize(int(screen_width * 0.3), int(screen_height * 0.3))
        entry_window.resizable(False, False)

        main_frame = ttk.Frame(entry_window, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        selected_category = self.selected_category.get()
        if selected_category == "PPOB":
            fields = ['clientId', 'clientKeyPattern', 'clientCallbackKey', 'privateKey', 'clientKey']
        else:
            fields = ['aggregatorId', 'clearPassword', 'aggregatorToken', 'privateKey', 'clientSecret']

        entries = {}

        for i, field in enumerate(fields):
            tk.Label(main_frame, text=field.capitalize() + ":", anchor="e").grid(row=i, column=0, sticky="e", padx=(0, 10), pady=5)
            entry_widget = ttk.Entry(main_frame, width=40)
            entry_widget.grid(row=i, column=1, sticky="ew", pady=5)
            entry_widget.insert(0, entry.get(field, ''))
            entries[field] = entry_widget

        def save_entry():
            new_entry = {field: entries[field].get() for field in fields}
            selected_category = self.selected_category.get()
            
            if title == "Edit Entry":
                if selected_category == "PPOB":
                    self.data[0][selected_category] = [new_entry if x['clientId'] == entry.get('clientId') else x for x in self.data[0][selected_category]]
                else:
                    self.data[0][selected_category] = [new_entry if x['aggregatorId'] == entry.get('aggregatorId') else x for x in self.data[0][selected_category]]
            else:
                self.data[0][selected_category].append(new_entry)
            
            self.populate_tree()
            entry_window.destroy()

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Save", command=save_entry, width=15).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=entry_window.destroy, width=15).pack(side=tk.LEFT)

        entry_window.transient(self.parent)
        entry_window.grab_set()
        self.parent.wait_window(entry_window)

    def remove_entry(self, event=None):
        selected_items = self.tree.selection()
        if selected_items:
            if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected entries?"):
                selected_category = self.selected_category.get()
                for item in selected_items:
                    item_id = self.tree.item(item)['text']
                    if selected_category == "PPOB":
                        self.data[0][selected_category] = [entry for entry in self.data[0][selected_category] if entry['clientId'] != item_id]
                    else:
                        self.data[0][selected_category] = [entry for entry in self.data[0][selected_category] if entry['aggregatorId'] != item_id]
                    self.tree.delete(item)

    def save_changes(self):
        with open(file_path, 'w') as file:
            json.dump(self.data, file, indent=4)
        messagebox.showinfo('Success', 'Aggregator config saved successfully.\nPlease restart the application to update the aggregator list.')
        Modules.get_list_dictionary_config()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Aggregator Configuration")
    app = AggregatorConfig(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.geometry("800x600")
    root.mainloop()