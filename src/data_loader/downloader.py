try:
    from src.data_loader.cache_manager import CacheManager
    from src.data_loader.validator import DataValidator
except ImportError:
    # Fallback or local
    from cache_manager import CacheManager
    from validator import DataValidator

import pandas as pd
import logging
import time

try:
    import yfinance as yf
except (ImportError, TypeError):
    # Fallback for py3.9 type union error or missing lib
    yf = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Managers
cache_mgr = CacheManager()
validator = DataValidator()

def fetch_data(ticker: str, start_date: str, interval: str = "1d", force_refresh: bool = False, max_retries: int = 3) -> pd.DataFrame:
    """
    Fetch historical data from Cache or yfinance.
    Now includes:
    1. Retry Logic
    2. Data Governance (Validation & Cleaning)
    """
    # 1. Try Cache
    if not force_refresh:
        df_cache = cache_mgr.load_data(ticker, start_date=start_date)
        if not df_cache.empty:
            logger.info(f"Cache Hit for {ticker} (Rows: {len(df_cache)})")
            # Governance Check on Cache? 
            # Ideally cache is already clean, but let's be safe if it was old data.
            # Only validate, don't re-clean heavy if it looks okay.
            return df_cache
    else:
        logger.info(f"Force Refresh: Bypassing cache for {ticker}...")
    
    # 2. Download from yfinance (with Retry)
    logger.info(f"Fetching data for {ticker} from {start_date}...")
    
    df_download = pd.DataFrame()
    
    for attempt in range(max_retries):
        try:
            data = yf.download(ticker, start=start_date, interval=interval, progress=False)
            
            if not data.empty:
                df_download = data
                break # Success
            else:
                 logger.warning(f"Attempt {attempt+1}/{max_retries}: Empty data returned for {ticker}")
                 
        except Exception as e:
            logger.warning(f"Attempt {attempt+1}/{max_retries}: Download failed for {ticker}: {e}")
            
        time.sleep(2 * (attempt + 1)) # Backoff 2s, 4s, 6s...

    if df_download.empty:
        logger.error(f"Failed to fetch data for {ticker} after {max_retries} attempts.")
        return pd.DataFrame()
    
    # Flatten MultiIndex if needed
    if isinstance(df_download.columns, pd.MultiIndex):
        df_download.columns = df_download.columns.get_level_values(0)
        
    # 3. Data Governance: Clean & Validate
    logger.info(f"Applying Data Governance Rules for {ticker}...")
    df_clean = validator.clean_and_validate(df_download, ticker)
    
    if df_clean is None:
        logger.error(f"Data Governance Failed for {ticker}. Data rejected.")
        return pd.DataFrame() # Rejected
        
    # 4. Save to Cache (Parquet)
    cache_mgr.save_data(ticker, df_clean)
        
    return df_clean

def fetch_financials(ticker: str) -> pd.DataFrame:
    """
    Fetch and cache financials for a ticker.
    Returns:
        pd.DataFrame (OHLCV)
    """
    if yf is None:
        logger.warning("yfinance not available. returning empty DF.")
        return pd.DataFrame()

    logger.info(f"Fetching Financials for {ticker}...")
    try:
        t = yf.Ticker(ticker)
        
        # 1. Income Statement
        inc = t.financials
        
        # 2. Balance Sheet
        bal = t.balance_sheet
        
        # 3. Cash Flow
        cf = t.cashflow
        
        # Combine all (Concatenate along index, shared columns are dates)
        frames = []
        if not inc.empty: frames.append(inc)
        if not bal.empty: frames.append(bal)
        if not cf.empty: frames.append(cf)
        
        if frames:
            combined = pd.concat(frames)
            # Remove duplicates just in case
            combined = combined.loc[~combined.index.duplicated(keep='first')]
            cache_mgr.save_financials(ticker, combined)
            return True
            
        return False
    except Exception as e:
        logger.error(f"Error fetching financials for {ticker}: {e}")
        return False

# Deprecated simple validate, use validator class
def validate_data(df: pd.DataFrame) -> bool:
    """Wrapper for backward compatibility calling new Validator"""
    if df.empty: return False
    is_valid, _ = validator.validate(df, "BackwardCompatCheck")
    return is_valid

if __name__ == "__main__":
    print("--- SELF-TEST START: downloader.py (v2) ---")
    
    # Test 1: Fetch BTC-USD
    ticker = "BTC-USD"
    start = "2024-01-01"
    
    print(f"Fetching {ticker}...")
    df = fetch_data(ticker, start, force_refresh=True)
    
    print(f"[TEST] Result Rows: {len(df)}")
    if not df.empty:
        print(f"[TEST] Parquet File Check: data/processed/{ticker.replace('-','_')}.parquet")
        import os
        expected_path = f"data/processed/{ticker.replace('-','_')}.parquet"
        print(f"[TEST] Exists? {os.path.exists(expected_path)}")
        
    print("--- SELF-TEST END ---")
