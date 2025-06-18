import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from app.custom.custom_treeview import CustomTreeview
from app.custom.custom_text import CustomText

class QueryResultWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Query Result")
        self.geometry("1000x700")  # Memperbesar ukuran default window

        self.style = ttk.Style(self)
        #self.style.theme_use("clam")  # Menggunakan tema 'clam' untuk tampilan yang lebih modern
        self.configure_styles()

        self.create_widgets()
        self.result_frames = []

    def configure_styles(self):
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        self.style.configure("TNotebook.Tab", padding=[10, 5])

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.close_button = ttk.Button(self, text="Close", command=self.destroy)
        self.close_button.pack(pady=10)

    def set_query_text(self, query_text):
        result_frame = ttk.Frame(self.notebook)
        self.notebook.add(result_frame, text=f"Query {len(self.result_frames) + 1}")

        query_text_widget = CustomText(result_frame, height=5, wrap=tk.WORD)
        query_text_widget.pack(fill=tk.X, padx=10, pady=10)
        query_text_widget.insert(tk.END, query_text)
        query_text_widget.config(state=tk.DISABLED)

        tree_frame = ttk.Frame(result_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Vertical scrollbar
        tree_scrolly = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scrolly.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        tree_scrollx = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scrollx.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        result_tree = CustomTreeview(tree_frame, yscrollcommand=tree_scrolly.set, xscrollcommand=tree_scrollx.set)
        result_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configure scrollbars
        tree_scrolly.config(command=result_tree.yview)
        tree_scrollx.config(command=result_tree.xview)

        self.result_frames.append((result_frame, result_tree, query_text, tree_scrollx, tree_scrolly))
        self.notebook.select(result_frame)

    def set_result_data(self, data, column_names, query_text):
        for result_frame, result_tree, tab_query_text, tree_scrollx, tree_scrolly in self.result_frames:
            if tab_query_text == query_text:
                result_tree['columns'] = column_names
                result_tree['show'] = 'headings'

                for col in column_names:
                    result_tree.heading(col, text=col, anchor=tk.W)
                    result_tree.column(col, anchor=tk.W, minwidth=100)  # Set minimum width

                for row in data:
                    result_tree.insert("", tk.END, values=row)

                self.autosize_columns(result_tree)
                
                # Ensure scrollbars are properly configured
                result_tree.configure(xscrollcommand=tree_scrollx.set, yscrollcommand=tree_scrolly.set)
                tree_scrollx.configure(command=result_tree.xview)
                tree_scrolly.configure(command=result_tree.yview)
                break

    def autosize_columns(self, treeview):
        max_width = 300  # Maximum column width
        for col in treeview['columns']:
            # Mengukur lebar teks header
            header_width = tkfont.Font().measure(col) + 20
            
            # Mengukur lebar konten terpanjang
            max_content_width = max(
                tkfont.Font().measure(str(treeview.set(child, col))) 
                for child in treeview.get_children('')
            ) + 20

            # Menggunakan lebar yang lebih besar antara header dan konten
            width = max(header_width, max_content_width)
            
            # Membatasi lebar maksimum
            width = min(width, max_width)
            
            treeview.column(col, width=width)