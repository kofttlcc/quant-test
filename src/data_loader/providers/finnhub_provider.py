import requests
import pandas as pd
import logging
import datetime
from typing import Optional
from .base import DataProvider

logger = logging.getLogger(__name__)

class FinnhubProvider(DataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"

    def fetch_price(self, ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
        """
        Finnhub Candle API
        https://finnhub.io/docs/api/stock-candles
        Note: Free tier has limits.
        """
        if not self.api_key:
            logger.error("Finnhub API Key missing")
            return None
            
        try:
            # Convert dates to Unix timestamp
            # start/end strings should be YYYY-MM-DD
            t_start = int(datetime.datetime.strptime(start, "%Y-%m-%d").timestamp())
            t_end = int(datetime.datetime.strptime(end, "%Y-%m-%d").timestamp())
            
            # Resolution 'D' for Day
            url = f"{self.base_url}/stock/candle"
            params = {
                'symbol': ticker,
                'resolution': 'D',
                'from': t_start,
                'to': t_end,
                'token': self.api_key
            }
            
            resp = requests.get(url, params=params)
            data = resp.json()
            
            if data.get('s') != 'ok':
                logger.error(f"Finnhub error for {ticker}: {data}")
                return None
                
            # Parse response: c, h, l, o, v, t
            df = pd.DataFrame({
                'Date': pd.to_datetime(data['t'], unit='s'),
                'Open': data['o'],
                'High': data['h'],
                'Low': data['l'],
                'Close': data['c'],
                'Volume': data['v']
            })
            df.set_index('Date', inplace=True)
            return df
            
        except Exception as e:
            logger.error(f"Finnhub fetch failed for {ticker}: {e}")
            return None

    def fetch_financials(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Finnhub Financials As Reported
        Note: This is often a Premium feature or limited in Free tier.
        We will implement a basic version.
        """
        # For free tier, maybe use 'metric' endpoint for basic fundamentals
        return None
