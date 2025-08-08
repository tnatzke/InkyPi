import os
import subprocess
import threading

from gpiozero import MotionSensor
import logging
import time

logger = logging.getLogger(__name__)


class MotionTask:
    # Pin connected to the PIR sensor's OUT pin
    pir_pin: int = 17

    # Delay in seconds before turning off the display after no motion is detected
    no_motion_delay: int = 120

    # Delay in seconds before turning the montion back on
    monitor_on_delay: int = 10

    # Replace 'HDMI-A-1' with the actual output name for your HDMI display.
    # You can find the output name by running 'wlr-randr' in the terminal.
    hdmi_output_name: str = "HDMI-A-1"

    # Set to True if the display is currently on, False otherwise
    display_on = True
    last_motion_time: float = time.time()  # Stores the time when motion was last detected
    monitor_turned_off_time : float
    # Initialize the PIR sensor
    pir: MotionSensor

    def __init__(self):
        # Initialize the PIR sensor
        self.pir = MotionSensor(self.pir_pin, queue_len=40, threshold=.7)
        # Attach event handlers for motion and no motion
        self.pir.when_motion = self.motion_detected_handler
        self.pir.when_no_motion = self.no_motion_detected_handler
        logger.info(f"PIR sensor started on GPIO {self.pir_pin}. Monitoring for motion...")
        logger.info(f"Display will turn off after {self.no_motion_delay} seconds of no motion.")

        self.thread = None
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.running = False
        os.environ["XDG_RUNTIME_DIR"] = "/run/user/1000"

    def turn_off_monitor(self):
        """Turns off the HDMI monitor using wlr-randr."""
        try:
            subprocess.call(f'wlr-randr --output {self.hdmi_output_name} --off', shell=True)
            logger.info(f"Monitor {self.hdmi_output_name} turned off.")
            self.display_on = False
            self.monitor_turned_off_time = time.time()
        except subprocess.CalledProcessError as e:
            logger.info(f"Error turning off monitor: {e}")
        except Exception as e:
            logger.info(f"An unexpected error occurred: {e}")

    def turn_on_monitor_with_delay(self):
        if not self.monitor_turned_off_time or time.time() - self.monitor_turned_off_time > self.monitor_on_delay:
            self.turn_on_monitor()

    def turn_on_monitor(self):
        """Turns on the HDMI monitor using wlr-randr."""
        try:
            subprocess.call(f'wlr-randr --output {self.hdmi_output_name} --on', shell=True)
            logger.info(f"Monitor {self.hdmi_output_name} turned on.")
            self.display_on = True
        except subprocess.CalledProcessError as e:
            logger.info(f"Error turning on monitor: {e}")
        except Exception as e:
            logger.info(f"An unexpected error occurred: {e}")

    def motion_detected_handler(self):
        """Handles motion detection events."""
        logger.info("Motion detected!")
        self.last_motion_time = time.time()

        if not self.display_on:
            self.turn_on_monitor_with_delay()

    def no_motion_detected_handler(self):
        """Handles no motion detection events."""
        logger.info("No motion detected.")

    def start(self):
        """Starts the background thread for turning off the display."""
        if not self.thread or not self.thread.is_alive():
            logger.info("Starting monitor task")
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.running = True
            self.thread.start()

    def stop(self):
        """Stops the task by notifying the background thread to exit."""
        with self.condition:
            self.running = False
            self.condition.notify_all()  # Wake the thread to let it exit
        if self.thread:
            logger.info("Stopping monitor task")
            self.thread.join()

    def run(self):
        try:
            while True:
                with self.condition:
                    if self.display_on and (time.time() - self.last_motion_time > self.no_motion_delay):
                        self.turn_off_monitor()
                    self.condition.wait(timeout=1)  # Check every second
                    if not self.running:
                        break
        except KeyboardInterrupt:
            logger.info("\nExiting script.")
        finally:
            # Ensure the display is turned on before exiting (optional)
            if not self.display_on:
                self.turn_on_monitor()
