"""An interface to Barty the bartender robot"""

import time
from typing import Optional

from gpiozero import Motor
from madsci.client.event_client import EventClient


class BartyInterface:
    """An interface to Barty the bartender robot"""

    cancel_flag: bool = False
    pause_flag: bool = False

    def __init__(self, logger: Optional[EventClient] = None) -> "BartyInterface":
        """Initialize the Barty Interface"""
        self.logger = logger if logger else EventClient()

        self.motors = {
            "motor_1": Motor(forward="BOARD15", backward="BOARD13", enable="BOARD11"),
            "motor_2": Motor(forward="BOARD16", backward="BOARD18", enable="BOARD22"),
            "motor_3": Motor(forward="BOARD21", backward="BOARD23", enable="BOARD19"),
            "motor_4": Motor(forward="BOARD24", backward="BOARD26", enable="BOARD32"),
        }

        self.logger.log("Barty initialized and connection open")

    def forward(self, motor_list, speed, seconds):
        """Move the motors forward."""
        for motor in motor_list:
            self.motors[motor].forward(speed)
            time.sleep(2)

        time.sleep(seconds - 2)

        for motor in motor_list:
            self.motors[motor].stop()
            time.sleep(2)

        self.logger.log("Moved motor forward")

    def backward(self, motor_list, speed, seconds):
        """Move the motors backward."""
        for motor in motor_list:
            self.motors[motor].backward(speed)
            time.sleep(2)

        time.sleep(seconds - 2)

        for motor in motor_list:
            self.motors[motor].stop()
            time.sleep(2)

        self.logger.log("Moved motor forward")

        self.logger.log("Moved motor backward")

    def refill(self, motor_list, vol):
        """Drive the specified motors forward to refill specific ink reservoirs."""
        norm_speed = 1.427  # * 1.5 mL/s at DC=1, f=50.
        duration = vol / norm_speed
        self.forward(motor_list, 1, duration)

        self.logger.log(f"Refilled motors {motor_list} by volume {vol}")

    def drain(self, motor_list, vol):
        """Drive the specified motors backward to drain specific ink reservoirs."""
        norm_speed = 1.427  # * 1.5 mL/s at DC=100, f=50.
        duration = vol / norm_speed
        self.backward(motor_list, 1, duration)

        self.logger.log(f"Drained motors {motor_list} by volume {vol}")

    def refill_all(self, vol):
        """Drive all motors forward to refill all the ink reservoirs."""
        lis_motors = ["motor_1", "motor_2", "motor_3", "motor_4"]
        self.refill(lis_motors, vol)

        self.logger.log(f"Refilled all reservoirs with volume: {vol}")

    def drain_all(self, vol):
        """Drive all motors backward to drain all the ink reservoirs."""
        lis_motors = ["motor_1", "motor_2", "motor_3", "motor_4"]
        self.drain(lis_motors, vol)

        self.logger.log(f"Drained all reservoirs by volume: {vol}")


if __name__ == "__main__":
    barty = BartyInterface()
