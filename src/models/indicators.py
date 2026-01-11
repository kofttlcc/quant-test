
import pandas as pd
import numpy as np
import logging

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    """
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    # MINOR-003 FIX: 不再硬編碼填充 50，保留 NaN 讓調用者決定處理方式
    return rsi

def calculate_bollinger(series: pd.Series, window: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands.
    Returns DataFrame with 'BBM' (Middle), 'BBU' (Upper), 'BBL' (Lower).
    """
    bbm = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    
    bbu = bbm + (std * std_dev)
    bbl = bbm - (std * std_dev)
    
    df = pd.DataFrame({
        'BBM': bbm,
        'BBU': bbu,
        'BBL': bbl
    }, index=series.index)
    
    return df

if __name__ == "__main__":
    print("--- SELF-TEST START: indicators.py ---")
    prices = pd.Series([100, 102, 104, 103, 102, 105, 107, 108, 109, 110, 115, 120, 118, 116, 115, 114])
    
    print("[TEST] RSI (period=5):")
    rsi = calculate_rsi(prices, period=5)
    print(rsi.tail(5))
    
    print("\n[TEST] Bollinger (window=5):")
    bb = calculate_bollinger(prices, window=5)
    print(bb.tail(5))
    
    if not rsi.isnull().all():
        print("[TEST] SUCCESS: Indicators calculated.")
    else:
        print("[TEST] FAILURE: Indicators are all NaN.")
    print("--- SELF-TEST END ---")
