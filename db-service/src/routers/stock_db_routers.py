from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import List
from src.script import db_writer, db_fetch

from botocore.exceptions import ClientError
from src.script import db_writer

router = APIRouter()

class StockRecord(BaseModel):
    symbol: str
    Date: str
    Open: float
    High: float
    Low: float
    Close: float
    Volume: int


class PredictRecord(BaseModel):
    symbol: str
    date: List[str]
    values: List[float]


@router.post("/write-stock")
def write_one_stock(record: StockRecord):
    error_log=[]
    
    try:
        db_writer.write_recent_stock_data(record.symbol, record.dict())
        return {"message": "Stock data inserted"}
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return{"message": "Recent data alredy inserted"}
        else:
            error_log.append({"record": record, "error": str(e)})


@router.post("/write-stock-bulk")
def write_bulk_stock(symbol: str = Query(...), records: list[dict] = Body(...)):
    success_count = 0
    skipped_count = 0
    error_log = []

    for record in records:
        try:
            db_writer.write_historical_stock_data(symbol, [record])
            success_count += 1
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                skipped_count += 1
            else:
                error_log.append({"record": record, "error": str(e)})

    return {
        "status": "success",
        "count": len(records),
        "inserted": success_count,
        "skipped": skipped_count,
        "response": {
            "message": f"{success_count} inserted, {skipped_count} skipped (duplicate)"
        },
        "errors": error_log if error_log else None
    }


@router.post("/write-predict")
def write_prediction(pred: PredictRecord):
    try:
        db_writer.write_predicted_data(pred.symbol, {"date": pred.date, "values": pred.values})
        return {"message": "Prediction inserted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fetch-historical")
def fetch_historical(ticker: str, start_date: str, end_date: str):
    return db_fetch.fetch_historical(ticker, start_date, end_date)


@router.get("/fetch-recent")
def fetch_recent(ticker: str):
    return db_fetch.fetch_recent(ticker)


@router.get("/fetch-predict")
def fetch_prediction(ticker: str, length: int):
    return db_fetch.fetch_predict(ticker, length)