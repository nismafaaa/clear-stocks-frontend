import logging
import requests
from fastapi import APIRouter
from service.crawler import StockCrawler
from service.csv_writer import append_stock_to_csv, append_batch_to_csv

from urllib.parse import urlencode

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/scrape")
def info():
    return{
        "message" : "With this prefix you can get either recent data or full data with certain date range",
        "available_methods": ["/scrape/recent", "/scrape/historical"]
    } 

@router.get("/scrape/recent")
def recent_scrape(ticker:str=None):
    scraper = StockCrawler()
    results = scraper.perform_crawl_recent_data(ticker=ticker)
    return results

@router.get("/scrape/historical")
def historical_scrape(ticker:str=None, start_date:str=None, end_date:str=None):
    scraper = StockCrawler()
    results = scraper.perform_crawl_with_date(ticker=ticker, start_date=start_date, end_date=end_date)
    return results

@router.get("/scrape/recent-write")
def recent_scrape_and_write(ticker: str, uploadcsv:bool=False):
    scraper = StockCrawler()
    result = scraper.perform_crawl_recent_data(ticker=ticker)
    
    if not result:
        return {"status": "error", "message": "Failed to scrape data or stock pirce not available in holiday."}
    
    payload = {
        "symbol": ticker,
        "Date": result["Date"],
        "Open": result["Open"],
        "High": result["High"],
        "Low": result["Low"],
        "Close": result["Close"],
        "Volume": int(result["Volume"].replace(",", ""))
    }
    
    if uploadcsv is True:
        append_stock_to_csv(ticker, payload) #Upload to CSV

    try:
        response = requests.post("http://db-service:5001/write-stock", json=payload) #Upload to DB
        return {"status": "success", "response": response.json()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/scrape/historical-write")
def historical_scrape_and_write(ticker: str, start_date: str, end_date: str, uploadcsv:bool=False):
    scraper = StockCrawler()
    results = scraper.perform_crawl_with_date(ticker, start_date, end_date)

    if not results:
        return {"status": "error", "message": "Failed to scrape data or stock pirce not available in holiday."}
    
    payload = {
        "symbol": ticker,
        "records": results  # list of stock record dicts
    }
        
    if uploadcsv is True:
        append_batch_to_csv(ticker, results) #Upload to CSV
    
    try:
        # add symbol & convert Volume
        for r in results:
            r["symbol"] = ticker
            r["Volume"] = int(r["Volume"].replace(",", ""))  # parsing ke int

        query_string = urlencode({"symbol": ticker})
        url = f"http://db-service:5001/write-stock-bulk?{query_string}"
        response = requests.post(url, json=results)
        return {
            "status": "success",
            "count": len(results),
            "response": response.json()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}