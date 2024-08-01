#!/usr/bin/env python3
"""The server that takes incoming WEI flow requests from the experiment application."""

from contextlib import asynccontextmanager

import barty_driver
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from wei.modules.rest_module import RESTModule
from wei.types.step_types import StepResponse, ActionRequest
from fastapi.datastructures import State
from typing import List, Annotated

global barty


workcell = None
local_ip = "kirby.alcf.anl.gov"
local_port = 8000
rest_module = RESTModule(
        name="pf400_node",
        version="0.0.1",
        description="A node to control the pf400 plate moving robot",
        model="pf400",
    )

@rest_module.action(name="drain_ink_all_motors", description="drains 100ml of ink on all pumps")
def drain_all(state: State, action: ActionRequest,):        
        barty_driver.drain_all(
            100
        )  # Combined protocol lists A and B plate volume as 195mL.
        
        return StepResponse.step_succeeded()
@rest_module.action(name="fill_ink_all_motors", description="fills 60ml of ink on all pumps")
def fill_all(state: State, action: ActionRequest,):               
            barty_driver.refill_all(60)
            return StepResponse.step_succeeded()

@rest_module.action(name="refill_ink", description="fills 5ml of ink on target pumps")
def refill_target( state: State, action: ActionRequest, motors: Annotated[List[int], "motors to run"]): 
            barty_driver.refill(motors, 5)
            return StepResponse.step_succeeded()
       


rest_module.start()
