"""
macro_dashboard.py - 宏觀態勢感知模組
=========================================
版本: v2.0 (Phase 2)
功能:
1. VIX 指數獲取與狀態解讀
2. 10Y/2Y Yield Curve
3. 市場廣度 (ADR)
4. 新聞情緒 (News Scanner)
5. **Macro Risk Score** (核心輸出)

數據源: yfinance
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

try:
    from src.models.macro.news_scanner import NewsScanner
except ImportError:
    from news_scanner import NewsScanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MacroSnapshot:
    """宏觀數據快照"""
    # 核心輸出
    risk_score: int          # 0-100 (0=Safe, 100=RiskOff)
    risk_mode: str           # "Risk On", "Neutral", "Risk Off"
    
    # 因子 1: VIX
    vix_value: float
    vix_status: str          # "Low", "Normal", "High", "Extreme"
    vix_score: int           # Component Score
    
    # 因子 2: 利率結構
    yield_10y: float
    yield_2y: float
    yield_spread: float      # bps
    yield_score: int         # Component Score
    
    # 因子 3: 情緒與廣度
    market_breadth: float    # ADR (Advance/Decline Ratio)
    sentiment_score: float   # -1.0 to 1.0
    sentiment_label: str     # "Bullish", "Neutral", "Bearish"
    sentiment_score_comp: int # Component Score
    
    # 元數據
    timestamp: str
    data_quality: str        # "Live", "Mixed", "Simulated"


class MacroDashboard:
    """
    宏觀態勢感知儀表板
    負責計算 Macro_Risk_Score
    """
    
    def __init__(self):
        self._cache: Optional[MacroSnapshot] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=15) # 15 min updates
        self.scanner = NewsScanner()
        
    def get_snapshot(self, force_refresh: bool = False) -> Dict[str, Any]:
        """獲取宏觀數據快照"""
        if not force_refresh and self._cache and self._cache_time:
            if datetime.now() - self._cache_time < self._cache_ttl:
                return asdict(self._cache)
        
        try:
            snapshot = self._fetch_and_calculate()
            self._cache = snapshot
            self._cache_time = datetime.now()
            return asdict(snapshot)
        except Exception as e:
            logger.error(f"Macro fetch failed: {e}")
            import traceback
            traceback.print_exc()
            return asdict(self._generate_fallback_data())

    def _fetch_and_calculate(self) -> MacroSnapshot:
        import yfinance as yf
        
        quality = "Live"
        
        # 1. Fetch VIX
        try:
            vix_t = yf.Ticker("^VIX")
            hist = vix_t.history(period="5d")
            if not hist.empty:
                vix = float(hist['Close'].iloc[-1])
            else:
                vix = 15.0
                quality = "Mixed"
        except:
            vix = 15.0
            quality = "Mixed"
            
        # 2. Fetch Yields
        try:
            tnx = yf.Ticker("^TNX") # 10Y
            irx = yf.Ticker("^IRX") # 13W (Proxy for short term)
            # Or assume 2Y is roughly correlated or fetch US2Y=X if available
            # We stick to TNX and manual 2Y proxy if needed. yfinance often has ^TNX.
            
            y10 = float(tnx.history(period="1d")['Close'].iloc[-1])
            y2 = float(irx.history(period="1d")['Close'].iloc[-1]) # Using IRX as short rate proxy
        except:
            y10, y2 = 4.0, 4.0
            quality = "Mixed"
            
        spread = (y10 - y2) * 100 # bps
        
        # 3. Sentiment
        sent_val, sent_qual = self.scanner.fetch_and_analyze()
        if sent_qual == "Simulated": quality = "Mixed" if quality == "Live" else quality
        
        # 4. Breadth (ADR)
        # Fetching ^ADD (NYSE Adv/Dec Line) usually works
        try:
            add = yf.Ticker("^ADD") # Net Issues? NO, raw count difference?
            # ^ADR is not reliable on YF standard.
            # Using custom estimate or ^VIX relation if fails.
            # Let's try fetching SPY vs RSP (Equal Weight)
            spy = yf.Ticker("SPY").history(period="5d")['Close']
            rsp = yf.Ticker("RSP").history(period="5d")['Close']
            
            spy_perf = (spy.iloc[-1]/spy.iloc[-2]) - 1
            rsp_perf = (rsp.iloc[-1]/rsp.iloc[-2]) - 1
            
            # If Equal weight outperforms, breadth is good.
            # ADR estimation
            breadth = 1.0 + (rsp_perf - spy_perf) * 10 
            breadth = max(0.5, min(1.5, breadth))
        except:
            breadth = 1.0 # Neutral
            
        # --- CALCULATION ENGINE ---
        
        # A. VIX Score (0-100 Risk)
        # 12=Safe, 20=Normal, 30=High
        if vix <= 12: v_score = 0
        elif vix >= 35: v_score = 100
        else: v_score = min(100, (vix - 12) / (35 - 12) * 100)
        
        # B. Yield Score (Inversion Risk)
        # Spread > 10bps = 0 Risk
        # Spread < -50bps = 100 Risk
        if spread > 10: y_score = 0
        elif spread < -50: y_score = 100
        else: y_score = min(100, (10 - spread) / (60) * 100)
        
        # C. Sentiment Score (Risk)
        # +1.0 (Bull) = 0 Risk
        # -1.0 (Bear) = 100 Risk
        s_score = (1.0 - sent_val) / 2.0 * 100
        
        # Weights
        # VIX: 40%, Yield: 30%, Sentiment: 30%
        final_risk = (v_score * 0.4) + (y_score * 0.3) + (s_score * 0.3)
        final_risk = int(final_risk)
        
        mode = "Neutral"
        if final_risk < 30: mode = "Risk On"
        elif final_risk > 75: mode = "Risk Off" # Global Rule > 80 is strictly Risk Off, we set 75 warn
        
        return MacroSnapshot(
            risk_score=final_risk,
            risk_mode=mode,
            vix_value=round(vix, 2),
            vix_status=self._vix_stat(vix),
            vix_score=int(v_score),
            yield_10y=round(y10, 2),
            yield_2y=round(y2, 2),
            yield_spread=round(spread, 0),
            yield_score=int(y_score),
            market_breadth=round(breadth, 2),
            sentiment_score=round(sent_val, 2),
            sentiment_label="Bullish" if sent_val > 0.2 else "Bearish" if sent_val < -0.2 else "Neutral",
            sentiment_score_comp=int(s_score),
            timestamp=datetime.now().isoformat(),
            data_quality=quality
        )
        
    def _vix_stat(self, v):
        if v < 15: return "Low"
        if v < 25: return "Normal"
        return "High"

    def _generate_fallback_data(self):
        return MacroSnapshot(
            risk_score=50,
            risk_mode="Neutral",
            vix_value=20.0, vix_status="Normal", vix_score=50,
            yield_10y=4.0, yield_2y=4.0, yield_spread=0, yield_score=50,
            market_breadth=1.0, sentiment_score=0.0, sentiment_label="Neutral", sentiment_score_comp=50,
            timestamp=datetime.now().isoformat(),
            data_quality="Fallback"
        )

# Global Instance
_dashboard = MacroDashboard()

def get_macro_snapshot(force_refresh=False):
    return _dashboard.get_snapshot(force_refresh)

def get_next_event():
    """主要財經事件 (Mock)"""
    return {
        "event": "FOMC Meeting",
        "date": "2026-01-28",
        "estimate": "Hold",
        "impact": "High"
    }

if __name__ == "__main__":
    print("--- SELF-TEST: macro_dashboard.py (v2) ---")
    s = get_macro_snapshot()
    print(f"Risk Score: {s['risk_score']} ({s['risk_mode']})")
    print(f"Components: VIX={s['vix_value']}, Spread={s['yield_spread']}, Sent={s['sentiment_score']}")
