"""
macro_factors.py - 宏觀因子模組
=========================================
版本: v1.0 (Phase 2 Sprint 2)
功能: VIX 恐慌指數等宏觀市場因子

數據源: yfinance (^VIX)
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VIXState:
    """VIX 狀態"""
    current_level: float
    percentile_30d: float
    regime: str  # "Low", "Normal", "Elevated", "Extreme"
    signal: int  # -1, 0, 1


class VIXAnalyzer:
    """
    VIX 恐慌指數分析器
    
    閾值定義:
    - Low: VIX < 15 (市場平靜，可能過度自滿)
    - Normal: 15 <= VIX < 20
    - Elevated: 20 <= VIX < 30 (市場擔憂)
    - Extreme: VIX >= 30 (恐慌)
    """
    
    THRESHOLDS = {
        "low": 15,
        "normal": 20,
        "elevated": 30
    }
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        
    def fetch_data(self, period: str = "1y") -> bool:
        """
        獲取 VIX 數據
        
        Args:
            period: 數據週期 (1mo, 3mo, 6mo, 1y, 2y)
            
        Returns:
            是否成功
        """
        try:
            import yfinance as yf
            vix = yf.download("^VIX", period=period, progress=False)
            
            if vix.empty:
                logger.error("VIX data is empty")
                return False
                
            # 處理 MultiIndex
            if isinstance(vix.columns, pd.MultiIndex):
                vix.columns = vix.columns.get_level_values(0)
                
            self.data = vix
            logger.info(f"VIX data loaded: {len(vix)} rows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fetch VIX data: {e}")
            return False
    
    def get_current_state(self) -> Optional[VIXState]:
        """獲取當前 VIX 狀態"""
        if self.data is None or self.data.empty:
            return None
            
        current = self.data['Close'].iloc[-1]
        
        # 計算 30 日百分位
        last_30 = self.data['Close'].tail(30)
        percentile = (last_30 < current).sum() / len(last_30) * 100
        
        # 確定 Regime
        if current < self.THRESHOLDS["low"]:
            regime = "Low"
            signal = 1  # 可以激進
        elif current < self.THRESHOLDS["normal"]:
            regime = "Normal"
            signal = 0
        elif current < self.THRESHOLDS["elevated"]:
            regime = "Elevated"
            signal = -1  # 減倉
        else:
            regime = "Extreme"
            signal = -1  # 強烈減倉
            
        return VIXState(
            current_level=float(current),
            percentile_30d=float(percentile),
            regime=regime,
            signal=signal
        )
    
    def get_risk_adjustment(self) -> float:
        """
        獲取風險調整係數
        
        Returns:
            0.0 - 1.0 的倉位調整係數
        """
        state = self.get_current_state()
        if state is None:
            return 1.0
            
        # 根據 VIX 水平調整倉位
        if state.regime == "Low":
            return 1.0
        elif state.regime == "Normal":
            return 0.8
        elif state.regime == "Elevated":
            return 0.5
        else:  # Extreme
            return 0.2


class MacroFactorEngine:
    """宏觀因子引擎 - 整合多個宏觀指標"""
    
    def __init__(self):
        self.vix_analyzer = VIXAnalyzer()
        self._cache: Dict[str, Any] = {}
        
    def refresh_all(self) -> Dict[str, bool]:
        """刷新所有宏觀數據"""
        results = {}
        results['vix'] = self.vix_analyzer.fetch_data()
        return results
    
    def get_composite_signal(self) -> Dict[str, Any]:
        """獲取綜合宏觀信號"""
        vix_state = self.vix_analyzer.get_current_state()
        
        return {
            "vix": {
                "level": vix_state.current_level if vix_state else None,
                "regime": vix_state.regime if vix_state else "Unknown",
                "signal": vix_state.signal if vix_state else 0
            },
            "risk_adjustment": self.vix_analyzer.get_risk_adjustment(),
            "recommendation": self._get_recommendation(vix_state)
        }
    
    def _get_recommendation(self, vix_state: Optional[VIXState]) -> str:
        if vix_state is None:
            return "數據不可用"
        if vix_state.regime == "Low":
            return "市場平靜，可考慮增加風險敞口"
        elif vix_state.regime == "Normal":
            return "市場正常，維持標準倉位"
        elif vix_state.regime == "Elevated":
            return "波動升高，建議減少倉位至 50%"
        else:
            return "市場恐慌，建議大幅減倉或對沖"


if __name__ == "__main__":
    print("--- SELF-TEST: macro_factors.py ---")
    
    engine = MacroFactorEngine()
    
    print("\n[TEST] Fetching VIX data...")
    results = engine.refresh_all()
    print(f"Fetch results: {results}")
    
    print("\n[TEST] Get composite signal...")
    signal = engine.get_composite_signal()
    print(f"VIX Level: {signal['vix']['level']}")
    print(f"VIX Regime: {signal['vix']['regime']}")
    print(f"Risk Adjustment: {signal['risk_adjustment']}")
    print(f"Recommendation: {signal['recommendation']}")
    
    print("\n--- SELF-TEST COMPLETE ---")
