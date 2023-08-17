#!/usr/bin/env python3

"""The server that takes incoming WEI flow requests from the experiment application"""
import json
import time

from argparse import ArgumentParser
from contextlib import asynccontextmanager
import ast
import uvicorn

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

import barty_driver
global barty


workcell = None
global barty, state
local_ip = 'kirby.alcf.anl.gov'
local_port = 8000

@asynccontextmanager
async def lifespan(app: FastAPI):
    global barty, state
    try:
           
            state = "IDLE"
    except Exception as err:
            print(err)
            state = "ERROR"
    yield
    pass

app = FastAPI(lifespan=lifespan, )

@app.post("/pumpA")
def run_pathA():
    barty_driver.forward("B", 100, 10)
    return None


@app.get("/state")
def get_state():
    global barty, state
    if state != "BUSY":
       pass
        #barty.get_status()
        #if barty.status_msg == 3:
        #            msg.data = 'State: ERROR'
        #            state = "ERROR"
        #elif barty.status_msg == 0:
         #           state = "IDLE"
    return JSONResponse(content={"State": state})

@app.get("/description")
async def description():
    global barty, state
    return JSONResponse(content={"State": state})

@app.get("/resources")
async def resources():
    global barty, state
    return JSONResponse(content={"State": state})

@app.post("/action")
def do_action(
    action_handle: str,
    action_vars, 
):
    global barty, state
    state = "BUSY"

    if action_handle == "drain_ink_all_motors":  
        try:           
            barty_driver.drain_all(250) # Combined protocol lists A and B plate volume as 195mL.
            response_content = {
                    "action_msg": "StepStatus.Succeeded",
                    "action_response": "True",
                    "action_log": ""
                }
            state = "IDLE"
            print("finished")
            return JSONResponse(content=response_content)
        except Exception as e:
            response_content = {
            "status": "failed",
            "error": str(e),
        }
            print(e)
            state = "IDLE"
            return JSONResponse(content=response_content)
    
    elif action_handle == "fill_ink_all_motors":  
        try:           
            barty_driver.refill_all(100)
            response_content = {
                    "action_msg": "StepStatus.Succeeded",
                    "action_response": "True",
                    "action_log": ""
                }
            print("finished")
            state = "IDLE"
            return JSONResponse(content=response_content)
        except Exception as e:
            response_content = {
            "action_msg": "failed",
            "action_response": str(e),
            "action_log": ""
        }
            state = "IDLE"
            return JSONResponse(content=response_content)

    elif action_handle == "refill_ink":  
        try: 
            barty_driver.refill(action_vars['motors'], 5)
            response_content = {
                    "action_msg": "StepStatus.Succeeded",
                    "action_response": "True",
                    "action_log": "run pumpB for" + actions_vars
                }
            state = "IDLE"
            return JSONResponse(content=response_content)
        except Exception as e:
            response_content = {
            "status": "failed",
            "error": str(e),
        }
            state = "IDLE"
            return JSONResponse(content=response_content)
   

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("barty_rest_node:app", host=local_ip, port=local_port, reload=True, ws_max_size=100000000000000000000000000000000000000)


