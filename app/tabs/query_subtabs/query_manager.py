#lokasi file app/tabs/query_manager.py
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import json
import platform
from app.custom.custom_treeview import CustomTreeview
from app.custom.custom_text import CustomText

class QueryManager:
    def __init__(self, parent_window, parent_tab):
        self.parent_tab = parent_tab
        self.root = parent_window
        self.load_data()
        self.database_treeview = None  # Tambahkan inisialisasi self.database_treeview
        self.group_treeview = None  # Tambahkan inisialisasi self.group_treeview
        self.setup_ui()

    def setup_ui(self):
        self.setup_treeviews()
        self.setup_buttons()
        self.setup_bindings()
        self.display_data_database()
        self.get_selected_database_value(None)
        self.group_treeview.bind("<<TreeviewSelect>>", self.get_selected_group_value)  # Tambahkan baris ini

    def setup_treeviews(self):
        self.database_treeview = CustomTreeview(self.root, columns=("Database",), show="headings")
        self.database_treeview.heading("Database", text="Database")
        self.database_treeview.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.group_treeview = CustomTreeview(self.root, columns=("Group",), show="headings")
        self.group_treeview.heading("Group", text="Group")
        self.group_treeview.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.query_text = CustomText(self.root, width=40)
        self.query_text.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

    def setup_buttons(self):
        ttk.Button(self.root, text="Tambah Database", command=self.add_database).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.root, text="Tambah Group", command=self.add_group).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.root, text="Save Query", command=self.edit_query).grid(row=2, column=2, padx=5, pady=5)
        
    def setup_bindings(self):
        delete_key = "<BackSpace>" if platform.system() == "Darwin" else "<Delete>"
        self.database_treeview.bind(delete_key, self.delete_database)
        self.group_treeview.bind(delete_key, self.delete_group)
        self.database_treeview.bind("<Double-1>", self.edit_database)
        self.group_treeview.bind("<Double-1>", self.edit_group)
        self.database_treeview.bind("<<TreeviewSelect>>", self.get_selected_database_value)
        self.group_treeview.bind("<<TreeviewSelect>>", self.get_selected_group_value)

    def load_data(self):
        self.read_json()  # Panggil self.read_json() saja di sini

    def read_json(self):
        with open("config/saved_query.json", "r") as file:
            data = json.load(file)
        return data

    def write_json(self, data):
        with open("config/saved_query.json", "w") as file:
            json.dump(data, file, indent=2)
        self.parent_tab.saved_queries = data  # Modifikasi baris ini
        self.parent_tab.update_combos()  # Modifikasi baris ini

    def display_data_database(self, event=None):
        try:
            data = self.read_json()
            self.database_treeview.delete(*self.database_treeview.get_children())
            for database in data.keys():
                self.database_treeview.insert("", tk.END, values=(database,))
        except:
            pass

    def display_data_group(self, event=None):
        try:
            if self.data_database:  # Memastikan bahwa data_database tidak kosong
                data = self.read_json()
                data_group_list = self.get_group_names(data, self.data_database[0])
                self.group_treeview.delete(*self.group_treeview.get_children())
                for item in data_group_list:
                    self.group_treeview.insert("", tk.END, values=(item,))
            else:
                messagebox.showinfo("Info", "Tidak ada database yang dipilih.")
        except:
            pass

    def display_data_query(self, event=None):
        try:
            if self.data_database and self.data_group:  # Memastikan bahwa data_database dan data_group tidak kosong
                data = self.read_json()
                query_list = self.get_query_names(data, self.data_database[0], self.data_group[0])
                self.query_text.delete('1.0', tk.END)
                self.query_text.insert(tk.END, query_list)
            else:
                messagebox.showinfo("Info", "Tidak ada database atau grup yang dipilih.")
        except:
            pass

    def get_group_names(self, json_data, database_name):
        if database_name in json_data:
            groups = [entry["Group"] for entry in json_data[database_name]]
            return groups
        else:
            return []

    def get_query_names(self, data, database, group):
        queries = []
        if database in data:
            for item in data[database]:
                if item["Group"] == group:
                    queries = item["Query"]
                    break
        return "\n".join(queries)

    def get_selected_database_value(self, event):
        selected_item = self.database_treeview.selection()
        if selected_item:
            selected_value = self.database_treeview.item(selected_item)['values'][0]
            self.data_database = [selected_value]  # Menyimpan database yang dipilih
            self.display_data_group()  # Panggil display_data_group di sini
            self.query_text.delete('1.0', tk.END)
        else:
            self.group_treeview.delete(*self.group_treeview.get_children())
            self.query_text.delete('1.0', tk.END)

    def get_selected_group_value(self, event):
        selected_item = self.group_treeview.selection()
        if selected_item:
            selected_value = self.group_treeview.item(selected_item)['values'][0]
            self.data_group = [selected_value]  # Menyimpan grup yang dipilih
            self.display_data_query()

    def add_database(self):
        try:
            new_database = simpledialog.askstring("Tambah Database", "Masukkan nama Database baru:")
            if new_database:
                data = self.read_json()
                if new_database not in data:
                    data[new_database] = []
                    self.write_json(data)
                    self.display_data_database()
                else:
                    messagebox.showerror("Error", f"Database '{new_database}' sudah ada.")
        except:
            pass

    def add_group(self):
        try:
            selected_database = self.database_treeview.selection()
            if selected_database:
                database_name = self.database_treeview.item(selected_database)['values'][0]
                new_group = simpledialog.askstring("Tambah Group", "Masukkan nama Group baru:")
                if new_group:
                    data = self.read_json()
                    group_exists = any(item["Group"] == new_group for item in data[database_name])
                    if not group_exists:
                        data[database_name].append({"Group": new_group, "Query": []})
                        self.write_json(data)
                        if self.group_treeview:
                            self.display_data_group()
                    else:
                        messagebox.showerror("Error", f"Group '{new_group}' sudah ada di Database '{database_name}'.")
            else:
                messagebox.showerror("Error", "Pilih Database terlebih dahulu.")
        except:
            pass

    def delete_database(self, event):
        try:
            selected_item = self.database_treeview.selection()
            if selected_item:
                database_name = self.database_treeview.item(selected_item)['values'][0]
                confirm = messagebox.askyesno("Konfirmasi Penghapusan", f"Anda yakin ingin menghapus Database '{database_name}'?")
                if confirm:
                    data = self.read_json()
                    del data[database_name]
                    self.write_json(data)
                    self.display_data_database()
                    self.data_database.clear()
                    self.data_group.clear()
                    self.query_text.delete('1.0', tk.END)
                    self.group_treeview.delete(*self.group_treeview.get_children())
        except:
            pass

    def delete_group(self, event):
        try:
            selected_database = self.database_treeview.selection()
            selected_group = self.group_treeview.selection()
            if selected_database and selected_group:
                database_name = self.database_treeview.item(selected_database)['values'][0]
                group_name = self.group_treeview.item(selected_group)['values'][0]
                confirm = messagebox.askyesno("Konfirmasi Penghapusan", f"Anda yakin ingin menghapus Group '{group_name}' beserta query-nya?")
                if confirm:
                    data = self.read_json()
                    data[database_name] = [item for item in data[database_name] if item["Group"] != group_name]
                    self.write_json(data)
                    self.display_data_group()
                    self.data_group.clear()
                    self.query_text.delete('1.0', tk.END)
                    self.group_treeview.delete(*self.group_treeview.get_children())
        except:
            pass

    def edit_database(self, event):
        try:
            selected_item = self.database_treeview.selection()
            if selected_item:
                database_name = self.database_treeview.item(selected_item)['values'][0]
                new_name = simpledialog.askstring("Edit Database", "Masukkan nama Database baru:", initialvalue=database_name)
                if new_name and new_name != database_name:
                    data = self.read_json()
                    data[new_name] = data.pop(database_name)
                    self.write_json(data)
                    self.display_data_database()
        except:
            pass

    def edit_group(self, event):
        try:
            selected_database = self.database_treeview.selection()
            selected_group = self.group_treeview.selection()
            if selected_database and selected_group:
                database_name = self.database_treeview.item(selected_database)['values'][0]
                group_name = self.group_treeview.item(selected_group)['values'][0]
                new_name = simpledialog.askstring("Edit Group", "Masukkan nama Group baru:", initialvalue=group_name)
                if new_name and new_name != group_name:
                    data = self.read_json()
                    for item in data[database_name]:
                        if item["Group"] == group_name:
                            item["Group"] = new_name
                            break
                    self.write_json(data)
                    self.display_data_group()
        except:
            pass

    def edit_query(self):
        try:
            selected_database = self.database_treeview.selection()
            selected_group = self.group_treeview.selection()
            if selected_database and selected_group:
                database_name = self.database_treeview.item(selected_database)['values'][0]
                group_name = self.group_treeview.item(selected_group)['values'][0]
                new_queries = [query.strip() for query in self.query_text.get("1.0", tk.END).strip().split('\n') if query.strip()]
                data = self.read_json()
                for item in data[database_name]:
                    if item["Group"] == group_name:
                        item["Query"] = [query + ";" if not query.endswith(";") else query for query in "\n".join(new_queries).split(';') if query.strip()]
                        break
                self.write_json(data)
                self.display_data_query()
        except:
            pass

    def update_combos(self):
        self.saved_queries = self.load_saved_queries()
        self.combo_environment['values'] = list(self.saved_queries.keys())
        self.update_saved_query_combo(None)
        if self.manager_window:
            self.manager_window.destroy()
            self.manager_window = None

    def update_combos(self):
        self.saved_queries = self.load_saved_queries()
        self.combo_environment['values'] = list(self.saved_queries.keys())
        
        # Mendapatkan environment yang saat ini dipilih
        current_environment = self.combo_environment.get()
        
        self.update_saved_query_combo(None)
        
        # Memilih kembali environment yang sama setelah memperbarui combo_saved_query
        if current_environment:
            self.combo_environment.set(current_environment)
            self.load_selected_queries(None)
        
        if self.manager_window:
            self.manager_window.destroy()
            self.manager_window = None
def main():
    root = tk.Tk()
    app = QueryManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
