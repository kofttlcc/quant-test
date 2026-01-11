
import sys
import os
import pandas as pd
import logging

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.data_loader.sp500_loader import SP500Loader

# Configure logging
logging.basicConfig(level=logging.INFO)

def verify():
    print("=== Starting Validation of Fixes ===")
    test_dir = "data_cache_validation"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
        
    loader = SP500Loader(data_dir=test_dir)
    
    # 1. BTC Verification
    print("\n[Test 1] Verifying BTC-USD Update (2008-2026)...")
    success_btc = loader.update_btc()
    
    btc_path = os.path.join(test_dir, "BTC-USD_price.csv")
    if success_btc and os.path.exists(btc_path):
        df = pd.read_csv(btc_path)
        print(f"   ✅ BTC File Created. Rows: {len(df)}")
        if not df.empty:
            print(f"   📅 Date Range: {df.iloc[0]['Date']} to {df.iloc[-1]['Date']}")
            # Basic check for 2008/2010 start (BTC starts 2014 on Yahoo usually, but we check if request covered range)
            # Actually Yahoo BTC-USD starts around 2014-09-17. 
            # If we get data, it means the request worked.
    else:
        print("   ❌ BTC Update Failed!")

    # 2. S&P 500 Subset Verification
    print("\n[Test 2] Verifying S&P 500 Subset Force Single-Thread Update (AAPL, MSFT)...")
    # Using small subset to save time
    loader.update_price_data(tickers=["AAPL", "MSFT"])
    
    for t in ["AAPL", "MSFT"]:
        path = os.path.join(test_dir, f"{t}_price.csv")
        if os.path.exists(path):
            df = pd.read_csv(path)
            print(f"   ✅ {t} File Created. Rows: {len(df)}")
            if not df.empty:
                 print(f"   📅 Date Range: {df.iloc[0]['Date']} to {df.iloc[-1]['Date']}")
        else:
             print(f"   ❌ {t} File Missing!")

    print("\n=== Validation Complete ===")

if __name__ == "__main__":
    verify()
