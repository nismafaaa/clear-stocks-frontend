import re
import requests
import logging
import pandas as pd

from flask import jsonify
from typing import Dict
from bs4 import BeautifulSoup
from requests import HTTPError, Timeout, RequestException

logging.basicConfig()

class StockCrawler():

    def _get_page_content(self, url, verbose=True):
        """
        Function to get the html element from the given url 
        """
        try:
            headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if verbose :
                print("Requests success.")
            return response.content
        except (HTTPError, Timeout, ConnectionError, RequestException) as e:
            print(e)
            return None
        
    def _get_recent_stock_price(self, page_content:str)->list[str]:
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
    
    def _parse_data(self, input_list:list)->list:
        """
        Function to parse raw results scrape from certain ticker

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
    
    def _date_format(self, input:str)->str:
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
    
    def perform_crawl(self, ticker:str)->Dict:
        """
        Crawler's function wrapper
        """
        url = f"https://finance.yahoo.com/quote/{ticker}/history"
        page_content = self._get_page_content(url=url, verbose=True)
        if page_content == "":
            logging.warning("page content is empty, can't fetch stock data.")
            return
        raw_data = self._get_recent_stock_price(page_content=page_content)
        parsed_data = self._parse_data(raw_data)
        df_stock = pd.DataFrame(parsed_data)
        df_stock['Date'] = df_stock['Date'].apply(self._date_format)

        return df_stock.to_dict(orient="records")


if __name__ == "__main__":
    crawler = StockCrawler()

    stock = crawler.perform_crawl(ticker="MSFT")

    print(stock[0])