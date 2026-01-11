
import pandas as pd
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheManager:
    """
    Parquet Cache for Financial Data.
    Ver: 2.0 (Parquet Only)
    Path: data/processed/{ticker}.parquet
    """
    def __init__(self, cache_dir='data/processed'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Verify structure
        if not self.cache_dir.exists():
            logger.error(f"Failed to create cache dir: {self.cache_dir}")
        else:
            logger.info(f"CacheManager initialized at {self.cache_dir} (Parquet)")

    def _get_path(self, ticker: str, kind: str = 'ohlcv') -> Path:
        """Get file path for ticker."""
        # Sanitize ticker
        safe_ticker = ticker.replace('^', '').replace('-', '_')
        return self.cache_dir / f"{safe_ticker}.parquet"

    def save_data(self, ticker: str, df: pd.DataFrame):
        """Save DataFrame to Parquet."""
        try:
            if df.empty:
                logger.warning(f"Attempted to save empty dataframe for {ticker}")
                return

            path = self._get_path(ticker)
            
            # Ensure standard index and cols
            df_save = df.copy()
            
            # If MultiIndex or funky columns, flatten/fix
            if isinstance(df.columns, pd.MultiIndex):
                df_save.columns = df_save.columns.get_level_values(0)
            
            # Ensure Index is Datetime
            if not isinstance(df_save.index, pd.DatetimeIndex):
                if 'Date' in df_save.columns:
                   df_save['Date'] = pd.to_datetime(df_save['Date'])
                   df_save.set_index('Date', inplace=True)
                elif 'date' in df_save.columns:
                   df_save['date'] = pd.to_datetime(df_save['date'])
                   df_save.set_index('date', inplace=True)
            
            # Write parquet (snappy compression is default and good)
            df_save.to_parquet(path)
            logger.info(f"Saved {ticker} to {path} (Rows: {len(df_save)})")
            
        except Exception as e:
            logger.error(f"Parquet Save Error ({ticker}): {e}")

    def load_data(self, ticker: str, start_date=None, end_date=None) -> pd.DataFrame:
        """Load DataFrame from Parquet."""
        path = self._get_path(ticker)
        if not path.exists():
            return pd.DataFrame()
            
        try:
            df = pd.read_parquet(path)
            
            # Filter Dates
            if start_date:
                df = df[df.index >= pd.Timestamp(start_date)]
            if end_date:
                df = df[df.index <= pd.Timestamp(end_date)]
                
            return df
        except Exception as e:
            logger.error(f"Parquet Load Error ({ticker}): {e}")
            return pd.DataFrame()

    def save_financials(self, ticker: str, df: pd.DataFrame):
        """Save Financials to Parquet (suffix _fin)."""
        try:
            path = self._get_path(ticker + "_fin")
            df.to_parquet(path)
            logger.info(f"Saved financials for {ticker} to {path}")
        except Exception as e:
            logger.error(f"Financials Save Error ({ticker}): {e}")

    def load_financials(self, ticker: str) -> pd.DataFrame:
        """Load financials from Parquet."""
        path = self._get_path(ticker + "_fin")
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_parquet(path)
        except Exception as e:
             logger.error(f"Financials Load Error ({ticker}): {e}")
             return pd.DataFrame()
