"""
data_loader.py - 統一數據加載器
================================
版本: v1.0
職責: [DataEng]
功能:
1. 封裝 yfinance 接口，統一獲取美股與加密貨幣數據
2. 提供自動重試機制
3. 標準化輸出格式 (OHLCV)
"""

import yfinance as yf
import pandas as pd
import time
from typing import List, Optional, Union, Dict
import logging

# 配置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    """
    統一數據加載器
    
    支持:
    - 單個/多個 Ticker 下載
    - 自動重試
    - 有界緩存 (MEM-001 FIX)
    """
    
    # MEM-001 FIX: 緩存配置
    MAX_CACHE_SIZE = 50  # 最大緩存 Ticker 數量
    CACHE_TTL = 3600  # 緩存過期時間（秒）
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache = {}
        self._cache_timestamps = {}  # MEM-001 FIX: 記錄緩存時間
        
    def _evict_expired_cache(self):
        """MEM-001 FIX: 清理過期和超量緩存"""
        import time
        now = time.time()
        
        # 1. 清理過期條目
        expired = [k for k, ts in self._cache_timestamps.items() 
                   if now - ts > self.CACHE_TTL]
        for k in expired:
            self.cache.pop(k, None)
            self._cache_timestamps.pop(k, None)
            logger.debug(f"Evicted expired cache: {k}")
        
        # 2. 如果仍超過限制，清理最舊的
        while len(self.cache) > self.MAX_CACHE_SIZE:
            oldest = min(self._cache_timestamps, key=self._cache_timestamps.get)
            self.cache.pop(oldest, None)
            self._cache_timestamps.pop(oldest, None)
            logger.debug(f"Evicted oldest cache: {oldest}")
    
    def clear_cache(self):
        """MEM-001 FIX: 手動清理全部緩存"""
        self.cache.clear()
        self._cache_timestamps.clear()
        logger.info("DataLoader cache cleared")

    def fetch_data(
        self, 
        tickers: Union[str, List[str]], 
        start_date: str, 
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """
        獲取歷史數據
        
        Args:
            tickers: 股票代碼 (str 或 list), e.g., "AAPL" or ["AAPL", "BTC-USD"]
            start_date: 開始日期 "YYYY-MM-DD"
            end_date: 結束日期 "YYYY-MM-DD" (默認至今)
            interval: 數據頻率 "1d", "1h", "15m"
            
        Returns:
            Dict[ticker, DataFrame]: 鍵為 ticker，值為標準化 OHLCV DataFrame
        """
        if isinstance(tickers, str):
            tickers = [tickers]
            
        results = {}
        
        # 批量下載效率更高，但 yfinance 返回格式處理較繁瑣
        # 這裡為了穩定性，採用逐個下載 (對於數量不大時) 或 yf.download 批量下載
        # 考慮到穩定性，先使用 yf.download 批量下載
        
        ticker_str = " ".join(tickers)
        logger.info(f"開始下載數據: {ticker_str}, 區間: {start_date} - {end_date or 'Now'}")
        
        for attempt in range(self.max_retries):
            try:
                # auto_adjust=True: 獲取復權數據 (Close 為 Adj Close)
                data = yf.download(
                    tickers, 
                    start=start_date, 
                    end=end_date, 
                    interval=interval,
                    group_by='ticker', 
                    auto_adjust=False, # 避免 yfinance 內部錯誤
                    progress=False
                )

                if data.empty:
                    logger.warning("下載數據為空")
                    return {}
                
                # 遍歷處理每個 ticker 的數據
                for t in tickers:
                    df = pd.DataFrame()
                    if len(tickers) == 1:
                        df = data.copy()
                        # 如果是 MultiIndex (比如 group_by='ticker' 導致的), 嘗試去層
                        if isinstance(df.columns, pd.MultiIndex):
                            try:
                                # 嘗試直接取 level 1 (Price Type)
                                df.columns = df.columns.get_level_values(1)
                            except IndexError:
                                # 如果只有一層，可能是 Ticker
                                df.columns = df.columns.get_level_values(0)
                    else:
                        if t in data.columns.levels[0]:
                            df = data[t].copy()
                        else:
                            logger.warning(f"在下載結果中未找到 {t} 的數據。")
                            continue

                    if df.empty:
                        logger.warning(f"{t} 數據為空")
                        continue

                    # 再次檢查 MultiIndex (防禦性)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = [c[-1] if isinstance(c, tuple) else c for c in df.columns]
                    
                    # 標準化列名
                    df = self._standardize_columns(df)
                    
                    # MEM-001 FIX: 記錄時間戳並檢查緩存限制
                    import time
                    self._evict_expired_cache()
                    self.cache[t] = df
                    self._cache_timestamps[t] = time.time()
                    results[t] = df
                
                logger.info("數據下載完成")
                return results
                
            except Exception as e:
                logger.error(f"下載失敗 (嘗試 {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("達到最大重試次數，放棄下載")
                    raise e
        
        return results

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        將列名標準化為: Open, High, Low, Close, Volume, Adj Close
        """
        # yfinance columns 通常是 Title Case: Open, High, Low, Close, Volume
        # 確保列存在
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # 檢查是否有缺失列
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            logger.warning(f"數據缺失列: {missing}")
        
        # 強制轉換為標準格式
        # 如果需要，這裡可以處理列名映射 (比如有些源是大寫全稱)
        
        # 處理空值: 先 ffill 再 bfill
        df = df.ffill().bfill()
        
        return df

if __name__ == "__main__":
    # 測試代碼
    loader = DataLoader()
    data = loader.fetch_data(["AAPL", "BTC-USD"], start_date="2025-01-01")
    
    for ticker, df in data.items():
        print(f"\n--- {ticker} ---")
        print(df.tail())
