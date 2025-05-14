import re
import requests
import logging
from datetime import datetime, date, timezone
import pandas as pd

from bs4 import BeautifulSoup
from requests import HTTPError, Timeout, RequestException

logger = logging.getLogger(__name__)

class StockCrawler():
        
    def _get_page_content(self, url, verbose=True):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            session = requests.Session()
            response = session.get(url, headers=headers)
            response.raise_for_status()
            if verbose:
                print(f"[INFO] Request to {url} succeeded with status {response.status_code}")
            return response.content
        except Exception as e:
            print(f"[ERROR] Failed to fetch URL {url}: {e}")
            return None
        
    def _get_stock_price(self, page_content:str) -> list[str]:
        """
        Function to scrape recent stock data from yahoo finance with the desired ticker

        params :
            page_content (str) : html page content from historical data yahoo finance site with certain ticker 
                                 (e.g. https://finance.yahoo.com/quote/AAPL/history)
        return :
            stock_price (list) : newest stock price data contain date, high, open, low, close data
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        page_elements = soup.find_all('td', class_='yf-1jecxey')
        raw_data = [element.text for element in page_elements]

        return raw_data
    
    def _remove_non_stock_data(self, input_list: list) -> list:
        cleaned_list = []
        for item in input_list:
            date_match = bool(re.match(r"\w{3} \d{1,2}, \d{4}", item))
            stock_match = bool(re.match(r"^\d{1,3}(,\d{3})*(\.\d{2})?$", item))
            vol_match = bool(re.match(r"^\d{1,3}(,\d{3})+$", item))

            if not (date_match or  stock_match or  vol_match):
                print(f"non stock data found : {item}")
                cleaned_list = cleaned_list[:-1]
                continue

            cleaned_list.append(item)

        return cleaned_list
    
    def _parse_data(self, input_list:list) -> list:
        """
        Function to parse raw results scrape

        params :
            input_list (list[Option]) : raw stock data
        return : 
            parsed_data (list) : structured data
        """
        parsed_data = []
        for i in range(0, len(input_list), 7):
            if i+6 < len(input_list):
                temp_dict = {
                    "Date": input_list[i],
                    "Open": input_list[i+1],
                    "High": input_list[i+2],
                    "Low": input_list[i+3],
                    "Close": input_list[i+4],
                    "Volume": input_list[i+6]
                }
                parsed_data.append(temp_dict)
            else:
                print(f"Skipping incomplete data at index {i}")
        return parsed_data
    
    def _date_format(self, input:str) -> str:
        input = input.lower()
        month_to_number = {
        'jan': '01', 'feb': '02', 'mar': '03',
        'apr': '04', 'may': '05', 'jun': '06',
        'jul': '07', 'aug': '08', 'sep': '09',
        'oct': '10', 'nov': '11', 'dec': '12'
        }
        match = re.match(r"(\w{3}) (\d{1,2}), (\d{4})", input)
        if match:
            month_str, day, year = match.groups()
            if len(day) < 2:
                day = '0' + str(day)
            month_num = month_to_number.get(month_str, '00')
        
        return f"{year}-{month_num}-{day}"
    
    def perform_crawl_with_date(self, ticker:str, start_date:str, end_date:str) -> dict:
        """
        function to perform crawl with date range and certain ticker

        params : 
            ticker (str) : stock symbol
            start_date (str) : start date (format:YYYY-MM-DD/e.g. 2025-05-02)
            end_date (str) : end date (format:YYYY-MM-DD/e.g. 2025-05-02)
        return :
            stock (list[dict]) : scrape results
        """
        date1 = start_date.split("-")
        date2 = end_date.split("-")
        dt1 = datetime(int(date1[0]), int(date1[1]), int(date1[2]), 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(int(date2[0]), int(date2[1]), int(date2[2]), 0, 0, tzinfo=timezone.utc)
        url = f"https://finance.yahoo.com/quote/{ticker}/history/?frequency=1d&period1={int(dt1.timestamp())}&period2={int(dt2.timestamp())}"
        page_content = self._get_page_content(url=url, verbose=True)
        if page_content == None:
            logging.warning("page content is empty, can't fetch stock data.")
            return
        raw_data = self._get_stock_price(page_content=page_content)
        raw_data = self._remove_non_stock_data(raw_data)
        parsed_data = self._parse_data(raw_data)
        df_stock = pd.DataFrame(parsed_data)
        df_stock['Date'] = df_stock['Date'].apply(self._date_format)
        stock = df_stock.to_dict(orient="records")

        return stock
    
    def perform_crawl_recent_data(self, ticker:str) -> dict:
        """
        function to perform crawl newest (1 day) stock price with certain ticker

        params :
            ticker (str) : stock symbol (e.g. AAPL)
        return :
            stock (list[dict]) : scrape results
        """
        date_now = datetime.now()
        dt1 = datetime(date_now.year, date_now.month, (date_now.day), 0, 0, 0, tzinfo=timezone.utc)
        dt2 = datetime(date_now.year, date_now.month, (date_now.day+1), 0, 0, 0, tzinfo=timezone.utc)
        url = f"https://finance.yahoo.com/quote/{ticker}/history/?frequency=1d&period1={int(dt1.timestamp())}&period2={int(dt2.timestamp())}"
        page_content = self._get_page_content(url, verbose=True)
        if page_content == None:
            logging.warning("page content is empty, can't fetch stock data.")
            return
        raw_data = self._get_stock_price(page_content=page_content)
        raw_data = self._remove_non_stock_data(raw_data)
        parsed_data = self._parse_data(raw_data)
        df_stock = pd.DataFrame(parsed_data)
        df_stock['Date'] = df_stock['Date'].apply(self._date_format)
        stock = df_stock.to_dict(orient="records")

        return stock[0]