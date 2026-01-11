import yfinance as yf
import pandas as pd
import logging
import requests
import time
from typing import Optional, Dict
from .base import DataProvider

logger = logging.getLogger(__name__)

# Configure Global Session for YFinance to avoid 403s
# YFinance uses requests internally. By default it doesn't use a session object we pass easily in all versions,
# but we can try to improve stability by being slow and steady.


class YFinanceProvider(DataProvider):
    def fetch_price(self, ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
        # Single ticker fetch (wrapper around batch for consistency)
        data_map = self.fetch_batch([ticker], start, end)
        return data_map.get(ticker)

    def fetch_batch(self, tickers: list[str], start: str, end: str) -> Dict[str, pd.DataFrame]:
        """
        Batch fetch with strict legacy optimizations:
        - threads=False (Critical for avoiding connection bans)
        - timeout=30
        - auto_adjust=False
        """
        if not tickers:
            return {}
            
        try:
            # Enforce single-threaded download
            # Using threads=False forces yfinance to download sequentially
            # This is slower but much more reliable for large history
            df = yf.download(
                tickers, 
                start=start, 
                end=end, 
                progress=False, 
                auto_adjust=False, 
                threads=False,  # STRICT SINGLE THREADING
                timeout=30,
                group_by='ticker'
            )
            
            if df is None or df.empty:
                logger.warning(f"YFinance returned empty data for batch of {len(tickers)}")
                return {}
                
            # DEBUG LOG
            # logger.info(f"Downloaded DF Columns: {df.columns}")
            # logger.info(f"Downloaded DF Head: {df.head(1)}")

            results = {}
            
            # Case 1: Single Ticker Result (structure is flat)
            if len(tickers) == 1:
                ticker = tickers[0]
                # If group_by='ticker' is used, even single ticker might come as MultiIndex OR Flat depending on version.
                # Let's inspect columns to be sure.
                if isinstance(df.columns, pd.MultiIndex):
                    # Usually (Ticker, Open), (Ticker, Close)...
                    if ticker in df.columns.levels[0]:
                        df = df[ticker] # Extract level
                results[ticker] = self._clean_df(df)
            else:
                # Case 2: Multi Ticker Result (MultiIndex columns)
                # Levels: (Price Type, Ticker) or (Ticker, Price Type)
                # group_by='ticker' usually results in (Ticker, Price Type)
                
                # Check for MultiIndex
                if isinstance(df.columns, pd.MultiIndex):
                    # We expect top level to be Ticker because group_by='ticker'
                    level0 = df.columns.levels[0]
                    
                    for t in tickers:
                        try:
                            if t in level0:
                                sub_df = df[t].copy() # Extract cross-section
                                clean = self._clean_df(sub_df)
                                if clean is not None and not clean.empty:
                                    results[t] = clean
                        except Exception as e:
                            logger.warning(f"Error extracting {t}: {e}")
                else:
                    # Fallback if yfinance didn't group as expected
                    pass
                        
            return results
            
        except Exception as e:
            logger.error(f"Batch download failed: {str(e)}")
            return {}

    def _clean_df(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """Legacy cleaning logic"""
        if df.empty: return None
        
        # Flatten columns if needed (though usually resolved by extraction)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        clean_cols = {}
        for c in df.columns:
            c_str = str(c).lower()
            if 'adj close' in c_str: clean_cols[c] = 'Adj Close'
            elif 'close' in c_str: clean_cols[c] = 'Close'
            elif 'open' in c_str: clean_cols[c] = 'Open'
            elif 'high' in c_str: clean_cols[c] = 'High'
            elif 'low' in c_str: clean_cols[c] = 'Low'
            elif 'volume' in c_str: clean_cols[c] = 'Volume'
            
        df = df.rename(columns=clean_cols)
        
        # Ensure Close exists and Drop NaNs
        if 'Close' not in df.columns:
            return None
            
        df = df.dropna(how='all')
        return df

    def fetch_financials(self, ticker: str) -> Optional[pd.DataFrame]:
        # Add retry logic for financials
        for attempt in range(3):
            try:
                t = yf.Ticker(ticker)
                # Fetch both BS and IS to be comprehensive like legacy
                # For now return BS as requested previously
                bs = t.balance_sheet
                if bs is not None and not bs.empty:
                    return bs
                # If empty, maybe try income statement?
                # But if BS is empty, likely ticker issue or no data.
                return None
            except Exception as e:
                logger.warning(f"YF Financials failed for {ticker} (Attempt {attempt+1}/3): {e}")
                time.sleep(2 * (attempt + 1)) # Backoff
        
        logger.error(f"YF Financials failed for {ticker} after 3 attempts.")
        return None
