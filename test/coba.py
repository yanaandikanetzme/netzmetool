import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import numpy as np
import cv2
import fitz  # PyMuPDF for PDF support
import io
import os

class BackgroundChangerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Pengubah Latar Belakang Foto")
        self.master.geometry("1200x800")

        self.image_path = None
        self.original_image = None
        self.modified_image = None
        self.background_changed = False

        # Load cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        self.upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Image frames
        self.original_frame = ttk.LabelFrame(main_frame, text="Gambar Asli", padding="5")
        self.original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.modified_frame = ttk.LabelFrame(main_frame, text="Gambar Hasil", padding="5")
        self.modified_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Image labels
        self.original_label = ttk.Label(self.original_frame)
        self.original_label.pack(expand=True, fill=tk.BOTH)
        self.modified_label = ttk.Label(self.modified_frame)
        self.modified_label.pack(expand=True, fill=tk.BOTH)

        # Control frame
        control_frame = ttk.Frame(main_frame, padding="5")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Buttons
        self.select_button = ttk.Button(control_frame, text="Pilih Foto", command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.color_button = ttk.Button(control_frame, text="Pilih Warna Latar", command=self.choose_color)
        self.color_button.grid(row=0, column=1, padx=5, pady=5)

        self.save_button = ttk.Button(control_frame, text="Simpan Gambar", command=self.save_image)
        self.save_button.grid(row=0, column=2, padx=5, pady=5)

        self.compress_button = ttk.Button(control_frame, text="Kompres File", command=self.compress_file)
        self.compress_button.grid(row=0, column=3, padx=5, pady=5)

        self.combine_pdf_button = ttk.Button(control_frame, text="Gabung PDF", command=self.combine_pdf)
        self.combine_pdf_button.grid(row=0, column=4, padx=5, pady=5)

        # File size estimation label
        self.file_size_label = ttk.Label(control_frame, text="Estimasi Ukuran File: -")
        self.file_size_label.grid(row=1, column=0, columnspan=5, padx=5, pady=5)

        # Configure grid
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.pdf")])
        if self.image_path:
            if self.image_path.lower().endswith('.pdf'):
                self.original_image = self.pdf_to_image(self.image_path)
            else:
                self.original_image = Image.open(self.image_path)
            self.modified_image = self.original_image.copy()
            self.background_changed = False
            self.show_image(self.original_image, self.original_label)
            self.show_image(self.modified_image, self.modified_label)
            self.update_file_size_estimation()

    def pdf_to_image(self, pdf_path):
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # Load first page
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        return img

    def show_image(self, image, label):
        width, height = 500, 500
        image.thumbnail((width, height))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo

    def choose_color(self):
        color = colorchooser.askcolor(title="Pilih warna latar belakang")[1]
        if color and self.original_image:
            self.change_background(color)

    def change_background(self, new_color):
        image = np.array(self.original_image)
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Deteksi wajah, tubuh penuh, dan tubuh bagian atas
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        bodies = self.body_cascade.detectMultiScale(gray, 1.1, 3)
        upper_bodies = self.upper_body_cascade.detectMultiScale(gray, 1.1, 3)
        
        # Buat mask
        mask = np.zeros(image.shape[:2], np.uint8)
        mask[:] = cv2.GC_PR_BGD
        
        # Fungsi untuk menandai area pada mask
        def mark_area(x, y, w, h, value):
            cv2.rectangle(mask, (x, y), (x+w, y+h), value, -1)
        
        # Tandai area wajah, tubuh, dan tubuh bagian atas
        for (x, y, w, h) in faces:
            mark_area(x, y, w, h, cv2.GC_FGD)
            mark_area(x-w//4, y-h//4, w+w//2, h+h//2, cv2.GC_PR_FGD)  # Area sekitar wajah
        
        for (x, y, w, h) in bodies:
            mark_area(x, y, w, h, cv2.GC_PR_FGD)
        
        for (x, y, w, h) in upper_bodies:
            mark_area(x, y, w, h, cv2.GC_PR_FGD)
        
        # Jika tidak ada tubuh terdeteksi, perkirakan area tubuh dari wajah
        if len(bodies) == 0 and len(upper_bodies) == 0 and len(faces) > 0:
            for (x, y, w, h) in faces:
                mark_area(x-w//2, y+h, w*2, h*3, cv2.GC_PR_FGD)
        
        # Tambahkan edge detection
        edges = cv2.Canny(gray, 50, 150)
        mask[edges != 0] = cv2.GC_PR_FGD
        
        # GrabCut
        bgdModel = np.zeros((1,65), np.float64)
        fgdModel = np.zeros((1,65), np.float64)
        rect = (0, 0, image.shape[1], image.shape[0])
        cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_MASK)
        
        # Buat mask final
        mask2 = np.where((mask == cv2.GC_PR_BGD) | (mask == cv2.GC_BGD), 0, 1).astype('uint8')
        
        # Terapkan operasi morfologi
        kernel = np.ones((5,5), np.uint8)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel)
        mask2 = cv2.morphologyEx(mask2, cv2.MORPH_OPEN, kernel)
        
        # Ubah warna latar belakang
        r, g, b = tuple(int(new_color[i:i+2], 16) for i in (1, 3, 5))
        background = np.full(image.shape, (r, g, b), dtype=np.uint8)
        
        # Apply improved blending
        blurred_mask = cv2.GaussianBlur(mask2.astype(float), (15, 15), 0)
        blurred_mask = np.repeat(blurred_mask[:, :, np.newaxis], 3, axis=2)
        result = image * blurred_mask + background * (1 - blurred_mask)
        
        self.modified_image = Image.fromarray(result.astype('uint8'))
        self.background_changed = True
        self.show_image(self.modified_image, self.modified_label)
        self.update_file_size_estimation()

    def save_image(self):
        if self.modified_image:
            file_types = [
                ('JPEG', '*.jpg'),
                ('PNG', '*.png'),
                ('PDF', '*.pdf'),
                ('JPEG', '*.jpeg')
            ]
            save_path = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=".png")
            if save_path:
                if save_path.lower().endswith('.pdf'):
                    self.save_as_pdf(save_path)
                else:
                    if self.background_changed:
                        self.modified_image.save(save_path)
                    else:
                        self.original_image.save(save_path)
                print(f"Gambar disimpan ke: {save_path}")

    def save_as_pdf(self, save_path):
        doc = fitz.open()
        img_byte_arr = io.BytesIO()
        image_to_save = self.modified_image if self.background_changed else self.original_image
        image_to_save.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        img_rect = fitz.Rect(0, 0, image_to_save.width, image_to_save.height)
        page = doc.new_page(width=image_to_save.width, height=image_to_save.height)
        page.insert_image(img_rect, stream=img_bytes)
        doc.save(save_path)
        doc.close()

    def compress_file(self):
        if not self.original_image:
            messagebox.showerror("Error", "Please select an image first")
            return

        quality = tk.simpledialog.askinteger("Compress", "Enter compression quality (1-100):", minvalue=1, maxvalue=100)
        if quality is None:
            return

        save_path = filedialog.asksaveasfilename(filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if save_path:
            image_to_compress = self.modified_image if self.background_changed else self.original_image
            image_to_compress.save(save_path, optimize=True, quality=quality)
            messagebox.showinfo("Success", f"Compressed image saved to: {save_path}")
            self.update_file_size_estimation(save_path)

    def combine_pdf(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not file_paths:
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not save_path:
            return

        pdf_writer = fitz.open()
        for path in file_paths:
            pdf_reader = fitz.open(path)
            pdf_writer.insert_pdf(pdf_reader)
        
        pdf_writer.save(save_path)
        pdf_writer.close()
        messagebox.showinfo("Success", f"Combined PDF saved to: {save_path}")

    def update_file_size_estimation(self, path=None):
        if path:
            size = os.path.getsize(path)
        else:
            img_byte_arr = io.BytesIO()
            image_to_estimate = self.modified_image if self.background_changed else self.original_image
            image_to_estimate.save(img_byte_arr, format='PNG')
            size = img_byte_arr.tell()
        
        size_kb = size / 1024
        if size_kb < 1000:
            size_str = f"{size_kb:.2f} KB"
        else:
            size_mb = size_kb / 1024
            size_str = f"{size_mb:.2f} MB"
        
        self.file_size_label.config(text=f"Estimasi Ukuran File: {size_str}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundChangerApp(root)
    root.mainloop()