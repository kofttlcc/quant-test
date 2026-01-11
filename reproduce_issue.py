
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.models.strategies import Strategies
from src.models.backtest_engine import BacktestEngine
from src.data_pipeline.data_loader import DataLoader

def test_run():
    print("Fetching data...")
    loader = DataLoader()
    # Simulate the request from page.tsx
    # start_date='2023-01-01', end_date='2023-12-31'
    data_map = loader.fetch_data(['BTC-USD'], start_date='2023-01-01', end_date='2023-12-31')
    
    if 'BTC-USD' not in data_map:
        print("Data fetch failed")
        return

    df = data_map['BTC-USD']
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns}")
    print(f"Indices: {df.index}")
    print(f"Close type: {type(df['Close'])}")
    print(f"Close shape: {df['Close'].shape}")
    
    print("Running Strategy (RSI)...")
    try:
        returns = Strategies.rsi_reversion(
            df,
            period=14,
            lower=30,
            upper=70
        )
        print(f"Returns type: {type(returns)}")
        print(f"Returns shape: {returns.shape}")
        
    except Exception as e:
        print(f"Strategy Error: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Running Backtest Engine...")
    try:
        engine = BacktestEngine(initial_capital=10000)
        result = engine.run(returns)
        print("Backtest metrics:", result.metrics)
    except Exception as e:
        print(f"Backtest Engine Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_run()
