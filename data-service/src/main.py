from fastapi import FastAPI
from src.routers import crawler_routers

app = FastAPI()
app.include_router(crawler_routers.router)