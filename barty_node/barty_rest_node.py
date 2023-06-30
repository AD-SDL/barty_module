import uvicorn
from fastapi import FastAPI
from barty_node import barty_driver 

app = FastAPI()

@app.post("/pumpA")
def run_pathA():
    barty_driver.forward("A", 100, 10)
    return None

# uvicorn barty_rest_node:app