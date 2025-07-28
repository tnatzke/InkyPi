import unittest
from time import sleep

from PIL import Image

from display.monitor_display import MonitorDisplay


class TestMonitorDisplay(unittest.TestCase):
    def test_displaying_images(self):
        display = MonitorDisplay(None)

        images = [r"C:\Users\Tim Natzke\PycharmProjects\InkyPi\docs\images\inky_clock.jpg",
                  r"C:\Users\Tim Natzke\PycharmProjects\InkyPi\docs\images\raspberry_pi_imager.png",
                  r"C:\Users\Tim Natzke\PycharmProjects\InkyPi\docs\images\raspberry_pi_imager_general.png"]

        for file in images:
            img = Image.open(file)
            display.display_image(img)
            sleep(10)

        display.cleanup_display()


if __name__ == '__main__':
    unittest.main()
