from fastapi import FastAPI
from mqtt_client import start_mqtt

app = FastAPI()

@app.on_event("startup")
def startup():
    start_mqtt()

@app.get("/")
def health():
    return {"status": "사랑"}