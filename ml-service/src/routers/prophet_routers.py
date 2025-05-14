import os
import logging
from fastapi import APIRouter
from script.run_prophet import ProphetModel, get_last_date_from_csv
import requests

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
    data_path = f"data/{ticker.lower()}_stock_price.csv"
    if not os.path.exists(data_path):
        logger.error("Data path didn't exists.")
    pm._init(data_path)
    last_date = get_last_date_from_csv(data_path)
    forecast_results, _ = pm.forecast_best(
        {
            'holidays': None,
            'changepoint_prior_scale': 0.1,
            'seasonality_prior_scale': 10,
            'seasonality_mode': 'additive',
            'period': 252
        },
        last_date,
        forecast_length=forecast_length
    )
    return {"ticker":ticker ,"results" : forecast_results}

@router.get("/ml/predict-write")
def predict_and_write(ticker: str, forecast_length: int):
    pm = ProphetModel()
    data_path = f"data/{ticker.lower()}_stock_price.csv"
    if not os.path.exists(data_path):
        logger.error("Data path didn't exist.")
    pm._init(data_path)
    last_date = get_last_date_from_csv(data_path)
    forecast_results, _ = pm.forecast_best(
        {
            'holidays': None,
            'changepoint_prior_scale': 0.1,
            'seasonality_prior_scale': 10,
            'seasonality_mode': 'additive',
            'period': 252
        },
        last_date,
        forecast_length=forecast_length
    )

    payload = {
        "symbol": ticker,
        "date": [d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d) for d in forecast_results["date"]],
        "values": forecast_results["values"]
    }

    try:
        response = requests.post("http://db-service:5001/write-predict", json=payload)
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}