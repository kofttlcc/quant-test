"""
wacc_calculator.py - 動態加權平均資本成本計算器
===================================================
功能: 
1. 使用 CAPM 模型計算權益成本 (Cost of Equity)
2. 計算稅後債務成本 (After-tax Cost of Debt)
3. 綜合計算 WACC
"""

import logging
from typing import Dict, Optional
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WACCCalculator:
    def __init__(self, ticker: str, info: Optional[Dict] = None):
        self.ticker = ticker
        self.info = info or {}
        
        # Defaults
        self.market_premium = 0.05  # 市場風險溢酬 (5%)
        self.risk_free_rate_default = 0.042 # 默認無風險利率 (4.2%)
        
    def _get_risk_free_rate(self) -> float:
        """獲取無風險利率 (10年期美債收益率)"""
        try:
            # 嘗試獲取實時數據
            tnx = yf.Ticker("^TNX")
            hist = tnx.history(period="1d")
            if not hist.empty:
                # Yahoo Finance 返回的是百分比 (e.g., 4.2), 需要除以 100
                return float(hist.iloc[-1]['Close']) / 100
        except Exception as e:
            logger.warning(f"Failed to fetch ^TNX, using default: {e}")
            
        return self.risk_free_rate_default

    def calculate(self) -> float:
        """執行 WACC 計算"""
        if not self.info:
             try:
                self.info = yf.Ticker(self.ticker).info
             except Exception:
                return 0.08 # Fallback

        # 1. Cost of Equity (CAPM)
        # Re = Rf + Beta * (Rm - Rf)
        rf = self._get_risk_free_rate()
        beta = self.info.get('beta', 1.0)
        
        # 校正 Beta: 避免數據缺失或極端值
        if beta is None or beta < 0.1: beta = 1.0
        
        cost_of_equity = rf + beta * self.market_premium
        
        # 2. Cost of Debt (Rd)
        # Rd = Interest Expense / Total Debt
        # 但 yfinance info 通常不直接提供 Interest Expense，我們可以用 financialCurrency 估算
        # 或者簡單使用 defaults based on credit rating logic (simplified here)
        
        # 簡易估計: 無風險利率 + 信用利差 (2%)
        pre_tax_cost_of_debt = rf + 0.02 
        
        # 稅率
        tax_rate = 0.21 # US Corporate Tax Rate assumption
        after_tax_cost_of_debt = pre_tax_cost_of_debt * (1 - tax_rate)
        
        # 3. Capital Structure
        market_cap = self.info.get('marketCap', 0)
        total_debt = self.info.get('totalDebt', 0)
        
        if market_cap == 0 and total_debt == 0:
            return 0.08 # Fallback
            
        total_value = market_cap + total_debt
        weight_equity = market_cap / total_value
        weight_debt = total_debt / total_value
        
        wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)
        
        # Safety Guards
        wacc = max(0.05, min(0.15, wacc)) # Clamp between 5% and 15%
        
        logger.info(f"[{self.ticker}] Dynamic WACC: {wacc:.2%} (Beta={beta:.2f}, Rf={rf:.2%}, We={weight_equity:.2f}, Wd={weight_debt:.2f})")
        
        return wacc

if __name__ == "__main__":
    w = WACCCalculator("AAPL")
    print(f"AAPL WACC: {w.calculate():.2%}")
