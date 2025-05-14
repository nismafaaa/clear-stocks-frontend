from fastapi import FastAPI
from src.routers import stock_db_routers

app = FastAPI()
app.include_router(stock_db_routers.router)