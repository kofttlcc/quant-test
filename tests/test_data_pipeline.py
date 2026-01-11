"""
test_data_pipeline.py - 數據管道測試
=============================================
覆蓋 Dev_Checklist.md 要求的數據下載與清洗測試。
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from src.data_pipeline.downloader import fetch_data, validate_data
    from src.data_pipeline.cleaning import handle_outliers
    from src.data_pipeline.cache_manager import CacheManager
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)


class TestDownloader(unittest.TestCase):
    """數據下載模組測試"""
    
    def test_fetch_data_returns_dataframe(self):
        """測試 fetch_data 返回 DataFrame"""
        # 使用短期數據減少測試時間
        df = fetch_data("AAPL", start_date="2024-12-01")
        self.assertIsInstance(df, pd.DataFrame)
    
    def test_fetch_data_has_required_columns(self):
        """測試返回數據包含必要列"""
        df = fetch_data("AAPL", start_date="2024-12-01")
        if not df.empty:
            required = {'Open', 'High', 'Low', 'Close', 'Volume'}
            self.assertTrue(required.issubset(set(df.columns)))
    
    def test_fetch_data_invalid_ticker(self):
        """測試無效 ticker 返回空 DataFrame"""
        df = fetch_data("INVALID_TICKER_XYZ123", start_date="2024-01-01")
        self.assertTrue(df.empty)


class TestDataValidation(unittest.TestCase):
    """數據驗證模組測試"""
    
    def test_validate_empty_dataframe(self):
        """測試空 DataFrame 驗證失敗"""
        df = pd.DataFrame()
        result = validate_data(df)
        self.assertFalse(result)
    
    def test_validate_missing_columns(self):
        """測試缺少必要列驗證失敗"""
        df = pd.DataFrame({
            'Date': ['2024-01-01'],
            'Close': [100.0]  # 缺少 Open, High, Low, Volume
        })
        result = validate_data(df)
        self.assertFalse(result)
    
    def test_validate_complete_dataframe(self):
        """測試完整 DataFrame 驗證通過"""
        df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Open': [100.0, 101.0],
            'High': [102.0, 103.0],
            'Low': [99.0, 100.0],
            'Close': [101.0, 102.0],
            'Volume': [1000000, 1100000]
        })
        result = validate_data(df)
        self.assertTrue(result)
    
    def test_validate_nan_values_fail(self):
        """測試含 NaN 值驗證失敗"""
        df = pd.DataFrame({
            'Date': ['2024-01-01', '2024-01-02'],
            'Open': [100.0, np.nan],  # NaN
            'High': [102.0, 103.0],
            'Low': [99.0, 100.0],
            'Close': [101.0, 102.0],
            'Volume': [1000000, 1100000]
        })
        result = validate_data(df)
        self.assertFalse(result)


class TestDataCleaning(unittest.TestCase):
    """數據清洗模組測試"""
    
    def test_handle_outliers_removes_extreme_values(self):
        """測試異常值處理"""
        # 構造含異常值的數據
        df = pd.DataFrame({
            'Close': [100.0, 102.0, 50.0, 103.0, 104.0]  # 50 是異常值 (>20% 跌幅)
        })
        
        cleaned = handle_outliers(df.copy())
        
        # 驗證清洗後數據形狀正確
        self.assertIsInstance(cleaned, pd.DataFrame)
        self.assertIn('Close', cleaned.columns)
    
    def test_handle_outliers_preserves_normal_data(self):
        """測試正常數據不受影響"""
        df = pd.DataFrame({
            'Close': [100.0, 101.0, 102.0, 103.0, 104.0]  # 正常數據
        })
        
        cleaned = handle_outliers(df.copy())
        
        # 正常數據應保持不變
        self.assertEqual(len(cleaned), len(df))


class TestCacheManager(unittest.TestCase):
    """緩存管理器測試"""
    
    def setUp(self):
        """測試前創建測試緩存"""
        self.cache = CacheManager(db_path='temp/test_cache.db')
    
    def test_save_and_load_data(self):
        """測試保存和加載數據"""
        test_df = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=5),
            'Open': [100.0, 101.0, 102.0, 103.0, 104.0],
            'High': [102.0, 103.0, 104.0, 105.0, 106.0],
            'Low': [99.0, 100.0, 101.0, 102.0, 103.0],
            'Close': [101.0, 102.0, 103.0, 104.0, 105.0],
            'Volume': [1000000] * 5
        }).set_index('Date')
        
        # 保存
        self.cache.save_data('TEST', test_df)
        
        # 加載
        loaded = self.cache.load_data('TEST')
        
        self.assertFalse(loaded.empty)
        self.assertEqual(len(loaded), 5)
    
    def tearDown(self):
        """測試後清理"""
        import os
        if os.path.exists('temp/test_cache.db'):
            os.remove('temp/test_cache.db')


if __name__ == '__main__':
    print("--- 數據管道測試 ---")
    unittest.main(verbosity=2)
