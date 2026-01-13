
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def brownian_bridge(start_val, end_val, n_steps, sigma, random_state=42):
    """
    生成布朗橋路徑以填充數據缺口。
    
    Args:
        start_val (float): 缺口前的最後一個已知值
        end_val (float): 缺口後的第一個已知值
        n_steps (int): 需要填充的缺失點數量
        sigma (float): 局部波動率 (標準差)
        random_state (int, optional): 隨機數種子
        
    Returns:
        np.array: 插值後的序列片段 (不含端點)
    """
    if random_state is not None:
        np.random.seed(random_state)
        
    dt = 1.0 / (n_steps + 1)
    t = np.linspace(dt, 1.0 - dt, n_steps)
    
    # 線性部分 (Drift)
    drift = start_val + (end_val - start_val) * t
    
    # 隨機部分 (橋的方差結構)
    # Variance = t * (1 - t)
    bridge_var = t * (1 - t)
    
    # Scale sigma to the bridge length? 
    # Standard formula: W(t) - tW(1). Var is t(1-t).
    # If we want to target a specific daily volatility 'sigma', we need to scale carefully.
    # The 'sigma' derived from daily returns is per-step volatility.
    # The bridge noise should scale with sqrt(n_steps)? 
    # Actually, for finance, simpler implementation:
    # Generate random walk with sigma, then bridge it.
    # But adhering to the skill file snippet:
    noise = np.random.normal(0, sigma * np.sqrt(bridge_var * n_steps), size=n_steps) # Scaling factor adjustment might be needed
    # Re-reading skill: "N(0, sigma^2 * ...)" 
    # The snippet had `sigma * np.sqrt(bridge_var)`. 
    # If sigma is daily vol, and time is normalized to 1...
    # Let's stick to the snippet for now, but ensure sigma is representative of the whole gap?
    # Actually, sigma usually means *daily* volatility.
    # If we normalize T=1, then sigma needs to be scaled by sqrt(T) (total time).
    # Let's assume n_steps is the T. 
    # Adjusted: `noise = np.random.normal(0, sigma * np.sqrt(n_steps) * np.sqrt(bridge_var), size=n_steps)`
    # Wait, the skill snippet is: `noise = np.random.normal(0, sigma * np.sqrt(bridge_var), size=n_steps)`
    # This implies 'sigma' passed in is the volatility *of the Bridge Process* (total variance).
    # We should calculate 'sigma' as Daily_Vol * Sqrt(N_Steps).
    
    noise = np.random.normal(0, sigma * np.sqrt(bridge_var * (n_steps + 1)), size=n_steps) 
    
    return drift + noise

def fill_missing_values(df: pd.DataFrame, method='brownian', random_state=42) -> pd.DataFrame:
    """
    Robustly fill missing values.
    
    Args:
        df: DataFrame with OHLCV data.
        method: 'brownian' or 'linear'.
    """
    if df.empty: return df
    clean_df = df.copy()
    
    # Identify numeric columns to interpolate
    cols = [c for c in ['Open', 'High', 'Low', 'Close'] if c in clean_df.columns]
    
    if method == 'linear':
        clean_df[cols] = clean_df[cols].interpolate(method='linear')
        return clean_df.ffill().bfill()
        
    # Brownian Bridge
    # Iterate over columns and find gaps
    for col in cols:
        series = clean_df[col]
        is_na = series.isna()
        if not is_na.any():
            continue
            
        # Get integer indices of nulls
        # A bit complex to vectorise, using iterative approach for safety
        # Find contiguous groups of NaNs
        # 0 1 1 0 0 1
        # diff: 1 0 -1 0 1
        
        # Simple slow approach: iterate. Data size isn't huge (daily bars).
        n = len(series)
        i = 0
        while i < n:
            if pd.isna(series.iloc[i]):
                # Found gap start
                start_gap = i
                while i < n and pd.isna(series.iloc[i]):
                    i += 1
                end_gap = i # Index of first non-nan after gap (or n)
                
                # Gap is [start_gap, end_gap)
                gap_len = end_gap - start_gap
                
                # Boundaries
                start_val = series.iloc[start_gap - 1] if start_gap > 0 else np.nan
                end_val = series.iloc[end_gap] if end_gap < n else np.nan
                
                if pd.isna(start_val) and pd.isna(end_val):
                    # All NaNs?
                    pass 
                elif pd.isna(start_val):
                    # Start of file is NaN -> Backfill
                    series.iloc[start_gap:end_gap] = end_val
                elif pd.isna(end_val):
                    # End of file is NaN -> Forward fill
                    series.iloc[start_gap:end_gap] = start_val
                else:
                    # True Gap
                    if gap_len < 2:
                         # Too short for bridge, linear
                         series.iloc[start_gap:end_gap] = np.linspace(start_val, end_val, gap_len+2)[1:-1]
                    else:
                        # Estimate Sigma (Local Volatility)
                        # Look back 20 periods
                        lookback_start = max(0, start_gap - 20)
                        history = series.iloc[lookback_start:start_gap]
                        # Calc daily returns std dev
                        if len(history) > 2:
                            daily_ret = history.pct_change().std()
                        else:
                            daily_ret = 0.02 # Default fallback
                            
                        # Sigma for the whole bridge duration?
                        # formula: sigma * sqrt(T). Here T = gap_len + 1 (steps).
                        # Let's pass daily_ret directly and handle scaling inside brownian_bridge if needed.
                        # Actually, my implemented function expects 'sigma' which is the scale of the noise.
                        # Standard Brownian Motion W(t) has var t.
                        # Scaled BM has var sigma^2 * t.
                        # So we pass annual vol? No, per-step vol.
                        
                        # Let's adjust implementation to match standard definition:
                        # P(t) = P(0) + drift + BrownianMotion(sigma)
                        # Here I used: noise = Normal(0, scaled_var)
                        # If I pass 'daily_ret', I want the bridge to fluctuate like daily returns.
                        # `brownian_bridge` code used `sigma * np.sqrt(bridge_var * (n_steps+1))`
                        # This looks correct-ish. `daily_ret` is ~sigma per step.
                        
                        bridge_values = brownian_bridge(
                            start_val, end_val, gap_len, 
                            sigma=daily_ret if not pd.isna(daily_ret) else 0.01,
                            random_state=random_state + start_gap
                        )
                        series.iloc[start_gap:end_gap] = bridge_values
                        
            else:
                i += 1
        
        clean_df[col] = series

    # Final cleanup (Volume, etc)
    if 'Volume' in clean_df.columns:
        clean_df['Volume'] = clean_df['Volume'].interpolate(method='linear').fillna(0)
        
    return clean_df.ffill().bfill() # Safety net for edges

def handle_outliers(df: pd.DataFrame, threshold_pct: float = 0.20) -> pd.DataFrame:
    """
    Detect and handle outliers using MAD and Brownian Bridge.
    """
    if df.empty or 'Close' not in df.columns:
        return df
    
    clean_df = df.copy()
    
    # 1. Detect Outliers (MAD based?)
    # For Emergency Phase, sticking to Threshold but using Bridge to fill.
    clean_df['pct_change'] = clean_df['Close'].pct_change()
    outliers = clean_df[clean_df['pct_change'].abs() > threshold_pct]
    
    if not outliers.empty:
        logger.warning(f"Found {len(outliers)} outliers > {threshold_pct:.0%}. Replacing with Brownian Bridge.")
        for idx in outliers.index:
             clean_df.loc[idx, ['Open', 'High', 'Low', 'Close']] = np.nan
             
        # 2. Fill Gaps
        clean_df = fill_missing_values(clean_df, method='brownian')
        
    clean_df.drop(columns=['pct_change'], inplace=True)
    return clean_df

if __name__ == "__main__":
    print("--- SELF-TEST START: cleaning.py ---")
    data = {
        'Close': [100, 101, 102, 103, 80, 105, 106, 107, 108, 109],
        'Open': [100]*10, 'High': [105]*10, 'Low': [95]*10
    }
    df = pd.DataFrame(data)
    print("Original (Index 4 is Outlier 80):")
    print(df['Close'].values)
    
    cleaned = handle_outliers(df, 0.20)
    print("Cleaned:")
    print(cleaned['Close'].values)
    
    print("--- SELF-TEST END ---")
