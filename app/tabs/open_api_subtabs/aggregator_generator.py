import tkinter as tk
from tkinter import ttk
from src.generate_cred_snap import OAuth2GenerateTokoNetzmeRequestHelper, OAuth2GenerateNetzmeRequestHelper

class AggregatorGenerator(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Menggunakan ttk untuk semua widget
        self.style = ttk.Style()
        self.style.configure('TFrame', padding=(10, 10))
        self.style.configure('TButton', padding=(5, 5))
        self.style.configure('TLabel', padding=(5, 5))
        
        # Label dan Entry untuk ID
        self.label_id = ttk.Label(self, text="ID:")
        self.label_id.grid(row=0, column=0, padx=10, pady=5, sticky="W")
        self.entry_id = ttk.Entry(self, width=30)
        self.entry_id.grid(row=0, column=1, padx=10, pady=5, sticky="EW")

        # Label dan Entry untuk Name
        self.label_name = ttk.Label(self, text="Name:")
        self.label_name.grid(row=1, column=0, padx=10, pady=5, sticky="W")
        self.entry_name = ttk.Entry(self, width=30)
        self.entry_name.grid(row=1, column=1, padx=10, pady=5, sticky="EW")

        # Label dan Combobox untuk Type
        self.label_type = ttk.Label(self, text="Type:")
        self.label_type.grid(row=2, column=0, padx=10, pady=5, sticky="W")
        self.combobox_type = ttk.Combobox(self, values=["Toko Netzme", "Netzme"], state="readonly", width=28)
        self.combobox_type.grid(row=2, column=1, padx=10, pady=5, sticky="EW")
        self.combobox_type.current(0)  # Set default value

        # Tombol Generate
        self.button_generate = ttk.Button(self, text="Generate", command=self.generate_output)
        self.button_generate.grid(row=3, column=0, columnspan=2, pady=10, sticky="EW")

        # Text Output
        self.text_output = tk.Text(self, height=34, width=50, wrap="word")
        self.text_output.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="EW")
        
        # Mengatur agar kolom 1 (entry dan combobox) dapat diperluas secara horizontal
        self.columnconfigure(1, weight=1)

    def generate_output(self):
        id_value = self.entry_id.get()
        name_value = self.entry_name.get()
        type_value = self.combobox_type.get()
        if type_value == "Netzme":
            helper = OAuth2GenerateNetzmeRequestHelper()
            output = helper.generate_netzme_aggregator_user_snap(id=id_value, name=name_value)
        else:
            helper = OAuth2GenerateTokoNetzmeRequestHelper()
            output = helper.generate_toko_netzme_aggregator_user_snap(id=id_value, name=name_value)
        
        self.text_output.delete(1.0, tk.END)  # Clear previous output
        self.text_output.insert(tk.END, output)