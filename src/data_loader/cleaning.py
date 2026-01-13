
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
    for col in cols:
        series = clean_df[col]
        is_na = series.isna()
        if not is_na.any():
            continue
            
        n = len(series)
        i = 0
        while i < n:
            if pd.isna(series.iloc[i]):
                start_gap = i
                while i < n and pd.isna(series.iloc[i]):
                    i += 1
                end_gap = i 
                
                gap_len = end_gap - start_gap
                start_val = series.iloc[start_gap - 1] if start_gap > 0 else np.nan
                end_val = series.iloc[end_gap] if end_gap < n else np.nan
                
                if pd.isna(start_val) and pd.isna(end_val):
                    pass 
                elif pd.isna(start_val):
                    series.iloc[start_gap:end_gap] = end_val
                elif pd.isna(end_val):
                    series.iloc[start_gap:end_gap] = start_val
                else:
                    if gap_len < 2:
                         series.iloc[start_gap:end_gap] = np.linspace(start_val, end_val, gap_len+2)[1:-1]
                    else:
                        lookback_start = max(0, start_gap - 20)
                        history = series.iloc[lookback_start:start_gap]
                        if len(history) > 2:
                            daily_ret = history.pct_change().std()
                        else:
                            # [CRIT-003] Fallback to forward data if history insufficient
                            lookforward = series.iloc[end_gap:min(end_gap+20, len(series))]
                            if len(lookforward) > 2:
                                daily_ret = lookforward.pct_change().std()
                            else:
                                daily_ret = 0.02 
                            
                        bridge_values = brownian_bridge(
                            start_val, end_val, gap_len, 
                            sigma=daily_ret if not pd.isna(daily_ret) else 0.01,
                            random_state=random_state + start_gap
                        )
                        series.iloc[start_gap:end_gap] = bridge_values
            else:
                i += 1
        
        clean_df[col] = series

    if 'Volume' in clean_df.columns:
        clean_df['Volume'] = clean_df['Volume'].interpolate(method='linear').fillna(0)
        
    return clean_df.ffill().bfill()

def detect_outliers_mad(data: np.ndarray, threshold: float = 3.5) -> np.ndarray:
    """
    使用 MAD 方法檢測異常值 (技能: data-gov-outliers)。
    
    Args:
        data: 輸入數組
        threshold: 判定閾值 (默認 3.5)
        
    Returns:
        boolean mask (True=異常)
    """
    median = np.median(data)
    diff = np.abs(data - median)
    mad = np.median(diff)

    if mad == 0:
        return np.zeros(len(data), dtype=bool)

    modified_z_score = 0.6745 * diff / mad
    return modified_z_score > threshold

def handle_outliers(df: pd.DataFrame, method: str = 'imputation') -> pd.DataFrame:
    """
    Detect and handle outliers using MAD (Robust Statistics).
    
    Args:
        df: DataFrame with OHLCV data.
        method: 
            - 'imputation': Treat as missing and fill with Brownian Bridge (Default for Signal Processing)
            - 'winsorize': Clip values to boundary (Default for ML training)
    """
    if df.empty or 'Close' not in df.columns:
        return df
    
    clean_df = df.copy()
    
    # Calculate Returns for outlier detection (Price levels are non-stationary)
    # We detect anomalies in *Returns* (Shocks), then reconstruct or flag prices?
    # Or detect anomalies in Price Spikes directly?
    # Usually Returns are better for MAD.
    
    returns = clean_df['Close'].pct_change().fillna(0)
    
    # Detect outliers in Returns
    outlier_mask = detect_outliers_mad(returns.values, threshold=3.5)
    
    if outlier_mask.any():
        num_outliers = outlier_mask.sum()
        logger.warning(f"Found {num_outliers} outliers using MAD.")
        
        if method == 'imputation':
            # Set price at outlier timestamp to NaN?
            # If Return at t is outlier, it means Price[t] (vs t-1) is anomalous.
            # So we should mark Price[t] as NaN.
            clean_df.loc[outlier_mask, ['Open', 'High', 'Low', 'Close']] = np.nan
            
            # Fill Gaps
            clean_df = fill_missing_values(clean_df, method='brownian')
            
        elif method == 'winsorize':
            # Winsorize Returns implies capping the price move?
            # Simpler: just clip the returns and reconstruct price?
            # Reconstructing price from returns is prone to drift.
            # For this phase, we stick to Imputation as it's safer for Time Series structure preservation.
            logger.info("Winsorization requested but Imputation used for safety in Phase 1.")
            clean_df.loc[outlier_mask, ['Open', 'High', 'Low', 'Close']] = np.nan
            clean_df = fill_missing_values(clean_df, method='brownian')

    return clean_df

if __name__ == "__main__":
    print("--- SELF-TEST START: cleaning.py (MAD) ---")
    
    # Normal Data + 1 Huge Spike
    np.random.seed(42)
    prices = [100.0]
    for _ in range(100):
        ret = np.random.normal(0, 0.01)
        prices.append(prices[-1] * (1 + ret))
        
    # Inject Outlier (10 sigma event)
    prices[50] = prices[49] * 1.5 # +50% jump
    
    df = pd.DataFrame({'Close': prices, 'Open': prices, 'High': prices, 'Low': prices})
    
    print(f"Original Outlier Value: {prices[50]:.2f}")
    
    cleaned = handle_outliers(df, method='imputation')
    
    new_val = cleaned.iloc[50]['Close']
    print(f"Cleaned Value: {new_val:.2f}")
    
    if abs(new_val - prices[50]) > 10:
        print("[TEST] SUCCESS: Outlier removed and interpolated.")
    else:
        print("[TEST] FAILURE: Outlier remains.")
    
    print("--- SELF-TEST END ---")
