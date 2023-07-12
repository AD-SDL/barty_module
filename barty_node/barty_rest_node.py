"""The server that takes incoming WEI flow requests from the experiment application"""
import json
from argparse import ArgumentParser
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

import barty_driver

workcell = None
global barty, state
local_ip = 'barty.alcf.anl.gov'
local_port = 8000



@asynccontextmanager
async def lifespan(app: FastAPI):
    global barty, state
    """Initial run function for the app, parses the worcell argument
        Parameters
        ----------
        app : FastApi
           The REST API app being initialized

        Returns
        -------
        None"""
    try:
            state = "IDLE"
    except Exception as err:
            print(err)
            state = "ERROR"

    # Yield control to the application
    yield

    # Do any cleanup here
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
        barty.get_status()
        if barty.status_msg == 3:
                    msg.data = 'State: ERROR'
                    state = "ERROR"
        elif barty.status_msg == 0:
                    state = "IDLE"
    return JSONResponse(content={"State": state})

@app.get("/description")
async def description():
    global barty, state
    return JSONResponse(content={"State": state })

@app.get("/resources")
async def resources():
    global barty, state
    return JSONResponse(content={"State": state })


@app.post("/action")
def do_action(
    action_handle: str,
    action_vars: str, 
):

    global barty, state
    state = "BUSY"
    if action_handle == 'pumpA':  
        try:           
            #sealer.seal()
            time.sleep(15)  
            response_content = {
                    "action_msg": "StepStatus.Succeeded",
                    "action_response": "True",
                    "action_log": ""
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
    uvicorn.run("barty_REST:app", host=local_ip, port=local_port, reload=True, ws_max_size=100000000000000000000000000000000000000)
