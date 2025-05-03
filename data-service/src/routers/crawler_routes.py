import logging
from fastapi import APIRouter
from service.crawler import StockCrawler

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

@router.get("/scraper/historical")
def historical_scrape(ticker:str=None, start_date:str=None, end_date:str=None):
    scraper = StockCrawler()
    results = scraper.perform_crawl_with_date(ticker=ticker, start_date=start_date, end_date=end_date)
    return results