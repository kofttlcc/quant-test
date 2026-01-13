"""
data_pipeline/cleaning.py - 數據治理管道
=========================================
功能:
1. 異常值檢測 (MAD - Median Absolute Deviation)
2. 缺失值插補 (Imputation)
3. 數據質量報告 (Data Quality Report)

Skill: quant-data-cleaning
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataCleaner:
    """
    標準化數據清洗管道
    """
    
    def __init__(self, outlier_threshold: float = 3.5):
        """
        Args:
            outlier_threshold: MAD 閾值 (默認 3.5, Iglewicz and Hoaglin 推薦)
        """
        self.threshold = outlier_threshold
        
    def detect_outliers_mad(self, series: pd.Series) -> pd.Series:
        """
        使用 MAD (中位數絕對偏差) 檢測異常值
        
        MAD = median(|Xi - median(X)|)
        Modified Z-score = 0.6745 * (Xi - median(X)) / MAD
        
        Returns:
            Boolean Series (True = Outlier)
        """
        if series.empty:
            return pd.Series(dtype=bool)
            
        median = series.median()
        mad = np.median(np.abs(series - median))
        
        if mad == 0:
            # 如果 MAD 為 0 (例如大部分數據相同)，退化為 Mean/Std 或忽略
            logger.warning(f"MAD is 0 for {series.name}, skipping outlier detection.")
            return pd.Series(False, index=series.index)
            
        modified_z_score = 0.6745 * (series - median) / mad
        
        return modified_z_score.abs() > self.threshold

    def clean_data(self, df: pd.DataFrame, method: str = 'winsorize') -> Tuple[pd.DataFrame, Dict]:
        """
        執行完整清洗流程
        
        Args:
            df: 原始 DataFrame (Time Series)
            method: 處理異常值的方法 ('drop', 'clip', 'winsorize', 'nan')
            
        Returns:
            (Cleaned DataFrame, Quality Report Dict)
        """
        if df.empty:
            return df, {"error": "Empty Data"}
            
        cleaned_df = df.copy()
        report = {
            "missing_values_imputed": 0,
            "outliers_detected": 0,
            "outliers_handled_method": method
        }
        
        # 1. 處理缺失值 (Missing Values)
        # 策略: Forward Fill (金融時間序列慣例) -> 剩餘的用 0 或 drop
        initial_missing = cleaned_df.isna().sum().sum()
        cleaned_df = cleaned_df.ffill()
        final_missing = cleaned_df.isna().sum().sum()
        report["missing_values_imputed"] = int(initial_missing - final_missing)
        
        # 2. 處理異常值 (Outliers)
        # 僅針對數值列
        numeric_cols = cleaned_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            is_outlier = self.detect_outliers_mad(cleaned_df[col])
            n_outliers = is_outlier.sum()
            
            if n_outliers > 0:
                report["outliers_detected"] += int(n_outliers)
                
                if method == 'nan':
                    cleaned_df.loc[is_outlier, col] = np.nan
                elif method == 'clip':
                    # Clip to threshold boundaries
                     median = cleaned_df[col].median()
                     mad = np.median(np.abs(cleaned_df[col] - median))
                     upper = median + (self.threshold * mad / 0.6745)
                     lower = median - (self.threshold * mad / 0.6745)
                     cleaned_df[col] = cleaned_df[col].clip(lower, upper)
                # 'winsorize' is essentially clipping at percentiles, but MAD clipping is robust
                
        return cleaned_df, report

if __name__ == "__main__":
    # Self-test
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100)
    data = np.random.randn(100)
    # Add outliers
    data[10] = 50 
    data[50] = -50
    # Add nan
    data[20] = np.nan
    
    df = pd.DataFrame({'Close': data}, index=dates)
    
    cleaner = DataCleaner()
    clean_df, report = cleaner.clean_data(df, method='clip')
    
    print("Report:", report)
    print("Original Max:", df['Close'].max())
    print("Cleaned Max:", clean_df['Close'].max())
