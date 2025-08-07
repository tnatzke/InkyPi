import logging
import os
import tkinter as tk
import tempfile
import subprocess
import atexit
import sys
from pathlib import Path

from PIL import Image, ImageTk
from display.abstract_display import AbstractDisplay

logger = logging.getLogger(__name__)


class MonitorDisplay(AbstractDisplay):
    root = None
    screen_width: int = None
    screen_height: int = None
    label = None

    """
    Handles the Inky e-paper display.

    This class initializes and manages interactions with the Inky display,
    ensuring proper image rendering and configuration storage.

    The Inky display driver supports auto configuration.
    """

    def initialize_display(self):
        """
        Initializes the Inky display device.

        Sets the display border and stores the display resolution in the device configuration.

        Raises:
            ValueError: If the resolution cannot be retrieved or stored.
        """

        config_resolution = self.device_config.get_config("resolution")
        if not config_resolution:
            root = tk.Tk()
            root.attributes('-fullscreen', True)
            self.screen_width = root.winfo_screenwidth()
            self.screen_height = root.winfo_screenheight()
            root.destroy()

            # store display resolution in device config
            logger.info(f"Saving resolution for monitor display {self.screen_width} x {self.screen_height}")
            self.device_config.update_value(
                "resolution",
                [int(self.screen_width), int(self.screen_height)],
                write=True)
        else:
            self.screen_width = config_resolution[0]
            self.screen_height = config_resolution[1]

        # Define the path to the subprocess script and its arguments
        subprocess_script = ["python", Path(__file__).parent.joinpath("image_viewer.py").resolve(), "-f",
                             self.device_config.current_transformed_image_file,
                             "-t", "3000"]

        # Start the subprocess
        self.viewer = subprocess.Popen(subprocess_script)
        atexit.register(self.cleanup_display)


    def display_image(self, image, image_settings=[]):
        """
        Displays the provided image on the Inky display.

        The image has been processed by adjusting orientation and resizing 
        before being sent to the display.

        Args:
            image (PIL.Image): The image to be displayed.
            image_settings (list, optional): Additional settings to modify image rendering.

        Raises:
            ValueError: If no image is provided.
        """
        pass

    def terminate_subprocess(self):
        if self.viewer.poll() is None:  # Check if the subprocess is still running
            logger.info(f"Terminating subprocess (PID: {self.viewer.pid})...")
            self.viewer.terminate()
            self.viewer.wait(timeout=5)  # Wait for a short period for graceful termination
            if self.viewer.poll() is None:
                logger.info("Subprocess did not terminate gracefully, killing...")
                self.viewer.kill()
        else:
            logger.info("Subprocess already terminated.")

    def cleanup_display(self):
        self.terminate_subprocess()
