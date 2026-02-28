import logging
import os
import pygame
import tempfile
import atexit

from display.abstract_display import AbstractDisplay

logger = logging.getLogger(__name__)


class MonitorDisplay(AbstractDisplay):
    root = None
    screen_width: int = None
    screen_height: int = None
    size: tuple = None
    label = None
    screen = None

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
        # Force SDL to use the KMSDRM driver for console output
        os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
        pygame.init()

        self.tmp_file = tempfile.NamedTemporaryFile(suffix=".png").name

        # Get screen dimensions and create a fullscreen surface
        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h
        self.size = (self.screen_width, self.screen_height)

        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        atexit.register(self.cleanup_display)

        # store display resolution in device config
        # if not self.device_config.get_config("resolution"):
        #     self.device_config.update_value(
        #         "resolution",
        #         [int(self.screen_width), int(self.screen_height)],
        #         write=True)

    def display_image(self, image, image_settings=[]):
        """
        Displays the provided image on the Monitor display.

        The image has been processed by adjusting orientation and resizing
        before being sent to the display.

        Args:
            image (PIL.Image): The image to be displayed.
            image_settings (list, optional): Additional settings to modify image rendering.

        Raises:
            ValueError: If no image is provided.
        """
        with open(self.tmp_file, mode="w+b") as temp_file:
            # Load and display the image
            image.save(temp_file, format="PNG")

            pygame_image = pygame.image.load(temp_file)
            pygame_image = pygame.transform.scale(image, self.size)  # Scale to fit screen
            self.screen.blit(pygame_image, (0, 0))
            pygame.display.update()


    def cleanup_display(self):
        pygame.quit()
