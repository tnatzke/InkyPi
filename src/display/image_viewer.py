import tkinter as tk
from PIL import Image, ImageTk
import os
import hashlib
import time
import argparse

class ImageViewerApp:
    def __init__(self, master, image_path, timeout):
        self.master = master

        self.master.attributes('-fullscreen', True)  # Set window to fullscreen
        self.master.bind('<Escape>', lambda e: self.master.destroy())  # Exit on Escape key

        self.timeout = timeout
        self.image_path = image_path
        self.current_hash = self.get_file_hash()

        self.label = tk.Label(master)
        self.label.pack()

        self.width, self.height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()

        self.load_image()
        self.check_for_changes()

    def get_file_hash(self):
        if not os.path.exists(self.image_path):
            return None
        with open(self.image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def load_image(self):
        try:
            img = Image.open(self.image_path)
            img = img.resize((self.width, self.height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.label.config(image=self.tk_image)
        except FileNotFoundError:
            self.label.config(text="Image not found!")
            self.tk_image = None
        except Exception as e:
            self.label.config(text=f"Error loading image: {e}")
            self.tk_image = None

    def check_for_changes(self):
        new_hash = self.get_file_hash()
        if new_hash != self.current_hash:
            self.current_hash = new_hash
            self.load_image()
        self.master.after(self.timeout, self.check_for_changes) # Check every 1 second

if __name__ == "__main__":
    os.environ['DISPLAY'] = ':0.0'

    parser = argparse.ArgumentParser(description='A simple program that displays image file changes.')

    parser.add_argument('-f', '--filename', type=str, required=True, help='Filename of a image to monitor.') # Optional argument with a value
    parser.add_argument('-t', '--timeout', type=int, required=True, help='How often the file should be checked for changes.') # Flag (boolean)

    args = parser.parse_args()

    root = tk.Tk()
    app = ImageViewerApp(root, args.filename, args.timeout)
    root.mainloop()