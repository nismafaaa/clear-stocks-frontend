import logging
from fastapi import FastAPI
from routers import prophet_routers

logging.basicConfig(format="[%(asctime)s]:[%(levelname)s]:%(message)s", level=logging.INFO)

app = FastAPI()

app.include_router(prophet_routers.router)

@app.get("/", tags=['test'])
def read_root():
    return {"Message": "ML service is running"}