# main.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.tabs.qr_tab import QRTab
from app.tabs.invoice_tab import InvoiceTab
from app.tabs.tools_tab import ToolsTab
from app.tabs.open_api_tab import OpenAPITab
from app.tabs.settlement_manual_tab import SettlementManualTab
from app.tabs.check_balance import CheckBalance
from app.tabs.query_tab import QueryTab
from config.value_handler import save_values, load_values
from PIL import Image, ImageTk
from src.modules import Modules
import platform

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Netzme Tool")
        
        # Dynamically set the window size based on screen resolution
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.8)
        
        self.geometry(f"{window_width}x{window_height}")
        self.minsize(int(screen_width * 0.5), int(screen_height * 0.5))  # Set minimum size to 50% of the screen
        
        self.resizable(True, True)  # Allow the window to be resized
        self.overrideredirect(False)  # Show window border and title

        # Set dark theme
        #self.set_dark_theme()

        # Set icon (platform-specific)
        self.set_icon()

        # Tab Control
        self.tab_control = ttk.Notebook(self)

        # QR Tab
        self.qr_tab = QRTab(self.tab_control)
        self.tab_control.add(self.qr_tab, text="QR")

        # Invoice Tab
        self.invoice_tab = InvoiceTab(self.tab_control)
        self.tab_control.add(self.invoice_tab, text="Invoice")

        # Tools Tab
        self.tools_tab = ToolsTab(self.tab_control)
        self.tab_control.add(self.tools_tab, text="Tools")

        # Open API Tab
        self.open_api_tab = OpenAPITab(self.tab_control)
        self.tab_control.add(self.open_api_tab, text="Open API")

        # Settlement Manual Tab
        self.settlement_manual_tab = SettlementManualTab(self.tab_control)
        self.tab_control.add(self.settlement_manual_tab, text="Settlement Manual")

        # Query Tab
        self.query_tab = QueryTab(self.tab_control)
        self.tab_control.add(self.query_tab, text="Query Tab")

        # Check Balance
        self.check_balance_tab = CheckBalance(self.tab_control)
        self.tab_control.add(self.check_balance_tab, text="Check Balance")

        self.tab_control.pack(expand=1, fill="both")

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        Modules.hapus_pycache()

    def set_dark_theme(self):
        # Configure dark theme colors
        bg_color = "#2E2E2E"
        fg_color = "#FFFFFF"
        select_color = "#4A4A4A"
        accent_color = "#007ACC"
        
        style = ttk.Style(self)
        style.theme_use('alt')  # Use the 'alt' theme as a base

        # Configure colors for various widget states
        style.configure(".", background=bg_color, foreground=fg_color)
        style.map(".", background=[('selected', select_color)])
        
        # Notebook (Tab control)
        style.configure("TNotebook", background=bg_color)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color)
        style.map("TNotebook.Tab", background=[("selected", select_color)])
        
        # Frame
        style.configure("TFrame", background=bg_color)
        
        # Button
        style.configure("TButton", background=bg_color, foreground=fg_color)
        style.map("TButton", background=[("active", accent_color)])
        
        # Label
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        
        # Entry
        style.configure("TEntry", fieldbackground=bg_color, foreground=fg_color)
        style.map("TEntry", fieldbackground=[("focus", select_color)])
        
        # Combobox
        style.configure("TCombobox", fieldbackground=bg_color, background=bg_color, foreground=fg_color)
        style.map("TCombobox", fieldbackground=[("readonly", bg_color)], background=[("readonly", bg_color)])
        
        # Checkbutton
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
        style.map("TCheckbutton", background=[("active", select_color)])
        
        # Radiobutton
        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        style.map("TRadiobutton", background=[("active", select_color)])
        
        # Scale (Slider)
        style.configure("TScale", background=bg_color, foreground=fg_color, troughcolor=select_color)
        
        # Progressbar
        style.configure("TProgressbar", background=accent_color, troughcolor=bg_color)
        
        # Treeview
        style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color)
        style.map("Treeview", background=[("selected", select_color)])
        style.configure("Treeview.Heading", background=select_color, foreground=fg_color)
        
        # Scrollbar
        style.configure("TScrollbar", background=bg_color, troughcolor=select_color, bordercolor=bg_color, arrowcolor=fg_color)
        
        # Spinbox
        style.configure("TSpinbox", fieldbackground=bg_color, background=bg_color, foreground=fg_color, arrowcolor=fg_color)
        
        # Separator
        style.configure("TSeparator", background=select_color)
        
        # Sizegrip
        style.configure("TSizegrip", background=bg_color)

        # Menu (this is a tk widget, not ttk)
        self.option_add("*Menu.background", bg_color)
        self.option_add("*Menu.foreground", fg_color)
        self.option_add("*Menu.selectColor", select_color)
        self.option_add("*Menu.activeBackground", select_color)
        self.option_add("*Menu.activeForeground", fg_color)

        # Configure colors for standard tk widgets (if used)
        self.configure(bg=bg_color)
        self.option_add("*Background", bg_color)
        self.option_add("*Foreground", fg_color)
        self.option_add("*selectBackground", select_color)
        self.option_add("*selectForeground", fg_color)

    def set_icon(self):
        try:
            icon_path = "app/rock.png"
            if platform.system() == "Windows":
                self.iconbitmap(icon_path)
            else:
                icon_img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(icon_img)
                self.iconphoto(False, photo)
        except Exception as e:
            print(f"Error setting icon: {e}")

    def on_closing(self):
        save_values(self)
        self.destroy()

if __name__ == "__main__":
    root = App()
    load_values(root)
    root.mainloop()