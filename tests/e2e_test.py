
import requests
import sqlite3
import pandas as pd
import time
import os

API_URL = "http://127.0.0.1:5001/api/v1"
DB_PATH = "temp/results.db"

def test_backtest_persistence():
    print("--- E2E TEST: Backtest Persistence ---")
    
    # 1. Trigger Backtest
    ticker = "AAPL"
    print(f"[STEP 1] Triggering Backtest for {ticker}...")
    try:
        start_time = time.time()
        resp = requests.get(f"{API_URL}/backtest/run?ticker={ticker}&strategy=momentum")
        print(f"API Response Time: {time.time() - start_time:.2f}s")
        
        if resp.status_code != 200:
            print(f"[FAIL] API returned {resp.status_code}: {resp.text}")
            return False
            
        data = resp.json()
        print(f"[SUCCESS] Backtest completed. Sharpe: {data['metrics']['Sharpe_Ratio']:.2f}")
    except Exception as e:
        print(f"[FAIL] API Request Error: {e}")
        return False

    # 2. Verify Database
    print(f"[STEP 2] Verifying Database Record in {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print(f"[FAIL] Database file not found at {DB_PATH}")
        return False
        
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql("SELECT * FROM backtest_runs ORDER BY timestamp DESC LIMIT 1", conn)
        conn.close()
        
        if df.empty:
            print("[FAIL] Database is empty. Persistence failed.")
            return False
            
        row = df.iloc[0]
        print(f"Latest Record: ID={row['id']}, Ticker={row['ticker']}, Strategy={row['strategy']}, Returns={row['total_return']:.2f}")
        
        if row['ticker'] == ticker and 'Momentum' in row['strategy']:
            print("[PASS] E2E Test Passed! Record matches.")
            return True
        else:
            print(f"[FAIL] Record mismatch. Expected {ticker}, got {row['ticker']}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Database Error: {e}")
        return False

if __name__ == "__main__":
    success = test_backtest_persistence()
    exit(0 if success else 1)
