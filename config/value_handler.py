#config/value_handler.py
import json
from tkinter import Entry
from tkinter.ttk import Combobox
from app.custom.custom_text import CustomText
from app.custom.custom_treeview import CustomTreeview

def save_values(root, file_path="savedvalues.json"):
    """ Save the values of all Entry, Combobox, and CustomText widgets in the application to a JSON file. """
    values = {}

    def get_widget_value(widget):
        if isinstance(widget, Entry):
            return widget.get()
        elif isinstance(widget, Combobox):
            state = str(widget.cget('state'))
            if state == 'readonly':
                current_value = widget.get()
                values = widget.cget('values')
                if current_value in values:
                    return values.index(current_value)  # Mengembalikan indeks nilai
                else:
                    return -1  # Mengembalikan -1 jika nilai tidak ditemukan
            else:
                return widget.get()
        elif isinstance(widget, CustomText):
            return widget.get("1.0", "end-1c")  # Mendapatkan teks dari CustomText
        elif isinstance(widget, CustomTreeview):  # Tambahkan kasus ini
            items = widget.get_children()
            values = [widget.item(item, "values") for item in items]
            return values

    def traverse_widgets(parent, parent_path):
        for widget in parent.winfo_children():
            widget_path = parent_path + "." + widget.winfo_name()
            widget_value = get_widget_value(widget)
            if widget_value is not None:
                values[widget_path] = widget_value
            traverse_widgets(widget, widget_path)

    traverse_widgets(root, "")
    with open(file_path, "w") as file:
        json.dump(values, file, indent=4)

def load_values(root, file_path="savedvalues.json"):
    """ Load the values from the JSON file and set them to the corresponding Entry, Combobox, and CustomText widgets in the application. """
    try:
        with open(file_path, "r") as file:
            values = json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found. No values will be loaded.")
        return

    def set_widget_value(widget, value):
        if isinstance(widget, Entry):
            widget.delete(0, "end")
            widget.insert(0, value)
        elif isinstance(widget, Combobox):
            widget.set(value)
        elif isinstance(widget, CustomText):
            widget.delete("1.0", "end")  # Menghapus teks saat ini
            widget.insert("1.0", value)  # Mengisi dengan nilai baru
        elif isinstance(widget, CustomTreeview):  # Tambahkan kasus ini
            widget.delete(*widget.get_children())  # Hapus semua item yang ada
            for item_values in value:
                widget.insert("", "end", values=item_values)

    def traverse_widgets(parent, parent_path):
        for widget in parent.winfo_children():
            widget_path = parent_path + "." + widget.winfo_name()
            if widget_path in values:
                value = values[widget_path]
                if isinstance(widget, Combobox):
                    widget.config(state='normal')
                    set_widget_value(widget, value)
                    widget.config(state='readonly')
                else:
                    set_widget_value(widget, value)
            traverse_widgets(widget, widget_path)

    traverse_widgets(root, "")