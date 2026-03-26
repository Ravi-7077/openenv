from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from newfile import TrafficEnv

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

env = TrafficEnv()

@app.get("/state")
def get_state():
    return env.state()