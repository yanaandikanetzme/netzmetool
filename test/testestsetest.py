import tkinter as tk
from tkinter import ttk
import subprocess
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk, ImageDraw
import pyscreenshot
import tempfile
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class FlutterInspector:
    def __init__(self, master):
        self.master = master
        master.title("Flutter Element Inspector")
        master.geometry("1200x800")

        self.dump_filename = "ui_dump.xml"
        self.screenshot_filename = "screen.png"
        self.elements = []
        self.create_widgets()

    def create_widgets(self):
        control_frame = ttk.Frame(self.master)
        control_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(control_frame, text="Select Package:").pack(side=tk.LEFT)
        self.package_combobox = ttk.Combobox(control_frame, width=30)
        self.package_combobox.pack(side=tk.LEFT, padx=(0, 10))

        self.load_button = ttk.Button(control_frame, text="Load Packages", command=self.load_packages)
        self.load_button.pack(side=tk.LEFT)

        self.inspect_button = ttk.Button(control_frame, text="Inspect", command=self.inspect_elements)
        self.inspect_button.pack(side=tk.LEFT, padx=(10, 0))

        # Frame untuk gambar dan teks
        content_frame = ttk.Frame(self.master)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Canvas untuk menampilkan screenshot
        self.canvas = tk.Canvas(content_frame, width=400, height=600)
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Area teks untuk menampilkan informasi elemen
        self.result_text = tk.Text(content_frame, wrap=tk.WORD, width=50)
        self.result_text.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def load_packages(self):
        try:
            # Dapatkan semua package
            result_packages = subprocess.run(
                ['adb', 'shell', 'dumpsys', 'package', '|', 'grep', 'Package', '|', 'cut', '-d', '[', '-f2', '|', 'cut', '-d', ']', '-f1'],
                capture_output=True, text=True, check=True, shell=True
            )
            all_packages = set(line.strip() for line in result_packages.stdout.splitlines() if line.strip())

            # Dapatkan aplikasi yang sedang berjalan
            result_running = subprocess.run(
                ['adb', 'shell', 'ps', '|', 'grep', 'u0_'],
                capture_output=True, text=True, check=True, shell=True
            )
            running_processes = set(line.split()[-1] for line in result_running.stdout.splitlines())

            # Filter package yang sedang berjalan dan bukan sistem
            running_packages = [
                pkg for pkg in all_packages.intersection(running_processes)
                if not pkg.startswith('android.') and
                not pkg.startswith('com.android.') and
                not pkg.startswith('com.google.android.')
            ]

            self.package_combobox['values'] = sorted(running_packages)
            if running_packages:
                self.package_combobox.set(running_packages[0])

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Loaded {len(running_packages)} running non-system packages.\n")

        except subprocess.CalledProcessError as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error loading packages: {e}\n")
            self.result_text.insert(tk.END, f"Output: {e.output}\n")
            self.result_text.insert(tk.END, f"Stderr: {e.stderr}\n")
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Unexpected error: {str(e)}\n")

    def inspect_elements(self):
        package_name = self.package_combobox.get()
        if not package_name:
            self.result_text.insert(tk.END, "Please select a package.\n")
            return

        try:
            # Ambil screenshot
            subprocess.run(['adb', 'shell', f'screencap -p /sdcard/{self.screenshot_filename}'], check=True)
            subprocess.run(['adb', 'pull', f'/sdcard/{self.screenshot_filename}', self.screenshot_filename], check=True)

            # Dapatkan hierarki UI
            subprocess.run(['adb', 'shell', f'uiautomator dump /sdcard/{self.dump_filename}'], check=True)
            subprocess.run(['adb', 'pull', f'/sdcard/{self.dump_filename}', self.dump_filename], check=True)

            # Parse XML dan tampilkan screenshot
            self.parse_xml_and_display_screenshot()

        except subprocess.CalledProcessError as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error: {e}\n")

    def parse_xml_and_display_screenshot(self):
        tree = ET.parse(self.dump_filename)
        root = tree.getroot()
        self.elements = []
        self.parse_element(root)

        # Tampilkan screenshot
        image = Image.open(self.screenshot_filename)
        image = image.resize((400, 600), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def parse_element(self, element):
        bounds = element.attrib.get('bounds')
        if bounds:
            coords = [int(x) for x in bounds.replace('][', ',').strip('[]').split(',')]
            self.elements.append((element, coords))
        for child in element:
            self.parse_element(child)

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        for element, (left, top, right, bottom) in self.elements:
            if left <= x*3 <= right and top <= y*3 <= bottom:
                self.highlight_element(element, (left, top, right, bottom))
                self.display_element_info(element)
                break

    def highlight_element(self, element, coords):
        image = Image.open(self.screenshot_filename)
        draw = ImageDraw.Draw(image)
        draw.rectangle(coords, outline="red", width=2)
        image = image.resize((400, 600), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

    def display_element_info(self, element):
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Element: {element.tag}\n\n")
        for attr, value in element.attrib.items():
            self.result_text.insert(tk.END, f"{attr}: {value}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = FlutterInspector(root)
    root.mainloop()