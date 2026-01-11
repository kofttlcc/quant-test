"""
sector_rotation.py - 板塊輪動分析模組
=============================================
版本: v1.0 (專家優化建議 Sprint 2)
功能: 11 個 SPDR 板塊 ETF 相對強弱分析

專家建議: 小宇宙策略更多靠 Sector Rotation (板塊輪動)

板塊 ETF:
- XLB: Materials
- XLC: Communication Services
- XLE: Energy
- XLF: Financials
- XLI: Industrials
- XLK: Technology
- XLP: Consumer Staples
- XLRE: Real Estate
- XLU: Utilities
- XLV: Healthcare
- XLY: Consumer Discretionary
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 板塊 ETF 定義
SECTOR_ETFS = {
    "XLB": "Materials",
    "XLC": "Communication Services", 
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Technology",
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLV": "Healthcare",
    "XLY": "Consumer Discretionary"
}

# 股票到板塊的映射 (常見股票)
STOCK_TO_SECTOR = {
    # Technology
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "AMD": "XLK", "INTC": "XLK",
    "AVGO": "XLK", "CRM": "XLK", "ORCL": "XLK", "CSCO": "XLK", "IBM": "XLK",
    
    # Communication Services
    "GOOGL": "XLC", "GOOG": "XLC", "META": "XLC", "NFLX": "XLC", "DIS": "XLC",
    
    # Consumer Discretionary
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY", "NKE": "XLY", "MCD": "XLY",
    
    # Financials
    "JPM": "XLF", "BAC": "XLF", "WFC": "XLF", "GS": "XLF", "MS": "XLF",
    "BRK-B": "XLF", "V": "XLF", "MA": "XLF",
    
    # Healthcare
    "JNJ": "XLV", "UNH": "XLV", "PFE": "XLV", "ABBV": "XLV", "MRK": "XLV",
    "LLY": "XLV", "TMO": "XLV",
    
    # Energy
    "XOM": "XLE", "CVX": "XLE", "COP": "XLE", "SLB": "XLE",
    
    # Industrials
    "CAT": "XLI", "BA": "XLI", "HON": "XLI", "UPS": "XLI", "GE": "XLI",
    
    # Consumer Staples
    "PG": "XLP", "KO": "XLP", "PEP": "XLP", "WMT": "XLP", "COST": "XLP",
    
    # Utilities
    "NEE": "XLU", "DUK": "XLU", "SO": "XLU",
    
    # Real Estate
    "AMT": "XLRE", "PLD": "XLRE", "CCI": "XLRE",
    
    # Materials
    "LIN": "XLB", "APD": "XLB", "ECL": "XLB"
}


@dataclass
class SectorMomentum:
    """板塊動量狀態"""
    etf: str
    name: str
    return_1m: float
    return_3m: float
    relative_strength: float  # 相對 SPY
    rank: int  # 強弱排名 (1 = 最強)


@dataclass 
class SectorRotationSignal:
    """板塊輪動信號"""
    top_sectors: List[str]  # 最強板塊
    bottom_sectors: List[str]  # 最弱板塊
    rotation_score: float  # 輪動強度評分
    recommendation: str


class SectorRotationAnalyzer:
    """
    板塊輪動分析器
    
    策略邏輯:
    1. 計算各板塊的相對動量
    2. 識別領先/落後板塊
    3. 為個股提供板塊權重調整建議
    """
    
    def __init__(self):
        self.sector_data: Dict[str, pd.DataFrame] = {}
        self.spy_data: Optional[pd.DataFrame] = None
        self._initialized = False
        
    def fetch_data(self, period: str = "1y") -> bool:
        """獲取所有板塊 ETF 數據"""
        try:
            import yfinance as yf
            
            # 獲取 SPY 作為基準
            spy = yf.download("SPY", period=period, progress=False)
            if isinstance(spy.columns, pd.MultiIndex):
                spy.columns = spy.columns.get_level_values(0)
            self.spy_data = spy
            
            # 獲取各板塊 ETF
            success_count = 0
            for etf in SECTOR_ETFS.keys():
                try:
                    data = yf.download(etf, period=period, progress=False)
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.get_level_values(0)
                    if not data.empty:
                        self.sector_data[etf] = data
                        success_count += 1
                except Exception as e:
                    logger.warning(f"Failed to fetch {etf}: {e}")
            
            self._initialized = success_count >= 8  # 至少 8 個板塊成功
            logger.info(f"Sector data loaded: {success_count}/{len(SECTOR_ETFS)} ETFs")
            return self._initialized
            
        except Exception as e:
            logger.error(f"Failed to fetch sector data: {e}")
            return False
    
    def calculate_sector_momentum(self) -> List[SectorMomentum]:
        """計算所有板塊的動量"""
        if not self._initialized:
            return []
            
        results = []
        spy_ret_1m = self._calculate_return(self.spy_data, 21)
        spy_ret_3m = self._calculate_return(self.spy_data, 63)
        
        for etf, data in self.sector_data.items():
            ret_1m = self._calculate_return(data, 21)
            ret_3m = self._calculate_return(data, 63)
            
            # 相對強弱 = 板塊收益 - SPY 收益
            rs = ret_3m - spy_ret_3m
            
            results.append(SectorMomentum(
                etf=etf,
                name=SECTOR_ETFS.get(etf, etf),
                return_1m=ret_1m,
                return_3m=ret_3m,
                relative_strength=rs,
                rank=0  # 稍後計算
            ))
        
        # 按相對強弱排序並分配排名
        results.sort(key=lambda x: x.relative_strength, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1
            
        return results
    
    def _calculate_return(self, data: pd.DataFrame, days: int) -> float:
        """計算 N 日收益率"""
        if data is None or len(data) < days:
            return 0.0
        try:
            current = float(data['Close'].iloc[-1])
            past = float(data['Close'].iloc[-days])
            return (current / past) - 1
        except:
            return 0.0
    
    def get_rotation_signal(self) -> SectorRotationSignal:
        """獲取板塊輪動信號"""
        momentum = self.calculate_sector_momentum()
        
        if len(momentum) < 6:
            return SectorRotationSignal([], [], 0, "Insufficient data")
        
        # 頂部 3 個板塊
        top_sectors = [m.etf for m in momentum[:3]]
        # 底部 3 個板塊
        bottom_sectors = [m.etf for m in momentum[-3:]]
        
        # 輪動強度 = 頂部 vs 底部的差距
        top_avg = np.mean([m.relative_strength for m in momentum[:3]])
        bottom_avg = np.mean([m.relative_strength for m in momentum[-3:]])
        rotation_score = top_avg - bottom_avg
        
        # 生成建議
        if rotation_score > 0.10:  # 10% 差距
            recommendation = f"強輪動: 增持 {', '.join(top_sectors)}，減持 {', '.join(bottom_sectors)}"
        elif rotation_score > 0.05:
            recommendation = f"中等輪動: 傾向 {', '.join(top_sectors)}"
        else:
            recommendation = "弱輪動: 板塊分化不明顯，建議均衡配置"
            
        return SectorRotationSignal(
            top_sectors=top_sectors,
            bottom_sectors=bottom_sectors,
            rotation_score=rotation_score,
            recommendation=recommendation
        )
    
    def get_stock_sector_weight(self, ticker: str) -> float:
        """
        根據板塊輪動獲取個股的權重調整係數
        
        Returns:
            1.0 = 中性
            > 1.0 = 增持 (板塊領先)
            < 1.0 = 減持 (板塊落後)
        """
        sector_etf = STOCK_TO_SECTOR.get(ticker.upper())
        if not sector_etf:
            return 1.0
            
        momentum = self.calculate_sector_momentum()
        for m in momentum:
            if m.etf == sector_etf:
                n = len(momentum)
                # 排名 1 -> 1.3, 排名 N -> 0.7
                weight = 1.0 + (n - m.rank) / n * 0.3 - 0.15
                return max(0.5, min(1.5, weight))
                
        return 1.0
    
    def get_sector_features(self, tickers: List[str]) -> pd.DataFrame:
        """
        為一組股票生成板塊特徵
        
        用於特徵工程
        """
        momentum = self.calculate_sector_momentum()
        sector_map = {m.etf: m for m in momentum}
        
        features = []
        for ticker in tickers:
            sector_etf = STOCK_TO_SECTOR.get(ticker.upper(), None)
            if sector_etf and sector_etf in sector_map:
                m = sector_map[sector_etf]
                features.append({
                    "ticker": ticker,
                    "sector": sector_etf,
                    "sector_ret_1m": m.return_1m,
                    "sector_ret_3m": m.return_3m,
                    "sector_rs": m.relative_strength,
                    "sector_rank": m.rank,
                    "sector_weight": self.get_stock_sector_weight(ticker)
                })
            else:
                features.append({
                    "ticker": ticker,
                    "sector": "Unknown",
                    "sector_ret_1m": 0,
                    "sector_ret_3m": 0,
                    "sector_rs": 0,
                    "sector_rank": 6,  # 中位
                    "sector_weight": 1.0
                })
                
        return pd.DataFrame(features)


if __name__ == "__main__":
    print("--- SELF-TEST: sector_rotation.py ---")
    
    analyzer = SectorRotationAnalyzer()
    
    print("\n[TEST] Fetching sector data...")
    success = analyzer.fetch_data(period="6mo")
    print(f"  Success: {success}")
    
    if success:
        print("\n[TEST] Sector Momentum:")
        momentum = analyzer.calculate_sector_momentum()
        for m in momentum[:5]:
            print(f"  {m.rank}. {m.etf} ({m.name}): "
                  f"1M={m.return_1m:.1%}, 3M={m.return_3m:.1%}, RS={m.relative_strength:.1%}")
        
        print("\n[TEST] Rotation Signal:")
        signal = analyzer.get_rotation_signal()
        print(f"  Top: {signal.top_sectors}")
        print(f"  Bottom: {signal.bottom_sectors}")
        print(f"  Score: {signal.rotation_score:.2%}")
        print(f"  Recommendation: {signal.recommendation}")
        
        print("\n[TEST] Stock Sector Weights:")
        test_stocks = ["AAPL", "XOM", "JPM", "UNH", "UNKNOWN"]
        for stock in test_stocks:
            weight = analyzer.get_stock_sector_weight(stock)
            sector = STOCK_TO_SECTOR.get(stock, "Unknown")
            print(f"  {stock} ({sector}): {weight:.2f}")
    
    print("\n--- SELF-TEST COMPLETE ---")
