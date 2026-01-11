
import sys
import os
import pandas as pd
import numpy as np
import logging
import shutil

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase1_Verifier")

def test_data_governance():
    logger.info("=== Starting Phase 1 Verification ===")
    
    # 1. Test Validator Logic
    from src.data_loader.validator import DataValidator
    validator = DataValidator()
    
    # Mock Data
    dates = pd.date_range("2024-01-01", periods=100)
    df_good = pd.DataFrame({
        "Open": [100.0]*100, "High": [105.0]*100, "Low": [95.0]*100, "Close": [102.0]*100, "Volume": [1000.0]*100
    }, index=dates)
    
    # Case A: Good Data
    res = validator.clean_and_validate(df_good.copy(), "GOOD_TEST")
    if res is None:
        logger.error("❌ Validator Failed on Good Data")
        sys.exit(1)
    else:
        logger.info("✅ Validator Passed Good Data")
        
    # Case B: > 5% Missing (Should Drop)
    df_bad = df_good.copy()
    df_bad.iloc[0:10] = np.nan # 10% Missing
    res = validator.clean_and_validate(df_bad, "BAD_TEST")
    if res is not None:
        logger.error("❌ Validator Failed to Drop Bad Data (>5%)")
        sys.exit(1)
    else:
        logger.info("✅ Validator Correctly Dropped Bad Data")
        
    # Case C: < 5% Missing (Should Interpolate)
    df_fix = df_good.copy()
    df_fix.iloc[0:2] = np.nan # 2% Missing
    res = validator.clean_and_validate(df_fix, "FIX_TEST")
    if res is None:
        logger.error("❌ Validator Failed to Fix Data (<5%)")
        sys.exit(1)
    elif res.isna().sum().sum() > 0:
        logger.error("❌ Validator Failed to Interpolate NaNs")
        sys.exit(1)
    else:
        logger.info("✅ Validator Correctly Interpolated Data")

    # 2. Test Downloader & Cache (Parquet)
    from src.data_loader.downloader import fetch_data
    import os
    
    logger.info("--- Testing Downloader & Parquet ---")
    ticker = "BTC-USD"
    # Force refresh to trigger download and save
    df = fetch_data(ticker, start_date="2025-01-01", force_refresh=True)
    
    if df.empty:
        logger.error("❌ Downloader Failed to Fetch BTC-USD")
        sys.exit(1)
        
    expected_path = f"data/processed/{ticker.replace('-','_')}.parquet"
    if not os.path.exists(expected_path):
        logger.error(f"❌ Parquet File Not Found at {expected_path}")
        sys.exit(1)
    else:
        logger.info(f"✅ Parquet File Exists: {expected_path}")
        
    # Test Load from Cache
    try:
        df_loaded = pd.read_parquet(expected_path)
        if len(df_loaded) > 0:
            logger.info(f"✅ Can Read Parquet (Rows: {len(df_loaded)})")
        else:
            logger.error("❌ Parquet File is Empty")
            sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to Read Parquet: {e}")
        sys.exit(1)

    logger.info("🎉 PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    test_data_governance()
