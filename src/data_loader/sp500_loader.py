
import pandas as pd
import time
import sys
import os
import logging

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.data_loader.downloader import fetch_data, fetch_financials

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_sp500_tickers():
    """
    Get S&P 500 tickers. 
    Ideally scrapes Wikipedia. For stability, we default to a top list or scrape.
    """
    try:
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        tickers = df['Symbol'].tolist()
        return [t.replace('.', '-') for t in tickers] # Fix BRK.B -> BRK-B
    except Exception as e:
        logger.warning(f"Failed to scrape S&P500: {e}. Using Default Top 50.")
        return [
            "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "V", "JNJ",
            "WMT", "JPM", "PG", "MA", "UNH", "HD", "CVX", "MRK", "ABBV", "KO", "PEP",
            "BAC", "AVGO", "COST", "PFE", "TMO", "CSCO", "ACN", "ABT", "DHR", "NFLX",
            "LIN", "MCD", "DIS", "TXN", "NEE", "ADBE", "PM", "AMD", "VZ", "CRM", "NKE"
        ]

def run_bulk_load(start_year=2008, end_year=2026):
    """
    Download Price and Financials for all tickers from start_year to end_year.
    """
    tickers = get_sp500_tickers()
    logger.info(f"Found {len(tickers)} tickers. Starting Bulk Load (2008-2026)...")
    
    start_date = f"{start_year}-01-01"
    
    for i, ticker in enumerate(tickers):
        logger.info(f"[{i+1}/{len(tickers)}] Processing {ticker}...")
        
        # 1. Fetch Prices
        # We assume 1d interval
        df = fetch_data(ticker, start_date=start_date, force_refresh=True)
        if df.empty:
            logger.warning(f"Failed to fetch prices for {ticker}")
        
        # 2. Fetch Financials
        # Note: yfinance free API only gives last 4 years approx.
        # We assume fetch_financials does its best.
        ok = fetch_financials(ticker)
        if not ok:
             logger.warning(f"Failed to fetch financials for {ticker}")
        
        # Rate Limit to be nice
        time.sleep(1.0) 
        
    logger.info("Bulk Load Complete.")

if __name__ == "__main__":
    run_bulk_load()
