"""An interface to Barty the bartender robot"""

import time
from typing import Optional

from gpiozero import Motor
from madsci.client.event_client import EventClient


class BartyInterface:
    """An interface to Barty the bartender robot"""

    cancel_flag: bool = False
    pause_flag: bool = False

    pump_max_speed = 1.427  # * ~1.5 mL/s

    def __init__(self, logger: Optional[EventClient] = None, simulate=False) -> "BartyInterface":
        """Initialize the Barty Interface"""
        self.logger = logger if logger else EventClient()
        self.simulate = simulate

        if not self.simulate:
            self.motors = [
                Motor(forward="BOARD15", backward="BOARD13", enable="BOARD11"),
                Motor(forward="BOARD16", backward="BOARD18", enable="BOARD22"),
                Motor(forward="BOARD21", backward="BOARD23", enable="BOARD19"),
                Motor(forward="BOARD24", backward="BOARD26", enable="BOARD32"),
            ]

        self.logger.log("Barty initialized and connection open")

    def forward(self, pump_list: list[int], speed: float, seconds: float):
        """
        Move the pump motors forward at the specified rate for a given amount of time.

        *args, **kwargs:
        - pump_list: a list of pump numbers to move
        - speed: the speed at which to move the pump motors (a float between 0 and 1 representing the duty cycle)
        - seconds: the amount of time to move the pump motors
        """
        if not self.simulate:
            for pump in pump_list:
                self.motors[pump].forward(speed)

        time.sleep(seconds)

        if not self.simulate:
            for pump in pump_list:
                self.motors[pump].stop()

        self.logger.log(f"Moved pumps {pump_list} forward")

    def backward(self, pump_list: list[int], speed: float, seconds: float):
        """
        Move the pump motors backward at the specified rate for a given amount of time.

        *args, **kwargs:
        - pump_list: a list of pump numbers to move
        - speed: the speed at which to move the pump motors (a float between 0 and 1 representing the duty cycle)
        - seconds: the amount of time to move the pump motors
        """
        if not self.simulate:
            for pump in pump_list:
                self.motors[pump].backward(speed)

        time.sleep(seconds)

        if not self.simulate:
            for pump in pump_list:
                self.motors[pump].stop()

        self.logger.log(f"Moved pumps {pump_list} backward")

    def fill(self, pump_list: list[int], amount: float):
        """
        Drive the specified pump's motors forward to fill specific reservoirs.

        *args, **kwargs:
        - pump_list: a list of pump numbers to refill
        - amount: the amount of liquid to refill in milliliters
        """
        duration = amount / self.pump_max_speed
        self.forward(pump_list, 1, duration)

        self.logger.log(f"Refilled {pump_list} by volume {amount}")

    def drain(self, pump_list, amount):
        """
        Drive the specified pump's motors forward to refill specific reservoirs.

        *args, **kwargs:
        - pump_list: a list of pump numbers to refill
        - amount: the amount of liquid to refill in milliliters
        """
        duration = amount / self.pump_max_speed
        self.backward(pump_list, 1, duration)

        self.logger.log(f"Drained {pump_list} by volume {amount}")

    def fill_all(self, amount: float):
        """
        Drive all pump motors forward to fill all the ink reservoirs.

        *args, **kwargs:
        - amount: the amount of liquid to refill in milliliters
        """
        self.fill(range(4), amount)

        self.logger.log(f"Refilled all reservoirs with volume: {amount}")

    def drain_all(self, amount: float):
        """
        Drive all pump motors backward to drain all the ink reservoirs.

        *args, **kwargs:
        - amount: the amount of liquid to refill in milliliters
        """
        self.drain(range(4), amount)

        self.logger.log(f"Drained all reservoirs by volume: {amount}")


if __name__ == "__main__":
    barty = BartyInterface()
