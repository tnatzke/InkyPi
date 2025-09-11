import logging.config
import tkinter as tk
from PIL import Image, ImageTk
import os
import hashlib
import time
import argparse

logging.config.fileConfig(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'logging.conf'))
logger = logging.getLogger(__name__)

class ImageViewerApp:
    def __init__(self, master, image_path, timeout):
        self.master = master

        logger.info("Hide mouse")
        self.master.config(cursor="none")

        logger.info("Set full screen")
        self.master.attributes('-fullscreen', True)  # Set window to fullscreen
        self.master.bind('<Escape>', lambda e: self.master.destroy())  # Exit on Escape key

        self.timeout = timeout
        self.image_path = image_path
        self.current_hash = self.get_file_hash()

        self.label = tk.Label(master)
        self.label.pack()

        self.label_time = tk.Label(master, font=('calibri', 48, 'bold'),
                              text=self.get_time(),
                                background="#ffffff",
                                   padx=0, pady=0,
                              foreground='black')
        self.label_time.place(x=1620, y=50)


        self.width, self.height = self.master.winfo_screenwidth(), self.master.winfo_screenheight()

        self.load_image()

        self.update_time()
        self.check_for_changes()

    def get_time(self) -> str:
        return time.strftime('%I:%M %p')

    def update_time(self):
        self.label_time.config(text=self.get_time())
        self.label_time.after(10000, self.update_time) # Update every 1000ms (1 second)

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
            self.label.config(image=self.tk_image, text=self.get_time())
        except FileNotFoundError:
            self.label.config(text="Image not found!")
            self.tk_image = None
        except Exception as e:
            self.label.config(text=f"Error loading image: {e}")
            self.tk_image = None

        self.master.attributes('-fullscreen', True)

    def check_for_changes(self):
        new_hash = self.get_file_hash()
        if new_hash != self.current_hash:
            self.current_hash = new_hash
            self.load_image()
        self.master.after(self.timeout, self.check_for_changes)  # Check every 1 second


if __name__ == "__main__":
    # os.environ['DISPLAY'] = ':0.0'

    parser = argparse.ArgumentParser(description='A simple program that displays image file changes.')

    parser.add_argument('-f', '--filename', type=str, required=True,
                        help='Filename of a image to monitor.')  # Optional argument with a value
    parser.add_argument('-t', '--timeout', type=int, required=True,
                        help='How often the file should be checked for changes.')  # Flag (boolean)

    args = parser.parse_args()
    logger.info(f"Start up arguments: {args}")

    root = tk.Tk()
    logger.info("Setup root GUI.")
    app = ImageViewerApp(root, args.filename, args.timeout)

    logger.info("Starting main loop.")
    root.mainloop()
