import tkinter as tk
from tkinter import Button, Label, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import io
import win32clipboard
import requests
import json
import pyperclip
import pyautogui

OCR_URL = 'Path'

API_KEY = 'API_KEY'

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture Tool")
        self.root.geometry("600x600")
        self.root.configure(bg='#f0f0f0')
        
        self.button_frame = tk.Frame(self.root, bg='#dcdcdc')
        self.button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.capture_button = Button(self.button_frame, text="Capture Full Screen", command=self.capture_and_extract_text, width=20, height=1, bg='lightblue', fg='gray', font=('Arial', 12))
        self.capture_button.pack(pady=5)
        
        self.partial_capture_button = Button(self.button_frame, text="Capture Selected Area", command=self.start_capture, width=20, height=1, bg='lightgreen', fg='gray', font=('Arial', 12))
        self.partial_capture_button.pack(pady=5)
        
        self.extract_text_button = Button(self.button_frame, text="Extract Text for Selected Area", command=self.extract_text, width=25, height=1, bg='lightgray', fg='gray', font=('Arial', 12))
        self.extract_text_button.pack(pady=5)
        
        self.display_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.display_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.text_box = tk.Text(self.display_frame, height=10, width=60, wrap=tk.WORD)
        self.text_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.display_frame, command=self.text_box.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_box.config(yscrollcommand=self.scrollbar.set)
        
        self.copy_text_button = tk.Button(self.root, text="Copy Text to Clipboard", command=self.copy_text, width=25, height=1, bg='lightgray', fg='gray', font=('Arial', 12))
        self.copy_text_button.pack(pady=10)

        self.image_label = Label(self.root, bg='#f0f0f0')
        self.image_label.pack(pady=10)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selected_image = None

    def capture_and_extract_text(self):
        screenshot = pyautogui.screenshot()

        image_byte_arr = io.BytesIO()
        screenshot.save(image_byte_arr, format='PNG')
        image_byte_arr = image_byte_arr.getvalue()

        payload = {
            'isOverlayRequired': False,
            'apikey': API_KEY,
            'language': 'eng'
        }

        files = {'screenshot.png': image_byte_arr}
        response = requests.post(OCR_URL, data=payload, files=files)

        try:
            result = response.json() 
            
            if result['IsErroredOnProcessing']:
                extracted_text = "Error: Could not process image."
            else:
                extracted_text = result['ParsedResults'][0]['ParsedText']
        except json.JSONDecodeError:
            extracted_text = "Error: Could not parse the response from the server."

        self.text_box.delete(1.0, tk.END)
        self.text_box.insert(tk.END, extracted_text)

    def start_capture(self):
        """Start capturing the screen by selecting an area."""
        self.root.withdraw()
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.attributes("-fullscreen", True)
        self.selection_window.attributes("-alpha", 0.3)
        self.selection_window.configure(bg='gray')
        self.selection_window.bind("<ButtonPress-1>", self.on_button_press)
        self.selection_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.selection_window.bind("<ButtonRelease-1>", self.on_button_release)
        self.selection_window.bind("<Escape>", self.cancel_selection)

    def on_button_press(self, event):
        """Record the starting point of the selection."""
        self.start_x = event.x_root
        self.start_y = event.y_root

    def on_mouse_drag(self, event):
        """Update the selection rectangle while dragging."""
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.selection_window.update_idletasks() 

    def on_button_release(self, event):
        """Finalize the selection and capture the selected area."""
        self.end_x = event.x_root
        self.end_y = event.y_root

        x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
        x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)

        screen_image = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        self.selected_image = screen_image
        self.display_image(screen_image)

        self.selection_window.destroy()
        self.root.deiconify()

    def cancel_selection(self, event):
        """Cancel the selection and close the overlay window."""
        self.selection_window.destroy()
        self.root.deiconify()

    def extract_text(self):
        """Extract text from the captured image using OCR."""
        if self.selected_image:
            image_byte_arr = io.BytesIO()
            self.selected_image.save(image_byte_arr, format='PNG')
            image_byte_arr = image_byte_arr.getvalue()

            payload = {
                'isOverlayRequired': False,
                'apikey': API_KEY,
                'language': 'eng'
            }

            files = {'screenshot.png': image_byte_arr}
            response = requests.post(OCR_URL, data=payload, files=files)

            try:
                result = response.json()
                if result['IsErroredOnProcessing']:
                    extracted_text = "Error: Could not process image."
                else:
                    extracted_text = result['ParsedResults'][0]['ParsedText']
            except json.JSONDecodeError:
                extracted_text = "Error: Could not parse the response from the server."

            self.text_box.delete(1.0, tk.END)
            self.text_box.insert(tk.END, extracted_text)
        else:
            messagebox.showwarning("No Image", "No image to extract text from.")

    def copy_text(self):
        """Copy the extracted text to the clipboard."""
        text = self.text_box.get(1.0, tk.END).strip()
        pyperclip.copy(text)

    def display_image(self, image):
        """Display the captured image in the UI."""
        global img
        img = ImageTk.PhotoImage(image)

        self.image_label.config(image=img)
        self.image_label.image = img

root = tk.Tk()
app = ScreenCaptureApp(root)

root.mainloop()
