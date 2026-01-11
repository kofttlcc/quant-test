from typing import List, Optional
import pandas as pd
from datetime import timedelta
from .data_models import Bar

def dataframe_to_bars(df: pd.DataFrame, symbol: str) -> List[Bar]:
    """
    Convert a Pandas DataFrame (Standard OHLCV) to a list of Bar objects.
    Assumes index is DatetimeIndex.
    """
    bars = []
    if df.empty:
        return bars

    for index, row in df.iterrows():
        try:
            bar = Bar(
                symbol=symbol,
                time=index,
                open=float(row.get('Open', 0)),
                high=float(row.get('High', 0)),
                low=float(row.get('Low', 0)),
                close=float(row.get('Close', 0)),
                volume=float(row.get('Volume', 0)),
                period=timedelta(minutes=1) # Default to 1m, can be inferred
            )
            bars.append(bar)
        except Exception:
            continue
            
    return bars

def bars_to_dataframe(bars: List[Bar]) -> pd.DataFrame:
    """
    Convert a list of Bar objects back to a DataFrame.
    """
    if not bars:
        return pd.DataFrame()
        
    data = []
    for bar in bars:
        data.append({
            'Date': bar.time,
            'Open': bar.open,
            'High': bar.high,
            'Low': bar.low,
            'Close': bar.close,
            'Volume': bar.volume
        })
        
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df
