import tkinter as tk
from tkinter import Button, Label, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import io
import win32clipboard
import pyautogui

class ScreenCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Capture Tool")
        self.root.geometry("600x600")
        self.root.configure(bg='#f0f0f0')
        
        self.button_frame = tk.Frame(self.root, bg='#dcdcdc')
        self.button_frame.pack(pady=20, padx=20, fill=tk.X)
        
        self.capture_button = Button(self.button_frame, text="Capture Full Screen", command=self.capture_full_screen, width=20, height=1, bg='lightblue', fg='gray', font=('Arial', 12))
        self.capture_button.pack(pady=5)
        
        self.partial_capture_button = Button(self.button_frame, text="Capture Selected Area", command=self.start_capture, width=20, height=1, bg='lightgreen', fg='gray', font=('Arial', 12))
        self.partial_capture_button.pack(pady=5)
        
        self.save_image_button = Button(self.button_frame, text="Save Image", command=self.save_image, width=25, height=1, bg='lightgray', fg='gray', font=('Arial', 12))
        self.save_image_button.pack(pady=5)
        
        self.copy_image_button = Button(self.button_frame, text="Copy Image to Clipboard", command=self.copy_image, width=25, height=1, bg='lightgray', fg='gray', font=('Arial', 12))
        self.copy_image_button.pack(pady=5)
        
        self.display_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.display_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

        self.image_label = Label(self.root, bg='#f0f0f0')
        self.image_label.pack(pady=10)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.selected_image = None

    def capture_full_screen(self):
        self.root.withdraw()

        self.root.after(200, self._capture_and_display_full_screen)

    def _capture_and_display_full_screen(self):
        screenshot = pyautogui.screenshot()

        self.selected_image = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())

        self.root.deiconify()

        self.display_image(self.selected_image)

        messagebox.showinfo("Capture Complete", "Full screen captured and displayed.")

    def start_capture(self):
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
        self.start_x = event.x_root
        self.start_y = event.y_root

    def on_mouse_drag(self, event):
        self.end_x = event.x_root
        self.end_y = event.y_root
        self.selection_window.update_idletasks()

    def on_button_release(self, event):
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
        self.selection_window.destroy()
        self.root.deiconify()

    def save_image(self):
        if self.selected_image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.selected_image.save(file_path)
                messagebox.showinfo("Save Image", "Image saved successfully!")
        else:
            messagebox.showwarning("No Image", "No image to save.")

    def copy_image(self):
        if self.selected_image:
            output = io.BytesIO()
            self.selected_image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()

            messagebox.showinfo("Copy to Clipboard", "Image copied to clipboard!")
        else:
            messagebox.showwarning("No Image", "No image to copy.")

    def display_image(self, image):
        img = ImageTk.PhotoImage(image)
        self.image_label.configure(image=img)
        self.image_label.image = img

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    root.mainloop()
