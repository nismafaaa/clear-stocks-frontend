import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logging.basicConfig(level=logging.INFO)
scheduler = BlockingScheduler()

def run_daily_scrape():
    url = "http://data-service:8001/scrape/recent-write?ticker=AAPL&uploadcsv=true"
    try:
        logging.info("Running scheduled scrape...")
        res = requests.get(url)
        logging.info(f"Status: {res.status_code}, Response: {res.json()}")
    except Exception as e:
        logging.error(f"Failed to run scheduled task: {e}")

# every weekday 20:15 UTC (03:15 WIB) market close in NYC (16.00)
trigger = CronTrigger(hour=20, minute=15, day_of_week='mon-fri')
scheduler.add_job(run_daily_scrape, trigger)

if __name__ == "__main__":
    logging.info("Scheduler started...")
    scheduler.start()
