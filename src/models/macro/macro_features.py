"""
macro_features.py - 擴展宏觀特徵模組
=============================================
版本: v2.0 (專家優化建議 Sprint 1)
功能: 利率、CPI 代理、SPY 相關性特徵

數據源: yfinance (免費)
- ^TNX: 10 年期國債收益率 (利率代理)
- ^IRX: 13 週國庫券利率 (短期利率)
- SPY: S&P 500 ETF (市場 Beta)
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class InterestRateState:
    """利率狀態"""
    current_level: float
    change_30d: float  # 30 日變化 (bps)
    regime: str  # "Rising", "Stable", "Falling"
    signal: int  # -1, 0, 1


@dataclass
class MarketBetaState:
    """市場 Beta 狀態"""
    ticker: str
    beta_60d: float
    correlation_60d: float
    relative_strength: float  # 相對 SPY 的強弱


class InterestRateAnalyzer:
    """
    利率分析器
    
    使用 10 年期國債收益率 (^TNX) 作為利率代理
    專家建議: 利率變化對股票估值有重大影響
    """
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.short_rate_data: Optional[pd.DataFrame] = None
        
    def fetch_data(self, period: str = "2y") -> bool:
        """獲取利率數據"""
        try:
            import yfinance as yf
            
            # 10 年期國債收益率
            tnx = yf.download("^TNX", period=period, progress=False)
            
            if tnx.empty:
                logger.error("TNX (10Y Yield) data is empty")
                return False
                
            # 處理 MultiIndex
            if isinstance(tnx.columns, pd.MultiIndex):
                tnx.columns = tnx.columns.get_level_values(0)
                
            self.data = tnx
            
            # 嘗試獲取短期利率 (可選)
            try:
                irx = yf.download("^IRX", period=period, progress=False)
                if isinstance(irx.columns, pd.MultiIndex):
                    irx.columns = irx.columns.get_level_values(0)
                self.short_rate_data = irx
            except Exception as e:
                logger.debug(f"Short rate fetch failed: {e}")
                pass
                
            logger.info(f"Interest rate data loaded: {len(tnx)} rows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch interest rate data: {e}")
            return False
    
    def get_current_state(self) -> Optional[InterestRateState]:
        """獲取當前利率狀態"""
        if self.data is None or self.data.empty:
            return None
            
        current = float(self.data['Close'].iloc[-1])
        
        # 30 日變化 (bps)
        if len(self.data) >= 30:
            prev_30d = float(self.data['Close'].iloc[-30])
            change_30d = (current - prev_30d) * 100  # 轉換為 bps
        else:
            change_30d = 0.0
        
        # 確定 Regime
        if change_30d > 20:  # 上升超過 20bps
            regime = "Rising"
            signal = -1  # 利率上升對股票不利
        elif change_30d < -20:  # 下降超過 20bps
            regime = "Falling"
            signal = 1  # 利率下降對股票有利
        else:
            regime = "Stable"
            signal = 0
            
        return InterestRateState(
            current_level=current,
            change_30d=change_30d,
            regime=regime,
            signal=signal
        )
    
    def get_rate_series(self) -> pd.Series:
        """獲取利率時間序列（用於特徵工程）"""
        if self.data is None:
            return pd.Series()
        return self.data['Close'].copy()
    
    def get_yield_curve_slope(self) -> Optional[float]:
        """
        獲取收益率曲線斜率 (10Y - 3M)
        斜率倒掛 (<0) 通常預示經濟衰退
        """
        if self.data is None or self.short_rate_data is None:
            return None
            
        try:
            long_rate = float(self.data['Close'].iloc[-1])
            short_rate = float(self.short_rate_data['Close'].iloc[-1])
            return long_rate - short_rate
        except Exception:
            return None


class MarketCorrelationAnalyzer:
    """
    市場相關性分析器
    
    專家建議: 小宇宙策略更多依靠 Beta (跟隨大勢)
    計算個股與 SPY 的滾動 Beta 和相關係數
    """
    
    def __init__(self, benchmark: str = "SPY"):
        self.benchmark = benchmark
        self.benchmark_data: Optional[pd.DataFrame] = None
        
    def fetch_benchmark(self, period: str = "2y") -> bool:
        """獲取基準數據"""
        try:
            import yfinance as yf
            
            spy = yf.download(self.benchmark, period=period, progress=False)
            
            if spy.empty:
                logger.error(f"{self.benchmark} data is empty")
                return False
                
            if isinstance(spy.columns, pd.MultiIndex):
                spy.columns = spy.columns.get_level_values(0)
                
            self.benchmark_data = spy
            logger.info(f"Benchmark {self.benchmark} data loaded: {len(spy)} rows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch benchmark data: {e}")
            return False
    
    def calculate_beta(self, stock_prices: pd.Series, window: int = 60) -> pd.Series:
        """
        計算滾動 Beta
        
        Beta = Cov(Stock, Market) / Var(Market)
        
        Args:
            stock_prices: 個股價格序列
            window: 滾動窗口天數
            
        Returns:
            滾動 Beta 序列
        """
        if self.benchmark_data is None:
            return pd.Series()
            
        # 對齊數據
        benchmark_prices = self.benchmark_data['Close']
        aligned_stock, aligned_benchmark = stock_prices.align(benchmark_prices, join='inner')
        
        # 計算收益率
        stock_ret = aligned_stock.pct_change()
        market_ret = aligned_benchmark.pct_change()
        
        # 滾動協方差和方差
        cov = stock_ret.rolling(window).cov(market_ret)
        var = market_ret.rolling(window).var()
        
        beta = cov / var
        return beta
    
    def calculate_correlation(self, stock_prices: pd.Series, window: int = 60) -> pd.Series:
        """計算滾動相關係數"""
        if self.benchmark_data is None:
            return pd.Series()
            
        benchmark_prices = self.benchmark_data['Close']
        aligned_stock, aligned_benchmark = stock_prices.align(benchmark_prices, join='inner')
        
        stock_ret = aligned_stock.pct_change()
        market_ret = aligned_benchmark.pct_change()
        
        corr = stock_ret.rolling(window).corr(market_ret)
        return corr
    
    def calculate_relative_strength(self, stock_prices: pd.Series, window: int = 20) -> pd.Series:
        """
        計算相對強弱 (RS)
        
        RS = Stock Performance / Benchmark Performance
        RS > 1: 股票跑贏大盤
        RS < 1: 股票跑輸大盤
        """
        if self.benchmark_data is None:
            return pd.Series()
            
        benchmark_prices = self.benchmark_data['Close']
        aligned_stock, aligned_benchmark = stock_prices.align(benchmark_prices, join='inner')
        
        stock_perf = aligned_stock.pct_change(window)
        bench_perf = aligned_benchmark.pct_change(window)
        
        rs = (1 + stock_perf) / (1 + bench_perf)
        return rs
    
    def get_stock_state(self, stock_prices: pd.Series, ticker: str = "STOCK") -> Optional[MarketBetaState]:
        """獲取個股市場狀態"""
        beta = self.calculate_beta(stock_prices)
        corr = self.calculate_correlation(stock_prices)
        rs = self.calculate_relative_strength(stock_prices)
        
        if beta.empty:
            return None
            
        return MarketBetaState(
            ticker=ticker,
            beta_60d=float(beta.iloc[-1]) if not pd.isna(beta.iloc[-1]) else 1.0,
            correlation_60d=float(corr.iloc[-1]) if not pd.isna(corr.iloc[-1]) else 0.5,
            relative_strength=float(rs.iloc[-1]) if not pd.isna(rs.iloc[-1]) else 1.0
        )


class MacroFeatureEngine:
    """
    宏觀特徵引擎 - 整合所有宏觀數據源
    
    專家建議: 這是特徵工程的核心 (70% 精力)
    """
    
    def __init__(self):
        self.rate_analyzer = InterestRateAnalyzer()
        self.market_analyzer = MarketCorrelationAnalyzer()
        self._initialized = False
        
    def initialize(self) -> Dict[str, bool]:
        """初始化所有數據源"""
        results = {}
        results['interest_rate'] = self.rate_analyzer.fetch_data()
        results['market_benchmark'] = self.market_analyzer.fetch_benchmark()
        self._initialized = all(results.values())
        return results
    
    def get_macro_features(self, stock_prices: pd.Series, ticker: str = "STOCK") -> Dict[str, pd.Series]:
        """
        獲取所有宏觀特徵
        
        Returns:
            包含以下特徵的字典:
            - rate_level: 利率水平
            - rate_change: 利率變化率
            - beta: 市場 Beta
            - correlation: 市場相關性
            - relative_strength: 相對強弱
        """
        if not self._initialized:
            self.initialize()
            
        features = {}
        
        # 利率特徵
        rate_series = self.rate_analyzer.get_rate_series()
        if not rate_series.empty:
            features['rate_level'] = rate_series
            features['rate_change'] = rate_series.pct_change(20)  # 20 日變化率
        
        # 市場 Beta 特徵
        features['beta'] = self.market_analyzer.calculate_beta(stock_prices)
        features['correlation'] = self.market_analyzer.calculate_correlation(stock_prices)
        features['relative_strength'] = self.market_analyzer.calculate_relative_strength(stock_prices)
        
        return features
    
    def get_composite_signal(self, stock_prices: pd.Series = None) -> Dict:
        """獲取綜合宏觀信號"""
        rate_state = self.rate_analyzer.get_current_state()
        
        result = {
            "interest_rate": {
                "level": rate_state.current_level if rate_state else None,
                "change_30d_bps": rate_state.change_30d if rate_state else None,
                "regime": rate_state.regime if rate_state else "Unknown",
                "signal": rate_state.signal if rate_state else 0
            },
            "yield_curve_slope": self.rate_analyzer.get_yield_curve_slope()
        }
        
        if stock_prices is not None:
            stock_state = self.market_analyzer.get_stock_state(stock_prices)
            result["market_beta"] = {
                "beta_60d": stock_state.beta_60d if stock_state else 1.0,
                "correlation_60d": stock_state.correlation_60d if stock_state else 0.5,
                "relative_strength": stock_state.relative_strength if stock_state else 1.0
            }
        
        return result


if __name__ == "__main__":
    print("--- SELF-TEST: macro_features.py ---")
    
    engine = MacroFeatureEngine()
    
    print("\n[TEST] Initializing data sources...")
    results = engine.initialize()
    print(f"Initialization results: {results}")
    
    print("\n[TEST] Get rate state...")
    rate_state = engine.rate_analyzer.get_current_state()
    if rate_state:
        print(f"  10Y Yield: {rate_state.current_level:.2f}%")
        print(f"  30D Change: {rate_state.change_30d:.1f} bps")
        print(f"  Regime: {rate_state.regime}")
    
    print("\n[TEST] Get yield curve slope...")
    slope = engine.rate_analyzer.get_yield_curve_slope()
    print(f"  Yield Curve Slope (10Y-3M): {slope:.2f}%" if slope else "  N/A")
    
    # 模擬股票數據測試
    print("\n[TEST] Testing with dummy stock prices...")
    import yfinance as yf
    aapl = yf.download("AAPL", period="1y", progress=False)
    if isinstance(aapl.columns, pd.MultiIndex):
        aapl.columns = aapl.columns.get_level_values(0)
    stock_prices = aapl['Close']
    
    features = engine.get_macro_features(stock_prices, "AAPL")
    print(f"  Features generated: {list(features.keys())}")
    print(f"  Latest Beta: {features['beta'].iloc[-1]:.2f}" if not features['beta'].empty else "  N/A")
    
    print("\n--- SELF-TEST COMPLETE ---")
