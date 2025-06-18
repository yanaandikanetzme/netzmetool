#lokasi app/tabs/tools_subtabs/android_subtabs/element_tab.py
import tkinter as tk
from tkinter import ttk
import subprocess
import re
from PIL import Image, ImageTk, ImageDraw
import io
from app.custom.custom_treeview import CustomTreeview

class AndroidElementExplorer(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.elements = []
        self.scale_factor = 1
        self.screenshot = None
        self.create_widgets()

    def create_widgets(self):
        input_frame = ttk.Frame(self)
        input_frame.pack(padx=10, pady=10, fill="x")

        ttk.Button(input_frame, text="Get UI Elements", command=self.get_ui_elements).pack(side="left")

        result_frame = ttk.Frame(self)
        result_frame.pack(padx=10, pady=(0, 10), expand=True, fill="both")

        self.tree = CustomTreeview(result_frame, columns=('Class', 'Text', 'Resource ID'), show='headings')
        self.tree.heading('Class', text='Class')
        self.tree.heading('Text', text='Text')
        self.tree.heading('Resource ID', text='Resource ID')
        self.tree.pack(side="left", expand=True, fill="both")
        self.tree.bind('<<TreeviewSelect>>', self.on_treeview_select)

        self.screenshot_canvas = tk.Canvas(result_frame, width=400, height=700)
        self.screenshot_canvas.pack(side="right", padx=(10, 0))

    def get_ui_elements(self):
        self.tree.selection_remove(self.tree.selection())

        try:
            # Get the top activity using dumpsys window windows
            result = subprocess.run(
                ['adb', 'shell', 'dumpsys', 'window', 'windows'],
                capture_output=True,
                text=True,
                check=True
            )

            current_focus_line = next((line for line in result.stdout.splitlines() if 'mCurrentFocus' in line), None)
            if current_focus_line:
                current_app = re.search(r'Window\{.*\s([^\s]+)\s.*\}', current_focus_line).group(1)
                print(f"Current active app: {current_app}")
            else:
                print("Current active app not found.")
                return

            self.screenshot = self.take_screenshot()
            self.display_screenshot()

            # Dump the UI hierarchy
            subprocess.run(
                ['adb', 'shell', 'uiautomator', 'dump', '/sdcard/window_dump.xml'],
                capture_output=True,
                text=True,
                check=True
            )

            # Pull the dump file to local
            subprocess.run(
                ['adb', 'pull', '/sdcard/window_dump.xml', '.'],
                capture_output=True,
                text=True,
                check=True
            )

            # Read and parse the UI dump
            with open('window_dump.xml', 'r') as file:
                xml_data = file.read()
                self.parse_and_display(xml_data)

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}\n\nMake sure ADB is installed and the device is connected.")

    def take_screenshot(self):
        result = subprocess.run(
            ['adb', 'exec-out', 'screencap', '-p'],
            capture_output=True,
            check=True
        )
        return Image.open(io.BytesIO(result.stdout))

    def parse_and_display(self, xml_data):
        self.tree.delete(*self.tree.get_children())
        self.elements.clear()
        
        pattern = r'<node.*?class="(.*?)".*?text="(.*?)".*?resource-id="(.*?)".*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"'
        matches = re.findall(pattern, xml_data, re.DOTALL)

        for i, match in enumerate(matches, 1):
            class_name, text, resource_id, left, top, right, bottom = match
            left, top, right, bottom = map(int, (left, top, right, bottom))

            element = {
                "id": i,
                "class": class_name,
                "text": text,
                "resource-id": resource_id,
                "bounds": (left, top, right, bottom)
            }
            self.elements.append(element)

            self.tree.insert('', 'end', values=(class_name, text, resource_id))

        self.display_screenshot()

    def display_screenshot(self):
        if self.screenshot:
            canvas_width = self.screenshot_canvas.winfo_width()
            canvas_height = self.screenshot_canvas.winfo_height()
            self.scale_factor = min(canvas_width / self.screenshot.width, canvas_height / self.screenshot.height)
            new_size = (int(self.screenshot.width * self.scale_factor), int(self.screenshot.height * self.scale_factor))
            
            screenshot_resized = self.screenshot.resize(new_size, Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(screenshot_resized)
            self.screenshot_canvas.config(width=new_size[0], height=new_size[1])
            self.screenshot_canvas.create_image(0, 0, anchor="nw", image=self.photo)

    def on_treeview_select(self, event):
        selection = self.tree.selection()
        if selection:
            selected_item = selection[0]
            item_index = self.tree.index(selected_item)
            if 0 <= item_index < len(self.elements):
                selected_element = self.elements[item_index]
                self.highlight_element(selected_element)

    def highlight_element(self, element):
        if self.screenshot:
            screenshot_copy = self.screenshot.copy()
            draw = ImageDraw.Draw(screenshot_copy)
            left, top, right, bottom = element["bounds"]
            draw.rectangle([left, top, right, bottom], outline="red", width=5)

            canvas_width = self.screenshot_canvas.winfo_width()
            canvas_height = self.screenshot_canvas.winfo_height()
            self.scale_factor = min(canvas_width / screenshot_copy.width, canvas_height / screenshot_copy.height)
            new_size = (int(screenshot_copy.width * self.scale_factor), int(screenshot_copy.height * self.scale_factor))
            
            screenshot_resized = screenshot_copy.resize(new_size, Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(screenshot_resized)
            self.screenshot_canvas.delete("all")
            self.screenshot_canvas.create_image(0, 0, anchor="nw", image=self.photo)
