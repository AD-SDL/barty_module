#!/usr/bin/env python3
"""A python module for controlling Barty the bartending robot."""

from typing import Annotated, List

from fastapi.datastructures import State
from wei.modules.rest_module import RESTModule
from wei.types.step_types import StepResponse

import barty_driver

barty_module = RESTModule(
    name="Barty",
    version="1.0.0",
    description="A python module controlling Barty the amazing bartending robot",
    model="Barty v1",
)


@barty_module.action(
    name="drain_ink_all_motors",
    description="Drains specified amount of liquid from all motors",
)
def drain_all(
    state: State, amount: Annotated[int, "Amount of ink to drain, in milliliters"] = 100
):
    """Drains specified amount of liquid from all motors"""
    barty_driver.drain_all(int(amount))

    return StepResponse.step_succeeded()


@barty_module.action(
    name="fill_ink_all_motors",
    description="fills the specified amount of ink on all pumps",
)
def fill_all(
    state: State, amount: Annotated[int, "Amount of ink to fill, in milliliters"] = 60
):
    """Refills the specified amount of liquid from all motors"""
    barty_driver.refill_all(amount)
    return StepResponse.step_succeeded()


@barty_module.action(
    name="refill_ink", description="fills the specified amount of ink on target pumps"
)
def refill_target(
    state: State,
    motors: Annotated[List[int], "motors to run"],
    amount: Annotated[int, "Amount of ink to fill, in milliliters"] = 5,
):
    """Refills the specified amount of ink on target pumps"""
    barty_driver.refill(motors, 5)
    return StepResponse.step_succeeded()


barty_module.start()
