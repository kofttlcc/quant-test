"""
ddm_model.py - 股利折現模型 (Dividend Discount Model)
=======================================================
版本: v1.0
功能: DDM 估值計算，支持 Gordon Growth 和 Two-Stage DDM
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DDMResult:
    """DDM 估值結果"""
    model: str
    intrinsic_value: float
    current_price: float
    margin_of_safety: float
    dividend: float
    cost_of_equity: float
    growth_rate: float
    confidence: str


class DDMValuation:
    """
    股利折現模型估值器
    
    支持:
    - Gordon Growth Model (永續成長)
    - Two-Stage DDM (兩階段成長)
    """
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self._dividend = None
        self._price = None
        self._beta = None
    
    def _fetch_data(self):
        """獲取股利和價格數據"""
        try:
            import yfinance as yf
            stock = yf.Ticker(self.ticker)
            
            # 獲取股利
            info = stock.info
            self._dividend = info.get('dividendRate', 0.0) or 0.0
            self._price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
            self._beta = info.get('beta', 1.0) or 1.0
            
        except Exception as e:
            logger.warning(f"Failed to fetch data for {self.ticker}: {e}")
            self._dividend = 0.0
            self._price = 100.0
            self._beta = 1.0
    
    def calculate_cost_of_equity(
        self, 
        risk_free_rate: float = None,
        market_premium: float = 0.05
    ) -> float:
        """
        使用 CAPM 計算權益成本
        
        Args:
            risk_free_rate: 無風險利率 (e.g., 10年國債)
            market_premium: 市場風險溢酬
        
        Returns:
            權益成本 (Cost of Equity)
        """
        if self._beta is None:
            self._fetch_data()
        
        if risk_free_rate is None:
             # Try to dynamic fetch or default to 4.2%
             try:
                 import yfinance as yf
                 tnx = yf.Ticker("^TNX")
                 hist = tnx.history(period="1d")
                 risk_free_rate = float(hist.iloc[-1]['Close']) / 100 if not hist.empty else 0.042
             except:
                 risk_free_rate = 0.042

        return risk_free_rate + self._beta * market_premium
    
    def gordon_growth(
        self,
        growth_rate: float = 0.03,
        cost_of_equity: float = None
    ) -> DDMResult:
        """
        Gordon Growth Model (永續成長模型)
        
        公式: P = D1 / (r - g)
        
        Args:
            growth_rate: 股利永續成長率
            cost_of_equity: 權益成本 (可選，自動計算)
        
        Returns:
            DDM 估值結果
        """
        if self._dividend is None:
            self._fetch_data()
        
        if cost_of_equity is None:
            cost_of_equity = self.calculate_cost_of_equity()
        
        # 檢查是否為股利股
        if self._dividend <= 0:
            return DDMResult(
                model="Gordon Growth",
                intrinsic_value=0.0,
                current_price=self._price,
                margin_of_safety=0.0,
                dividend=0.0,
                cost_of_equity=cost_of_equity,
                growth_rate=growth_rate,
                confidence="N/A - No Dividend"
            )
        
        # 避免分母為零或負數
        if cost_of_equity <= growth_rate:
            return DDMResult(
                model="Gordon Growth",
                intrinsic_value=0.0,
                current_price=self._price,
                margin_of_safety=0.0,
                dividend=self._dividend,
                cost_of_equity=cost_of_equity,
                growth_rate=growth_rate,
                confidence="Invalid - r <= g"
            )
        
        # 計算明年股利
        d1 = self._dividend * (1 + growth_rate)
        
        # Gordon Growth 公式
        intrinsic_value = d1 / (cost_of_equity - growth_rate)
        
        # 安全邊際
        margin = (intrinsic_value - self._price) / self._price if self._price > 0 else 0
        
        # 置信度評估
        confidence = "HIGH" if margin > 0.2 else ("MEDIUM" if margin > 0 else "LOW")
        
        return DDMResult(
            model="Gordon Growth",
            intrinsic_value=round(intrinsic_value, 2),
            current_price=round(self._price, 2),
            margin_of_safety=round(margin, 4),
            dividend=round(self._dividend, 2),
            cost_of_equity=round(cost_of_equity, 4),
            growth_rate=growth_rate,
            confidence=confidence
        )
    
    def two_stage_ddm(
        self,
        high_growth_rate: float = 0.08,
        high_growth_years: int = 5,
        terminal_growth_rate: float = 0.03,
        cost_of_equity: float = None
    ) -> DDMResult:
        """
        Two-Stage DDM (兩階段成長模型)
        
        階段1: 高速成長期
        階段2: 永續穩定成長期
        
        Args:
            high_growth_rate: 高成長階段成長率
            high_growth_years: 高成長年數
            terminal_growth_rate: 終值成長率
            cost_of_equity: 權益成本
        
        Returns:
            DDM 估值結果
        """
        if self._dividend is None:
            self._fetch_data()
        
        if cost_of_equity is None:
            cost_of_equity = self.calculate_cost_of_equity()
        
        if self._dividend <= 0:
            return DDMResult(
                model="Two-Stage DDM",
                intrinsic_value=0.0,
                current_price=self._price,
                margin_of_safety=0.0,
                dividend=0.0,
                cost_of_equity=cost_of_equity,
                growth_rate=terminal_growth_rate,
                confidence="N/A - No Dividend"
            )
        
        # 階段1: 高成長期股利現值
        pv_high_growth = 0.0
        dividend = self._dividend
        
        for year in range(1, high_growth_years + 1):
            dividend *= (1 + high_growth_rate)
            pv_high_growth += dividend / ((1 + cost_of_equity) ** year)
        
        # 階段2: 終值
        terminal_dividend = dividend * (1 + terminal_growth_rate)
        
        if cost_of_equity <= terminal_growth_rate:
            terminal_value = 0.0
        else:
            terminal_value = terminal_dividend / (cost_of_equity - terminal_growth_rate)
        
        terminal_pv = terminal_value / ((1 + cost_of_equity) ** high_growth_years)
        
        intrinsic_value = pv_high_growth + terminal_pv
        margin = (intrinsic_value - self._price) / self._price if self._price > 0 else 0
        confidence = "HIGH" if margin > 0.2 else ("MEDIUM" if margin > 0 else "LOW")
        
        return DDMResult(
            model="Two-Stage DDM",
            intrinsic_value=round(intrinsic_value, 2),
            current_price=round(self._price, 2),
            margin_of_safety=round(margin, 4),
            dividend=round(self._dividend, 2),
            cost_of_equity=round(cost_of_equity, 4),
            growth_rate=terminal_growth_rate,
            confidence=confidence
        )


def calculate_ddm(
    ticker: str,
    model: str = "gordon",
    growth_rate: float = 0.03
) -> Dict[str, Any]:
    """
    便捷函數: 計算 DDM 估值
    
    Args:
        ticker: 股票代碼
        model: "gordon" 或 "two_stage"
        growth_rate: 成長率
    
    Returns:
        估值結果字典
    """
    ddm = DDMValuation(ticker)
    
    if model == "two_stage":
        result = ddm.two_stage_ddm(terminal_growth_rate=growth_rate)
    else:
        result = ddm.gordon_growth(growth_rate=growth_rate)
    
    return asdict(result)


if __name__ == "__main__":
    print("--- SELF-TEST: ddm_model.py ---")
    
    # 測試 JNJ (高股利股)
    ticker = "JNJ"
    
    print(f"\n[TEST] Gordon Growth Model for {ticker}")
    result = calculate_ddm(ticker, "gordon", 0.03)
    print(f"  當前價格: ${result['current_price']}")
    print(f"  股利: ${result['dividend']}")
    print(f"  內在價值: ${result['intrinsic_value']}")
    print(f"  安全邊際: {result['margin_of_safety']*100:.1f}%")
    print(f"  置信度: {result['confidence']}")
    
    print(f"\n[TEST] Two-Stage DDM for {ticker}")
    result = calculate_ddm(ticker, "two_stage", 0.025)
    print(f"  內在價值: ${result['intrinsic_value']}")
    print(f"  安全邊際: {result['margin_of_safety']*100:.1f}%")
    
    # 測試 AAPL (低股利股)
    print(f"\n[TEST] DDM for AAPL (low dividend)")
    result = calculate_ddm("AAPL", "gordon", 0.03)
    print(f"  股利: ${result['dividend']}")
    print(f"  置信度: {result['confidence']}")
    
    print("\n--- SELF-TEST COMPLETE ---")
