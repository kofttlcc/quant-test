"""
validator.py - 數據驗證模塊
===========================
版本: v2.0 (Role-Aligned)
職責: [DataEng]
功能:
1. 檢測數據質量問題 (缺失值、異常值)
2. 驗證價格連續性
3. **數據清洗與治理** (5% 規則)
4. 生成質量報告
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """數據驗證器"""
    
    def __init__(self):
        pass

    def validate(self, df: pd.DataFrame, ticker: str = "Unknown") -> Tuple[bool, Dict]:
        """純驗證 (不修改數據)"""
        report = {
            "ticker": ticker,
            "total_rows": len(df),
            "issues": [],
            "warnings": [],
            "missing_pct": 0.0
        }
        
        if df.empty:
            report["issues"].append("DataFrame 為空")
            return False, report
            
        # 1. 檢查必要列
        required = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [c for c in required if c not in df.columns]
        if missing_cols:
            report["issues"].append(f"缺失必要列: {missing_cols}")
            return False, report
            
        # 2. 檢查缺失值 (NaN)
        nan_counts = df[required].isna().sum()
        total_cells = len(df) * len(required)
        total_nans = nan_counts.sum()
        missing_pct = total_nans / total_cells if total_cells > 0 else 0
        report["missing_pct"] = missing_pct
        
        if total_nans > 0:
            report["warnings"].append(f"發現 NaN 值: {nan_counts.to_dict()}")
            # 嚴重缺失判斷 ( > 5% as per Global Rules)
            if missing_pct > 0.05: 
                report["issues"].append(f"NaN 比例過高 ({missing_pct:.2%}) > 5%")
        
        # 3. 價格異常檢查 (負值或零)
        price_cols = ['Open', 'High', 'Low', 'Close']
        for col in price_cols:
            if (df[col] <= 0).any():
                report["issues"].append(f"{col} 包含 <= 0 的價格")
        
        # 4. OHLC 邏輯檢查
        if (df['High'] < df['Low']).any():
            cnt = (df['High'] < df['Low']).sum()
            report["issues"].append(f"High < Low 異常行數: {cnt}")
            
        is_valid = len(report["issues"]) == 0
        
        if not is_valid:
            logger.warning(f"[{ticker}] 數據驗證失敗: {report['issues']}")
        else:
            logger.info(f"[{ticker}] 數據驗證通過 (Rows: {len(df)})")
            
        return is_valid, report

    def clean_and_validate(self, df: pd.DataFrame, ticker: str = "Unknown") -> Optional[pd.DataFrame]:
        """
        執行數據治理與清洗 (Global Rules Phase 1)
        
        Rules:
        1. 若缺失值 > 5%: 丟棄 (Return None)
        2. 若缺失值 < 5%: 插值 (Interpolate)
        """
        if df.empty:
            return None
            
        # 1. 驗證
        is_valid, report = self.validate(df, ticker)
        
        # 2. 嚴格丟棄規則 > 5%
        if report["missing_pct"] > 0.05:
            logger.error(f"[{ticker}] 數據丟棄: 缺失率 {report['missing_pct']:.2%} > 5% 閾值")
            return None
            
        # 3. 插值規則 < 5%
        df_clean = df.copy()
        if report["missing_pct"] > 0:
            logger.info(f"[{ticker}] 執行插值 (缺失率 {report['missing_pct']:.2%})")
            df_clean = df_clean.interpolate(method='time', limit_direction='both')
            df_clean = df_clean.ffill().bfill() # Ensure no NaNs remain
            
        # 4. 再次檢查是否仍有 NaN (例如全空列)
        if df_clean.isna().sum().sum() > 0:
             logger.error(f"[{ticker}] 插值後仍有殘留 NaN，丟棄數據")
             return None

        # 5. 確保日期索引排序
        df_clean.sort_index(inplace=True)
        
        return df_clean

if __name__ == "__main__":
    # 測試代碼
    dates = pd.date_range("2026-01-01", periods=100)
    df_good = pd.DataFrame({
        "Open": [100]*100, "High": [105]*100, "Low": [95]*100, "Close": [102]*100, "Volume": [1000]*100
    }, index=dates)
    
    # 創建 > 5% 缺失
    df_bad = df_good.copy()
    df_bad.iloc[0:10] = np.nan # 10% Missing
    
    # 創建 < 5% 缺失
    df_fixable = df_good.copy()
    df_fixable.iloc[0:3] = np.nan # 3% Missing
    
    validator = DataValidator()
    
    print("測試正常數據:", validator.clean_and_validate(df_good, "GOOD") is not None)
    print("測試嚴重缺失 (>5%):", validator.clean_and_validate(df_bad, "BAD") is None)
    print("測試輕微缺失 (<5%):", validator.clean_and_validate(df_fixable, "FIXABLE") is not None)
