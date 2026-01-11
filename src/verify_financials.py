
import sys
import os
import pandas as pd
import logging
import yfinance as yf

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.data_loader.providers.yfinance_provider import YFinanceProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_financials():
    print("=== Verifying Financials Fetch ===")
    
    provider = YFinanceProvider()
    tickers = ["AAPL", "MSFT"]
    
    for t in tickers:
        print(f"\nFetching Balance Sheet for {t}...")
        try:
            # Direct debugging of yfinance Ticker
            ticker_obj = yf.Ticker(t)
            # print(f"DEBUG: Ticker info keys: {ticker_obj.info.keys() if ticker_obj.info else 'None'}")
            
            df = provider.fetch_financials(t)
            
            if df is not None:
                print(f"✅ {t} Balance Sheet Shape: {df.shape}")
                print(df.head())
            else:
                print(f"❌ {t} Balance Sheet returned None/Empty")
                
        except Exception as e:
            print(f"❌ {t} Exception: {e}")

if __name__ == "__main__":
    verify_financials()
