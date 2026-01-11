
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def handle_outliers(df: pd.DataFrame, threshold_pct: float = 0.20) -> pd.DataFrame:
    """
    Detect and handle outliers in price data.
    
    Logic:
    If the daily return (Close-to-Close) exceeds the threshold_pct (e.g., 20%),
    we consider it an anomaly (flash crash/spike) unless confirmed by Volume.
    For simplicity in Phase 1, we will just mark and interpolate or drop.
    Here we will fill with previous value (Forward Fill) for safety.
    
    Args:
        df (pd.DataFrame): DataFrame with 'Close' column.
        threshold_pct (float): Percentage change threshold (default 0.20 for 20%).
        
    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    if df.empty or 'Close' not in df.columns:
        return df
    
    clean_df = df.copy()
    
    # Calculate pct change
    clean_df['pct_change'] = clean_df['Close'].pct_change()
    
    # Identify outliers
    outliers = clean_df[clean_df['pct_change'].abs() > threshold_pct]
    
    if not outliers.empty:
        logger.warning(f"Found {len(outliers)} outliers exceeding {threshold_pct*100}% change.")
        for idx in outliers.index:
            logger.warning(f"Outlier at index {idx}: Change {outliers.loc[idx, 'pct_change']:.2%}")
            # Simple handling: Replace 'Close', 'High', 'Low', 'Open' with NaN and interpolate
            # This is a naive approach; a better one would be to cap/floor or check sources.
            # Given requirement: "瞬間 > 20% 跌幅視為壞帳" -> Treat as Bad Data
            
            # Setting to NaN first
            clean_df.loc[idx, ['Open', 'High', 'Low', 'Close']] = np.nan
            
        # Interpolate linear
        clean_df[['Open', 'High', 'Low', 'Close']] = clean_df[['Open', 'High', 'Low', 'Close']].interpolate(method='linear')
        logger.info("Outliers interpolated.")
    else:
        logger.info("No outliers found.")
        
    clean_df.drop(columns=['pct_change'], inplace=True)
    return clean_df

if __name__ == "__main__":
    print("--- SELF-TEST START: cleaning.py ---")
    
    # Create Dummy Data with an outlier
    data = {
        'Date': pd.date_range(start='2024-01-01', periods=10),
        'Open': [100]*10,
        'High': [105]*10,
        'Low': [95]*10,
        'Close': [100, 101, 102, 103, 80, 105, 106, 107, 108, 109], # Index 4 (5th item) is 80 (from 103) -> -22% drop
        'Volume': [1000]*10
    }
    df = pd.DataFrame(data)
    
    print("[TEST] Original Data (Subset):")
    print(df.iloc[3:7])
    
    print("\n[TEST] Applying handle_outliers...")
    cleaned = handle_outliers(df, threshold_pct=0.20)
    
    print("[TEST] Cleaned Data (Subset):")
    print(cleaned.iloc[3:7])
    
    # Verify the outlier (80) is gone/changed
    val_at_anomaly = cleaned.iloc[4]['Close']
    if val_at_anomaly != 80:
        print(f"[TEST] SUCCESS: Outlier 80 replaced with {val_at_anomaly}")
    else:
        print("[TEST] FAILURE: Outlier not handled.")
        
    print("--- SELF-TEST END ---")
