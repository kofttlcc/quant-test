"""
data_update_service.py - 數據更新服務
=========================================
版本: v2.0 (S&P 500 Full Coverage)
功能:
1. 歷史價格數據更新 (2008-2026)
2. 財報數據全量下載
3. S&P 500 全覆蓋支持
4. 進度回調和日誌輸出

數據源: yfinance
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Callable, Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UpdateProgress:
    """更新進度"""
    total: int
    completed: int
    current_ticker: str
    status: str  # "running", "completed", "failed"
    errors: List[str]
    
    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0


@dataclass
class DataCoverageReport:
    """數據覆蓋報告"""
    ticker: str
    price_start: Optional[str]
    price_end: Optional[str]
    price_rows: int
    has_financials: bool
    financial_metrics: List[str]
    status: str  # "complete", "partial", "missing"


class DataUpdateService:
    """數據更新服務 - 支持 S&P 500 全覆蓋"""
    
    # 默認股票列表（小規模測試用）
    DEFAULT_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "BRK-B", "JPM", "V"
    ]
    
    # 目標數據覆蓋範圍 - 擴展到 2008
    TARGET_START_DATE = "2008-01-01"
    TARGET_END_DATE = datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def _convert_timestamp_keys(df):
        """
        MAJOR-005 FIX: 將 DataFrame 轉為 dict，確保 key 是字符串
        統一提取為靜態方法，消除重複代碼
        """
        if df is None or df.empty:
            return {}
        df_copy = df.copy()
        df_copy.columns = [
            col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) 
            for col in df_copy.columns
        ]
        return df_copy.to_dict()
    
    def __init__(self, cache_dir: str = "quant_data"):
        self.cache_dir = cache_dir
        self.progress: Optional[UpdateProgress] = None
        self._lock = threading.Lock()
        self._cancel_flag = False
        
        # 確保目錄存在
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "prices"), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, "financials"), exist_ok=True)
    
    def get_sp500_tickers(self) -> List[str]:
        """
        獲取 S&P 500 股票列表
        優先從 Wikipedia 抓取，失敗則使用備用列表
        """
        try:
            import pandas as pd
            table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            df = table[0]
            tickers = df['Symbol'].tolist()
            # 修復 BRK.B -> BRK-B
            return [t.replace('.', '-') for t in tickers]
        except Exception as e:
            logger.warning(f"Failed to scrape S&P500: {e}. Using default Top 50.")
            return [
                "AAPL", "MSFT", "GOOG", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "V", "JNJ",
                "WMT", "JPM", "PG", "MA", "UNH", "HD", "CVX", "MRK", "ABBV", "KO", "PEP",
                "BAC", "AVGO", "COST", "PFE", "TMO", "CSCO", "ACN", "ABT", "DHR", "NFLX",
                "LIN", "MCD", "DIS", "TXN", "NEE", "ADBE", "PM", "AMD", "VZ", "CRM", "NKE",
                "ORCL", "INTC", "QCOM", "IBM", "GE", "CAT", "HON", "UPS"
            ]
        
    def audit_data_coverage(self, tickers: List[str] = None) -> List[DataCoverageReport]:
        """
        審計數據覆蓋情況
        
        Args:
            tickers: 要審計的股票列表
            
        Returns:
            數據覆蓋報告列表
        """
        if tickers is None:
            tickers = self.DEFAULT_TICKERS
            
        reports = []
        
        for ticker in tickers:
            report = self._audit_single_ticker(ticker)
            reports.append(report)
            
        return reports
    
    def _audit_single_ticker(self, ticker: str) -> DataCoverageReport:
        """審計單個股票的數據覆蓋"""
        price_file = os.path.join(self.cache_dir, "prices", f"{ticker}.csv")
        financial_file = os.path.join(self.cache_dir, "financials", f"{ticker}.json")
        
        price_start = None
        price_end = None
        price_rows = 0
        has_financials = False
        financial_metrics = []
        
        # 檢查價格數據
        if os.path.exists(price_file):
            try:
                import pandas as pd
                df = pd.read_csv(price_file, parse_dates=['Date'])
                price_rows = len(df)
                if price_rows > 0:
                    price_start = df['Date'].min().strftime("%Y-%m-%d")
                    price_end = df['Date'].max().strftime("%Y-%m-%d")
            except Exception as e:
                logger.warning(f"Failed to read {price_file}: {e}")
                
        # 檢查財報數據
        if os.path.exists(financial_file):
            try:
                with open(financial_file, 'r') as f:
                    data = json.load(f)
                    financial_metrics = list(data.keys()) if isinstance(data, dict) else []
                    has_financials = len(financial_metrics) > 0
            except Exception as e:
                logger.warning(f"Failed to read {financial_file}: {e}")
        
        # 確定狀態
        if price_rows > 0 and price_start and price_start <= "2010-01-01" and has_financials:
            status = "complete"
        elif price_rows > 0:
            status = "partial"
        else:
            status = "missing"
            
        return DataCoverageReport(
            ticker=ticker,
            price_start=price_start,
            price_end=price_end,
            price_rows=price_rows,
            has_financials=has_financials,
            financial_metrics=financial_metrics[:5],  # 只顯示前5個
            status=status
        )
    
    def update_incremental(
        self,
        tickers: List[str] = None,
        progress_callback: Callable[[UpdateProgress], None] = None,
        force_full: bool = False
    ) -> UpdateProgress:
        """
        增量更新數據（斷點續傳）
        
        只下載缺失的日期範圍，而非全量重新下載。
        如果 force_full=True，則強制全量更新。
        
        Args:
            tickers: 要更新的股票列表
            progress_callback: 進度回調函數
            force_full: 強制全量更新
            
        Returns:
            最終進度狀態
        """
        import pandas as pd
        import yfinance as yf
        from datetime import datetime, timedelta
        
        if tickers is None:
            tickers = self.DEFAULT_TICKERS
            
        with self._lock:
            self.progress = UpdateProgress(
                total=len(tickers),
                completed=0,
                current_ticker="",
                status="running",
                errors=[]
            )
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            for ticker in tickers:
                self._update_progress(ticker, "incremental", progress_callback)
                
                try:
                    price_file = os.path.join(self.cache_dir, "prices", f"{ticker}.csv")
                    start_date = self.TARGET_START_DATE  # 默認完整歷史
                    
                    # 檢查現有數據
                    if not force_full and os.path.exists(price_file):
                        try:
                            existing_df = pd.read_csv(price_file, parse_dates=['Date'])
                            if not existing_df.empty:
                                last_date = existing_df['Date'].max()
                                # 從最後日期的下一天開始
                                start_date = (last_date + timedelta(days=1)).strftime("%Y-%m-%d")
                                logger.info(f"{ticker}: 增量從 {start_date} 開始 (已有 {len(existing_df)} 行)")
                                
                                # 如果最後日期已經是今天，跳過
                                if start_date >= today:
                                    logger.info(f"{ticker}: 數據已是最新，跳過")
                                    self._increment_completed(progress_callback)
                                    continue
                        except Exception as e:
                            logger.warning(f"{ticker}: 讀取現有數據失敗，執行全量更新 - {e}")
                    
                    # 下載新數據
                    logger.info(f"{ticker}: 下載 {start_date} 至 {today}")
                    new_df = yf.download(
                        ticker,
                        start=start_date,
                        end=today,
                        progress=False
                    )
                    
                    if not new_df.empty:
                        # 處理 MultiIndex
                        if hasattr(new_df.columns, 'get_level_values'):
                            new_df.columns = new_df.columns.get_level_values(0)
                        
                        # 重置索引將 Date 變為列
                        new_df = new_df.reset_index()
                        if 'index' in new_df.columns:
                            new_df.rename(columns={'index': 'Date'}, inplace=True)
                        
                        # ===== 數據完整性驗證 =====
                        try:
                            from src.data_loader.validator import DataValidator
                            validator = DataValidator()
                            
                            # 驗證新下載的數據
                            is_valid, report = validator.validate(new_df.set_index('Date') if 'Date' in new_df.columns else new_df, ticker)
                            
                            if not is_valid:
                                # 數據有嚴重問題，拒絕保存
                                logger.warning(f"{ticker}: 新數據驗證失敗，拒絕保存 - {report['issues']}")
                                self._add_error(f"{ticker}: 數據驗證失敗 - {report['issues']}", progress_callback)
                                self._increment_completed(progress_callback)
                                continue
                            elif report.get('warnings'):
                                logger.info(f"{ticker}: 數據警告 (仍保存) - {report['warnings']}")
                        except ImportError:
                            logger.warning(f"{ticker}: DataValidator 未安裝，跳過驗證")
                        except Exception as e:
                            logger.warning(f"{ticker}: 驗證過程異常 - {e}")
                        
                        # 合併或覆蓋
                        if not force_full and os.path.exists(price_file):
                            try:
                                existing_df = pd.read_csv(price_file, parse_dates=['Date'])
                                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                                combined_df.drop_duplicates(subset=['Date'], keep='last', inplace=True)
                                combined_df.sort_values('Date', inplace=True)
                                combined_df.to_csv(price_file, index=False)
                                logger.info(f"{ticker}: 合併完成，共 {len(combined_df)} 行 (新增 {len(new_df)} 行)")
                            except Exception as e:
                                # 合併失敗則直接覆蓋
                                new_df.to_csv(price_file, index=False)
                                logger.warning(f"{ticker}: 合併失敗，直接覆蓋 - {e}")
                        else:
                            new_df.to_csv(price_file, index=False)
                            logger.info(f"{ticker}: 保存 {len(new_df)} 行")
                    else:
                        logger.info(f"{ticker}: 無新數據")
                    
                    # ===== 財報增量更新 =====
                    financial_file = os.path.join(self.cache_dir, "financials", f"{ticker}.json")
                    try:
                        stock = yf.Ticker(ticker)
                        
                        def convert_timestamp_keys(df):
                            """將 DataFrame 轉為 dict，確保 key 是字符串"""
                            if df is None or df.empty:
                                return {}
                            df_copy = df.copy()
                            df_copy.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in df_copy.columns]
                            return df_copy.to_dict()
                        
                        new_financials = {}
                        if stock.income_stmt is not None and not stock.income_stmt.empty:
                            new_financials['income_stmt'] = convert_timestamp_keys(stock.income_stmt)
                        if stock.balance_sheet is not None and not stock.balance_sheet.empty:
                            new_financials['balance_sheet'] = convert_timestamp_keys(stock.balance_sheet)
                        if stock.cashflow is not None and not stock.cashflow.empty:
                            new_financials['cashflow'] = convert_timestamp_keys(stock.cashflow)
                        
                        if new_financials:
                            # 檢查是否有新數據需要更新
                            if os.path.exists(financial_file):
                                try:
                                    with open(financial_file, 'r') as f:
                                        existing = json.load(f)
                                    # 比較最新季度日期
                                    existing_dates = set()
                                    new_dates = set()
                                    for key in ['income_stmt', 'balance_sheet', 'cashflow']:
                                        if key in existing and isinstance(existing[key], dict):
                                            existing_dates.update(existing[key].keys() if isinstance(next(iter(existing[key].values()), None), dict) else [])
                                        if key in new_financials:
                                            first_val = next(iter(new_financials[key].values()), None)
                                            if isinstance(first_val, dict):
                                                new_dates.update(first_val.keys())
                                    
                                    if new_dates - existing_dates:
                                        # 有新季度數據，合併更新
                                        for key in new_financials:
                                            if key in existing:
                                                existing[key].update(new_financials[key])
                                            else:
                                                existing[key] = new_financials[key]
                                        with open(financial_file, 'w') as f:
                                            json.dump(existing, f, default=str, indent=2)
                                        logger.info(f"{ticker}: 財報增量更新完成 (新季度: {new_dates - existing_dates})")
                                    else:
                                        logger.info(f"{ticker}: 財報已是最新")
                                except Exception as e:
                                    # 解析失敗則直接覆蓋
                                    with open(financial_file, 'w') as f:
                                        json.dump(new_financials, f, default=str, indent=2)
                                    logger.warning(f"{ticker}: 財報合併失敗，直接覆蓋 - {e}")
                            else:
                                with open(financial_file, 'w') as f:
                                    json.dump(new_financials, f, default=str, indent=2)
                                logger.info(f"{ticker}: 財報新建保存")
                    except Exception as e:
                        logger.warning(f"{ticker}: 財報更新失敗 - {e}")
                        
                    self._increment_completed(progress_callback)
                    
                except Exception as e:
                    self._add_error(f"{ticker}: {e}", progress_callback)
                    self._increment_completed(progress_callback)
                    
                # 速率限制
                time.sleep(0.5)
            
            with self._lock:
                self.progress.status = "completed"
                
        except Exception as e:
            with self._lock:
                self.progress.status = "failed"
                self.progress.errors.append(f"Fatal: {e}")
                
        if progress_callback:
            progress_callback(self.progress)
            
        return self.progress
    
    def update_all(
        self,
        tickers: List[str] = None,
        progress_callback: Callable[[UpdateProgress], None] = None
    ) -> UpdateProgress:
        """
        更新所有數據
        
        Args:
            tickers: 要更新的股票列表
            progress_callback: 進度回調函數
            
        Returns:
            最終進度狀態
        """
        if tickers is None:
            tickers = self.DEFAULT_TICKERS
            
        with self._lock:
            self.progress = UpdateProgress(
                total=len(tickers) * 2,  # 價格 + 財報
                completed=0,
                current_ticker="",
                status="running",
                errors=[]
            )
        
        try:
            import yfinance as yf
            
            for ticker in tickers:
                # 更新價格數據
                self._update_progress(ticker, "price", progress_callback)
                try:
                    df = yf.download(
                        ticker,
                        start=self.TARGET_START_DATE,
                        end=self.TARGET_END_DATE,
                        progress=False
                    )
                    if not df.empty:
                        # 處理 MultiIndex
                        if hasattr(df.columns, 'get_level_values'):
                            df.columns = df.columns.get_level_values(0)
                        df.to_csv(os.path.join(self.cache_dir, "prices", f"{ticker}.csv"))
                        logger.info(f"Saved {len(df)} rows for {ticker}")
                    self._increment_completed(progress_callback)
                except Exception as e:
                    self._add_error(f"{ticker} price: {e}", progress_callback)
                    self._increment_completed(progress_callback)
                
                # 更新財報數據
                self._update_progress(ticker, "financials", progress_callback)
                try:
                    stock = yf.Ticker(ticker)
                    financials = {}
                    
                    # 獲取財報 - Issue 1 FIX: 將 Timestamp 列名轉為字符串
                    def convert_timestamp_keys(df):
                        """將 DataFrame 轉為 dict，確保 key 是字符串"""
                        if df is None or df.empty:
                            return {}
                        # 將 Timestamp 列名轉為字符串
                        df_copy = df.copy()
                        df_copy.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in df_copy.columns]
                        return df_copy.to_dict()
                    
                    if stock.income_stmt is not None and not stock.income_stmt.empty:
                        financials['income_stmt'] = convert_timestamp_keys(stock.income_stmt)
                    if stock.balance_sheet is not None and not stock.balance_sheet.empty:
                        financials['balance_sheet'] = convert_timestamp_keys(stock.balance_sheet)
                    if stock.cashflow is not None and not stock.cashflow.empty:
                        financials['cashflow'] = convert_timestamp_keys(stock.cashflow)
                        
                    if financials:
                        with open(os.path.join(self.cache_dir, "financials", f"{ticker}.json"), 'w') as f:
                            json.dump(financials, f, default=str, indent=2)
                        logger.info(f"Saved financials for {ticker}")
                    self._increment_completed(progress_callback)
                except Exception as e:
                    self._add_error(f"{ticker} financials: {e}", progress_callback)
                    self._increment_completed(progress_callback)
            
            with self._lock:
                self.progress.status = "completed"
                
        except Exception as e:
            with self._lock:
                self.progress.status = "failed"
                self.progress.errors.append(f"Fatal error: {e}")
                
        if progress_callback:
            progress_callback(self.progress)
            
        return self.progress
    
    def update_sp500_all(
        self,
        progress_callback: Callable[[UpdateProgress], None] = None
    ) -> UpdateProgress:
        """
        更新所有 S&P 500 股票數據 (2008-至今)
        
        這是「一鍵更新」的完整版本，覆蓋所有 S&P 500 成分股。
        預計耗時較長（取決於網絡速度，約 30-60 分鐘）。
        
        Returns:
            最終進度狀態
        """
        logger.info("Starting S&P 500 Full Update (2008-present)...")
        tickers = self.get_sp500_tickers()
        logger.info(f"Found {len(tickers)} S&P 500 tickers")
        
        # 添加延遲以避免 rate limiting
        return self._update_with_rate_limit(tickers, progress_callback, delay=1.0)
    
    def _update_with_rate_limit(
        self,
        tickers: List[str],
        progress_callback: Callable[[UpdateProgress], None] = None,
        delay: float = 1.0
    ) -> UpdateProgress:
        """
        帶速率限制的更新（避免被 yfinance 限流）
        """
        with self._lock:
            self.progress = UpdateProgress(
                total=len(tickers) * 2,  # 價格 + 財報
                completed=0,
                current_ticker="",
                status="running",
                errors=[]
            )
            self._cancel_flag = False
        
        try:
            import yfinance as yf
            
            for ticker in tickers:
                # 檢查取消標誌
                if self._cancel_flag:
                    with self._lock:
                        self.progress.status = "cancelled"
                    break
                
                # 更新價格數據
                self._update_progress(ticker, "price", progress_callback)
                try:
                    df = yf.download(
                        ticker,
                        start=self.TARGET_START_DATE,
                        end=self.TARGET_END_DATE,
                        progress=False
                    )
                    if not df.empty:
                        # 處理 MultiIndex
                        if hasattr(df.columns, 'get_level_values'):
                            df.columns = df.columns.get_level_values(0)
                        df.to_csv(os.path.join(self.cache_dir, "prices", f"{ticker}.csv"))
                        logger.info(f"Saved {len(df)} rows for {ticker}")
                    self._increment_completed(progress_callback)
                except Exception as e:
                    self._add_error(f"{ticker} price: {e}", progress_callback)
                    self._increment_completed(progress_callback)
                
                # 更新財報數據
                self._update_progress(ticker, "financials", progress_callback)
                try:
                    stock = yf.Ticker(ticker)
                    financials = {}
                    
                    # 獲取財報 - 將 Timestamp 列名轉為字符串
                    def convert_timestamp_keys(df):
                        if df is None or df.empty:
                            return {}
                        df_copy = df.copy()
                        df_copy.columns = [col.strftime('%Y-%m-%d') if hasattr(col, 'strftime') else str(col) for col in df_copy.columns]
                        return df_copy.to_dict()
                    
                    if stock.income_stmt is not None and not stock.income_stmt.empty:
                        financials['income_stmt'] = convert_timestamp_keys(stock.income_stmt)
                    if stock.balance_sheet is not None and not stock.balance_sheet.empty:
                        financials['balance_sheet'] = convert_timestamp_keys(stock.balance_sheet)
                    if stock.cashflow is not None and not stock.cashflow.empty:
                        financials['cashflow'] = convert_timestamp_keys(stock.cashflow)
                        
                    if financials:
                        with open(os.path.join(self.cache_dir, "financials", f"{ticker}.json"), 'w') as f:
                            json.dump(financials, f, default=str, indent=2)
                        logger.info(f"Saved financials for {ticker}")
                    self._increment_completed(progress_callback)
                except Exception as e:
                    self._add_error(f"{ticker} financials: {e}", progress_callback)
                    self._increment_completed(progress_callback)
                
                # 速率限制
                time.sleep(delay)
            
            if self.progress.status == "running":
                with self._lock:
                    self.progress.status = "completed"
                    
        except Exception as e:
            with self._lock:
                self.progress.status = "failed"
                self.progress.errors.append(f"Fatal error: {e}")
                
        if progress_callback:
            progress_callback(self.progress)
            
        return self.progress
    
    def cancel_update(self):
        """取消正在進行的更新"""
        self._cancel_flag = True
    
    def _update_progress(self, ticker: str, task: str, callback: Callable = None):
        with self._lock:
            self.progress.current_ticker = f"{ticker} ({task})"
        if callback:
            callback(self.progress)
            
    def _increment_completed(self, callback: Callable = None):
        with self._lock:
            self.progress.completed += 1
        if callback:
            callback(self.progress)
            
    def _add_error(self, error: str, callback: Callable = None):
        with self._lock:
            self.progress.errors.append(error)
        logger.error(error)
        if callback:
            callback(self.progress)
    
    def get_progress(self) -> Optional[Dict[str, Any]]:
        """獲取當前進度（用於 API）"""
        if self.progress is None:
            return None
        return asdict(self.progress)


if __name__ == "__main__":
    print("--- SELF-TEST: data_update_service.py ---")
    
    service = DataUpdateService(cache_dir="temp/quant_data")
    
    # 測試審計
    print("\n[TEST] Audit data coverage...")
    reports = service.audit_data_coverage(["AAPL", "MSFT"])
    for r in reports:
        print(f"  {r.ticker}: {r.status} | Rows: {r.price_rows} | Range: {r.price_start} to {r.price_end}")
    
    # 測試更新（只更新 1 個股票）
    print("\n[TEST] Update data (1 ticker)...")
    def print_progress(p: UpdateProgress):
        print(f"  Progress: {p.percentage:.1f}% | {p.current_ticker}")
    
    result = service.update_all(["AAPL"], progress_callback=print_progress)
    print(f"  Final status: {result.status}")
    print(f"  Errors: {result.errors}")
    
    print("\n--- SELF-TEST COMPLETE ---")
