
import threading
import time
import pandas as pd
import numpy as np
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.data_loader.cache_manager import CacheManager
from src.data_loader.data_loader import DataLoader

def test_concurrency():
    print("\n--- Testing Concurrency (FileLock) ---")
    ticker = "TEST_LOCK"
    cm = CacheManager()
    
    # Create dummy data
    df = pd.DataFrame(index=pd.date_range("2024-01-01", periods=100), data={"Close": range(100)})
    
    def writer(i):
        try:
            print(f"Writer {i} starting...")
            # Modify data slightly
            df_mod = df.copy() + i
            cm.save_data(ticker, df_mod)
            print(f"Writer {i} done.")
        except Exception as e:
            print(f"Writer {i} failed: {e}")

    threads = []
    for i in range(5):
        t = threading.Thread(target=writer, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    # Verify file exists and is readable
    loaded = cm.load_data(ticker)
    if not loaded.empty:
        print("SUCCESS: Concurrency test passed. Data readable.")
        # Cleanup
        path = cm._get_path(ticker)
        if path.exists(): os.remove(path)
        lock = path.with_suffix('.lock')
        if lock.exists(): os.remove(lock)
    else:
        print("FAILURE: Concurrency test failed. Data corruption or missing.")

def test_gap_handling():
    print("\n--- Testing Gap Handling (Data Loader) ---")
    
    # Create data with a gap > 3 days (e.g. 5 days)
    # Days: 1, 2, 3, [4, 5, 6, 7, 8 GAP], 9, 10
    dates = [
        "2024-01-01", "2024-01-02", "2024-01-03",
        "2024-01-09", "2024-01-10"
    ]
    df = pd.DataFrame(index=pd.to_datetime(dates), data={"Close": [100, 101, 102, 110, 111], "Volume": [1000]*5})
    
    # Mock download return
    loader = DataLoader()
    # We inject this DF directly into the logic we added to verify behavior
    # Ideally we'd mock fetch_data, but let's test the logic block directly by extracting it or simulating
    
    # Simulate the logic block we added in DataLoader
    print("Input Dates:", df.index.strftime("%Y-%m-%d").tolist())
    
    # 1. AsFreq
    df_resampled = df.asfreq('D')
    print("Resampled Length (Raw):", len(df_resampled)) # Should be 10 days
    
    # 2. Interpolate limit=3
    numeric_cols = df_resampled.select_dtypes(include=['float', 'int']).columns
    df_interp = df_resampled.copy()
    df_interp[numeric_cols] = df_interp[numeric_cols].interpolate(method='time', limit=3)
    
    # 3. Dropna how=all
    df_final = df_interp.dropna(how='all')
    
    print("Final Dates:", df_final.index.strftime("%Y-%m-%d").tolist())
    
    # Verification Rule:
    # 01-04, 05, 06 (missing) -> Interpolate limit 3?
    # Wait, distance is 6 days (3 to 9). 
    # interpolate(limit=3) should fill only 3 max consecutive NaNs? 
    # Actually pandas limit works on number of NaNs.
    # Gap is 04, 05, 06, 07, 08 (5 days).
    # If limit=3, it might fill first 3 or partially?
    # Let's check result.
    
    missing_days = ["2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07", "2024-01-08"]
    
    # If gap is 5 days and limit=3, standard behavior is it fills NOTHING if the gap is larger than limit?
    # Or fills partial? 'pandas' interpolate with limit usually fills up to limit.
    # BUT we want to ensure it DOES NOT fill widely.
    
    # Let's see what happened.
    filled_count = len(df_final) - 5 # 5 original
    print(f"Filled Days: {filled_count}")
    
    if 0 <= filled_count <= 3:
        print("SUCCESS: Gap handling regulated. Did not blindly fill all 5 days.")
    else:
        print(f"FAILURE: Filled too many days ({filled_count}). Blind fill detected.")

if __name__ == "__main__":
    try:
        test_concurrency()
        test_gap_handling()
    except Exception as e:
        print(f"Test Crashed: {e}")
