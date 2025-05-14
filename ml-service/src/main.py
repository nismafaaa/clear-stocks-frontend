from fastapi import FastAPI
from src.routers import prophet_routers

app = FastAPI()

app.include_router(prophet_routers.router)

@app.get("/", tags=['test'])
def read_root():
    return {"Message": "ML service is running"}