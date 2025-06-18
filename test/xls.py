import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import threading
import queue
import time
from pdf2docx import Converter
import pandas as pd
import tabula
import io
import sys
import logging

class PDFConverter:
    def __init__(self, master):
        self.master = master
        master.title("Konverter PDF")
        master.geometry("500x400")

        self.output_format = tk.StringVar(value="docx")
        
        self.format_frame = ttk.Frame(master)
        self.format_frame.pack(pady=10)
        ttk.Radiobutton(self.format_frame, text="DOCX", variable=self.output_format, value="docx").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.format_frame, text="XLSX", variable=self.output_format, value="xlsx").pack(side=tk.LEFT, padx=5)

        self.convert_button = ttk.Button(master, text="Pilih PDF dan Konversi", command=self.start_conversion)
        self.convert_button.pack(pady=10)

        self.progress_frame = ttk.Frame(master)
        self.progress_frame.pack(pady=5, padx=10, fill=tk.X)
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.progress_label = tk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT)

        self.time_label = tk.Label(master, text="")
        self.time_label.pack(pady=5)

        self.log_text = scrolledtext.ScrolledText(master, height=10)
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.queue = queue.Queue()
        self.log_queue = queue.Queue()

        # Set up logging
        self.setup_logging()

    def setup_logging(self):
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue

            def emit(self, record):
                self.log_queue.put(self.format(record))

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(queue_handler)

    def start_conversion(self):
        pdf_file = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not pdf_file:
            return

        output_format = self.output_format.get()
        output_file = filedialog.asksaveasfilename(
            defaultextension=f".{output_format}", 
            filetypes=[(f"{output_format.upper()} Files", f"*.{output_format}")]
        )
        if not output_file:
            return

        self.convert_button.config(state=tk.DISABLED)
        self.progress_bar["value"] = 0
        self.progress_label.config(text="0%")
        self.time_label.config(text="")
        self.log_text.delete('1.0', tk.END)

        thread = threading.Thread(target=self.convert_pdf, args=(pdf_file, output_file, output_format))
        thread.start()

        self.start_time = time.time()
        self.master.after(100, self.check_queue)
        self.master.after(100, self.check_log_queue)
        self.update_timer()

    def convert_pdf(self, pdf_file, output_file, output_format):
        try:
            if output_format == 'docx':
                self.convert_to_docx(pdf_file, output_file)
            else:
                self.convert_to_xlsx(pdf_file, output_file)

            self.queue.put(("conversion_complete", None))
        except Exception as e:
            logging.error(f"Terjadi kesalahan: {str(e)}")
            self.queue.put(("conversion_error", str(e)))

    def convert_to_docx(self, pdf_file, output_file):
        cv = Converter(pdf_file)
        cv.convert(output_file, start=0, end=None)
        cv.close()

    def convert_to_xlsx(self, pdf_file, output_file):
        logging.info(f"Mulai mengonversi {pdf_file} ke XLSX")
        dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            all_data = pd.concat(dfs, ignore_index=True)
            all_data.to_excel(writer, sheet_name='All_Data', index=False)
            logging.info(f"Data disimpan ke {output_file}")

        total_rows = len(all_data)
        for i in range(0, total_rows, 100):
            progress = min((i + 100) / total_rows * 100, 100)
            self.queue.put(("update_progress", progress))
            time.sleep(0.1)  # Simulasi proses untuk update progress

    def check_queue(self):
        try:
            message = self.queue.get(0)
            if message[0] == "update_progress":
                self.progress_bar["value"] = message[1]
                self.progress_label.config(text=f"{message[1]:.1f}%")
            elif message[0] == "conversion_complete":
                self.progress_bar["value"] = 100
                self.progress_label.config(text="100%")
                messagebox.showinfo("Sukses", f"File PDF berhasil dikonversi ke {self.output_format.get().upper()}")
                self.convert_button.config(state=tk.NORMAL)
                self.time_label.config(text="")
            elif message[0] == "conversion_error":
                messagebox.showerror("Error", f"Terjadi kesalahan: {message[1]}")
                self.convert_button.config(state=tk.NORMAL)
                self.time_label.config(text="")
        except queue.Empty:
            pass
        finally:
            self.master.after(100, self.check_queue)

    def check_log_queue(self):
        while True:
            try:
                log = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log + "\n")
                self.log_text.see(tk.END)
            except queue.Empty:
                break
        self.master.after(100, self.check_log_queue)

    def update_timer(self):
        if self.convert_button['state'] == tk.DISABLED:
            elapsed_time = int(time.time() - self.start_time)
            estimated_total_time = elapsed_time * 100 / max(self.progress_bar["value"], 1)
            remaining_time = max(int(estimated_total_time - elapsed_time), 0)
            
            minutes, seconds = divmod(remaining_time, 60)
            self.time_label.config(text=f"Perkiraan waktu tersisa: {minutes:02d}:{seconds:02d}")
            
            self.master.after(1000, self.update_timer)

root = tk.Tk()
app = PDFConverter(root)
root.mainloop()