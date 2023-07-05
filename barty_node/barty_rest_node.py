import uvicorn
from fastapi import FastAPI
import barty_driver

app = FastAPI()

@app.post("/pumpA")
def run_pathA():
    barty_driver.forward("B", 100, 10)
    return None


