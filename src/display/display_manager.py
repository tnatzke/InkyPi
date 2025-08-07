import fnmatch
import json
import logging

from display.monitor_display import MonitorDisplay
from utils.image_utils import resize_image, change_orientation, apply_image_enhancement
from display.inky_display import InkyDisplay
from display.waveshare_display import WaveshareDisplay

logger = logging.getLogger(__name__)

class DisplayManager:

    """Manages the display and rendering of images."""

    def __init__(self, device_config):

        """
        Initializes the display manager and selects the correct display type 
        based on the configuration.

        Args:
            device_config (object): Configuration object containing display settings.

        Raises:
            ValueError: If an unsupported display type is specified.
        """
        
        self.device_config = device_config
     
        display_type = device_config.get_config("display_type", default="inky")

        if display_type == "inky":
            self.display = InkyDisplay(device_config)
        elif display_type == "monitor":
            self.display = MonitorDisplay(device_config)
        elif fnmatch.fnmatch(display_type, "epd*in*"):  
            # derived from waveshare epd - we assume here that will be consistent
            # otherwise we will have to enshring the manufacturer in the 
            # display_type and then have a display_model parameter.  Will leave
            # that for future use if the need arises.
            #
            # see https://github.com/waveshareteam/e-Paper
            self.display = WaveshareDisplay(device_config)
        else:
            raise ValueError(f"Unsupported display type: {display_type}")

    def display_image(self, image, image_settings=[]):
        
        """
        Delegates image rendering to the appropriate display instance.

        Args:
            image (PIL.Image): The image to be displayed.
            image_settings (list, optional): List of settings to modify image rendering.

        Raises:
            ValueError: If no valid display instance is found.
        """

        if not hasattr(self, "display"):
            raise ValueError("No valid display instance initialized.")
        
        # Save the image
        logger.info(f"Saving image to {self.device_config.current_image_file}")
        image.save(self.device_config.current_image_file)

        # Resize and adjust orientation
        image = change_orientation(image, self.device_config.get_config("orientation"))
        image = resize_image(image, self.device_config.get_resolution(), image_settings)
        if self.device_config.get_config("inverted_image"): image = image.rotate(180)
        image = apply_image_enhancement(image, self.device_config.get_config("image_settings"))

        # Save the modified Image
        logger.info(f"Saving the modified image to {self.device_config.current_transformed_image_file}")
        image.save(self.device_config.current_transformed_image_file)

        # Pass to the concrete instance to render to the device.
        self.display.display_image(image, image_settings)