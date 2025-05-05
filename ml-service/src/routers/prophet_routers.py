import os
import logging
from fastapi import APIRouter
from script.run_prophet import ProphetModel

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/ml")
def info():
    return{
        "message" : "With this prefix you can get predicted stock values in the future",
        "available_methods": "/ml/predict"
    }

@router.get("/ml/predict")
def predict(ticker:str=None, forecast_length:int=None):
    pm = ProphetModel()
    data_path = f"data/{ticker}_stock_price.csv"
    if not os.path.exists(data_path):
        logger.error("Data path or ticker stock didn't exists.")
        return
    pm._init(data_path)
    logger.info("Start forecasting...")
    forecast_results, _ = pm.forecast_best(
        {
            'holidays': None,
            'changepoint_prior_scale': 0.1,
            'seasonality_prior_scale': 10,
            'seasonality_mode': 'additive',
            'period': 252
        },
        '2025-05-02',
        forecast_length=forecast_length
    )
    logger.info("Done forecasting.")
    return {"ticker":ticker ,"results" : forecast_results}