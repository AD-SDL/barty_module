"""A Node i"""

from typing import Optional

from madsci.client.event_client import EventClient
# from madsci.common.types.action_types import ActionFailed, ActionSucceeded
# from madsci.common.types.node_types import RestNodeConfig
# from madsci.node_module.abstract_node_module import action
# from madsci.node_module.rest_node_module import RestNode

import time
import RPi.GPIO as gpio


class BartyInterface:
    """An interface to Barty the bartender robot"""

    status_code: int = 0    # what does this do?

    def __init__(self, logger: Optional[EventClient] = None) -> "BartyInterface":
        """Initialize the Barty Interface"""
        self.logger = logger if logger else EventClient()

        # Using the pin numbers (inside) instead of GPIO (outside)
        gpio.setmode(gpio.BOARD)  
        gpio.setwarnings(False)

        self.motors = {
            "motor_1": {"e": 11, "f": 15, "r": 13},
            "motor_2": {"e": 22, "f": 16, "r": 18},
            "motor_3": {"e": 19, "f": 21, "r": 23},
            "motor_4": {"e": 32, "f": 24, "r": 26},
        }

        self.logger.log("Barty initialized and connection open")


    def initialize_motors(self, motor):
        """Initialize the motors."""
        gpio.setmode(gpio.BOARD)

        gpio.setup(self.motors[motor]["e"], gpio.OUT)
        gpio.setup(self.motors[motor]["f"], gpio.OUT)
        gpio.setup(self.motors[motor]["r"], gpio.OUT)

        pwm = gpio.PWM(self.motors[motor]["e"], 50)
        pwm.start(0)
        self.motors[motor]["pwm"] = pwm

        gpio.output(self.motors[motor]["e"], True)
        gpio.output(self.motors[motor]["f"], False)
        gpio.output(self.motors[motor]["r"], False)

        self.logger.log(f"Initialized motor: {self.motors[motor]}")

        return   # TODO: Don't need to tell it to return here right? won't it just do it?
    
    
    def forward(self, lis_motors, speed, second):
        """Move the motors forward."""
        for motor in lis_motors:
            self.initialize_motors(motor)
            self.motors[motor]["pwm"].start(0)
            time.sleep(2)
            gpio.output(self.motors[motor]["f"], False)
            gpio.output(self.motors[motor]["r"], True)
            self.motors[motor]["pwm"].ChangeDutyCycle(speed)
        time.sleep(second)

        for motor in lis_motors:
            self.motors[motor]["pwm"].stop()

        gpio.cleanup()

        self.logger.log("Moved motor forward")


    def backward(self, lis_motors, speed, second):
        """Move the motors backward."""
        for motor in lis_motors:
            self.initialize_motors(motor)
            self.motors[motor]["pwm"].start(0)
            time.sleep(2)
            gpio.output(self.motors[motor]["f"], True)
            gpio.output(self.motors[motor]["r"], False)
            self.motors[motor]["pwm"].ChangeDutyCycle(speed)

        time.sleep(second)

        for motor in lis_motors:
            self.motors[motor]["pwm"].stop()

        gpio.cleanup()

        self.logger.log("Moved motor backward")


    def refill(self, lis_motors, vol):
        """Drive the specified motors forward to refill specific ink reservoirs."""
        norm_speed = 1.427  # 1.5 mL/s at DC=100, f=50.
        duration = vol / norm_speed
        self.forward(lis_motors, 100, duration)

        self.logger.log(f"Refilled motors {lis_motors} by volume {vol}")


    def drain(self, lis_motors, vol):
        """Drive the specified motors backward to drain specific ink reservoirs."""
        norm_speed = 1.427  # 1.5 mL/s at DC=100, f=50.
        duration = vol / norm_speed
        self.backward(lis_motors, 100, duration)

        self.logger.log(f"Drained motors {lis_motors} by volume {vol}")


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


    # def run_command(self, command: str, fail: bool = False) -> bool:
    #     """Run a command on the test interface."""
    #     self.logger.log(f"Running command {command}.")
    #     if fail:
    #         self.logger.log(f"Failed to run command {command}.")
    #         return False
    #     return True


    # QUESTIONS: 
        # should each method be returning a True False here?
        # do I need an if main at the end here?


if __name__ == "__main__":
    barty = BartyInterface()
    
    



    










