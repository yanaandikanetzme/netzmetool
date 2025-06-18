# app/tabs/tools_subtabs/generator_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from app.custom.custom_scrolledtext import CustomScrolledText
from PIL import Image, ImageTk
import qrcode
import cv2
import base64
import io
import threading
import uuid

class GeneratorTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_ui()

    def create_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Main frame
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Input")
        input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        input_frame.columnconfigure(0, weight=1)

        # Input type selection
        self.input_type = tk.StringVar(value="text")
        ttk.Radiobutton(input_frame, text="Text", variable=self.input_type, value="text", command=self.toggle_input_type).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Radiobutton(input_frame, text="File", variable=self.input_type, value="file", command=self.toggle_input_type).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Text input
        self.text_input = CustomScrolledText(input_frame, width=40, height=5)
        self.text_input.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        # File input
        self.file_frame = ttk.Frame(input_frame)
        self.file_path = tk.StringVar()
        ttk.Entry(self.file_frame, textvariable=self.file_path).grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        ttk.Button(self.file_frame, text="Browse", command=self.browse_file).grid(row=0, column=1, padx=5, pady=5)
        self.file_frame.columnconfigure(0, weight=1)
        self.file_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.file_frame.grid_remove()

        # Action frame
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        action_frame.columnconfigure(0, weight=1)

        # Action buttons
        self.qr_button = ttk.Button(action_frame, text="Encode to QR", command=self.handle_qr)
        self.qr_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.base64_button = ttk.Button(action_frame, text="Encode to Base64", command=self.handle_base64)
        self.base64_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        # New button for decoding Base64 to image
        self.base64_to_image_button = ttk.Button(action_frame, text="Decode Base64 to Image", command=self.decode_base64_to_image)
        self.base64_to_image_button.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        ttk.Button(action_frame, text="Generate UUID", command=self.generate_uuid).grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # Initialize the visibility of base64_to_image_button based on initial input type
        self.toggle_input_type()

        # Result frame
        result_frame = ttk.LabelFrame(self, text="Result")
        result_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)

        # Result text
        self.result_text = CustomScrolledText(result_frame, width=60, height=10)
        self.result_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Image display
        self.img_label = tk.Label(result_frame)
        self.img_label.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def toggle_input_type(self):
        if self.input_type.get() == "file":
            self.text_input.grid_remove()
            self.file_frame.grid()
            self.qr_button.config(text="Decode QR")
            self.base64_button.config(text="Encode to Base64")
            self.base64_to_image_button.grid_remove()  # Hide the button
        else:
            self.file_frame.grid_remove()
            self.text_input.grid()
            self.qr_button.config(text="Encode to QR")
            self.base64_button.config(text="Encode to Base64")
            self.base64_to_image_button.grid()  # Show the button

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")])
        if file_path:
            self.file_path.set(file_path)
            self.display_image(file_path)

    def display_image(self, file_path):
        try:
            img = Image.open(file_path)
            img.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(img)
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while displaying the image: {str(e)}")

    def handle_qr(self):
        if self.input_type.get() == "file":
            self.decode_qr_from_file()
        else:
            self.encode_to_qr()

    def handle_base64(self):
        if self.input_type.get() == "file":
            self.encode_file_to_base64()
        else:
            self.encode_text_to_base64()

    def decode_base64_to_image(self):
        base64_string = self.text_input.get("1.0", 'end-1c').strip()
        if not base64_string:
            messagebox.showerror("Error", "Please enter a Base64 encoded string.")
            return

        try:
            # Decode the Base64 string
            image_data = base64.b64decode(base64_string)
            
            # Create a PIL Image object
            image = Image.open(io.BytesIO(image_data))
            
            # Display the image
            image.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(image)
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Base64 decoded and image displayed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while decoding Base64 to image: {str(e)}")
            
    def decode_qr_from_file(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        try:
            image = cv2.imread(file_path)
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(image)
            
            if bbox is not None and data:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, data)
            else:
                messagebox.showinfo("Result", "No QR code found in the image.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def encode_to_qr(self):
        text = self.text_input.get("1.0", 'end-1c')
        if not text:
            messagebox.showerror("Error", "Please enter some text to encode.")
            return

        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            img.thumbnail((300, 300))
            img_tk = ImageTk.PhotoImage(img)
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "QR Code generated and displayed.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating QR code: {str(e)}")

    def encode_file_to_base64(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.")
            return

        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, encoded_string)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while encoding: {str(e)}")

    def encode_text_to_base64(self):
        text = self.text_input.get("1.0", 'end-1c')
        if not text:
            messagebox.showerror("Error", "Please enter some text to encode.")
            return

        try:
            encoded_string = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, encoded_string)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while encoding: {str(e)}")

    def generate_uuid(self):
        new_uuid = str(uuid.uuid4())
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, new_uuid)