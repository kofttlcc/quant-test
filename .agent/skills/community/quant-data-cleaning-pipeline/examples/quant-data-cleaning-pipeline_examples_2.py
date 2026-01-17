from src.data_pipeline.cleaning import detect_outliers_mad, fill_missing_values

def clean_financial_data(df):
    # Step 1: 在收益率上檢測異常（非價格水平）
    returns = df['Close'].pct_change().fillna(0)
    outlier_mask = detect_outliers_mad(returns.values, threshold=3.5)
    
    # Step 2: 標記為 NaN
    df.loc[outlier_mask, ['Open', 'High', 'Low', 'Close']] = np.nan
    
    # Step 3: 布朗橋填補
    df = fill_missing_values(df, method='brownian')
    
    return df
