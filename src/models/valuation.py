"""
valuation.py - 內在價值計算平台 (Phase 7.0)
===================================================
移植自 old-system/valuation_enhanced.py
適配 Phase 6.5 CacheManager 基礎設施。
"""

import numpy as np
import pandas as pd
import yfinance as yf
import requests
from dataclasses import dataclass
from typing import Dict, Optional, List, Tuple
import logging
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    from src.data_loader.cache_manager import CacheManager
    from src.models.sentiment_engine import SentimentEngine
    from src.models.ddm_model import DDMValuation
    from src.models.wacc_calculator import WACCCalculator
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class IndustryData:
    """行業基準數據 (Industry Benchmark Data)"""
    sector: str
    industry: str
    median_pe: float
    median_pb: float
    wacc_range: Tuple[float, float]  # (min, max)
    growth_range: Tuple[float, float]
    terminal_growth: float

# Simplified Industry Benchmarks (Ported subset)
INDUSTRY_BENCHMARKS: Dict[str, IndustryData] = {
    "Technology": IndustryData("Technology", "Software", 28.0, 6.0, (0.08, 0.12), (0.10, 0.25), 0.03),
    "Healthcare": IndustryData("Healthcare", "Pharma", 22.0, 4.0, (0.07, 0.10), (0.05, 0.15), 0.025),
    "Financial Services": IndustryData("Financial Services", "Banks", 12.0, 1.2, (0.08, 0.11), (0.03, 0.08), 0.02),
    "default": IndustryData("Unknown", "Unknown", 20.0, 3.0, (0.08, 0.11), (0.05, 0.10), 0.025)
}

@dataclass
class ValuationResult:
    """估值結果對象 (Valuation Result Object)"""
    ticker: str
    company_name: str
    current_price: float
    fair_value: float
    margin_of_safety: float
    status: str
    models: Dict[str, float]
    details: Dict
    data_quality: str = "High"  # New field for Audit Protocol


# MEM-003 FIX: CacheManager 單例
_cache_manager_instance = None

def get_cache_manager():
    """獲取共享的 CacheManager 實例"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()
    return _cache_manager_instance


class ValuationEngine:
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.cache = get_cache_manager()  # MEM-003 FIX: 使用共享實例
        self.pipeline_financials = pd.DataFrame() # To be loaded
        self.info = {}
        
    def _fetch_data(self) -> bool:
        """從緩存或 yfinance 加載數據 (Load data from Cache and yfinance)"""
        try:
            # 1. Ticker Info (Live/Cache)
            t = yf.Ticker(self.ticker)
            self.info = t.info
            
            # 2. Financials from Cache (Phase 6.5)
            self.pipeline_financials = self.cache.load_financials(self.ticker)
            
            # Fallback if cache empty? Try fetch
            if self.pipeline_financials.empty:
                logger.info(f"Financials cache miss for {self.ticker}. Fetching...")
                from src.data_loader.downloader import fetch_financials
                fetch_financials(self.ticker)
                self.pipeline_financials = self.cache.load_financials(self.ticker)
                
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching data: {e}")
            return False
        except ValueError as e:
            logger.error(f"Data parsing error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in _fetch_data: {e}")
            return False

    def _get_ttm_metric(self, metric_name: str) -> float:
        """從已加載的財務數據中獲取 TTM (近12個月) 指標值 (Get TTM value)"""
        if self.pipeline_financials.empty:
            return 0.0
            
        # 1. Try 'metric' column (Long Format)
        if 'metric' in self.pipeline_financials.columns:
            df_metric = self.pipeline_financials[self.pipeline_financials['metric'] == metric_name]
            if not df_metric.empty:
                df_metric = df_metric.sort_values(by='date', ascending=False)
                return float(df_metric.iloc[0]['value'])
                
        # 2. Try Index lookup (Wide Format - yfinance default)
        # yfinance columns are Dates. We need to find the latest date.
        if metric_name in self.pipeline_financials.index:
            try:
                row = self.pipeline_financials.loc[metric_name]
                # If row is a Series (one row), its index are dates.
                # Sort dates descending to get latest
                if isinstance(row, pd.Series):
                    # Sort index (dates) desc
                    row_sorted = row.sort_index(ascending=False)
                    # Get first non-NaN value
                    for val in row_sorted:
                         if pd.notna(val):
                             return float(val)
                elif isinstance(row, pd.DataFrame):
                    # Duplicate index case? Take first
                    return float(row.iloc[0, 0]) # Crude fallback
            except Exception as e:
                logger.error(f"Error extracting metric {metric_name}: {e}")
                
        return 0.0

    def calculate_dcf(self, wacc=0.09, growth_rate=0.08, terminal_growth=0.025) -> Optional[float]:
        """現金流折現模型 (Discounted Cash Flow Model)"""
        fcf = self._get_ttm_metric('Free Cash Flow')
        if not fcf or fcf <= 0:
            # Fallback to Net Income + D&A ?
            fcf = self.info.get('freeCashflow', 0)
        
        if not fcf or fcf <= 0:
            return None
            
        shares = self.info.get('sharesOutstanding', 1)
        net_debt = self.info.get('totalDebt', 0) - self.info.get('totalCash', 0)
        
        # Projection (5 Years)
        future_fcf = []
        current_fcf = fcf
        
        for i in range(1, 6):
            current_fcf = current_fcf * (1 + growth_rate)
            future_fcf.append(current_fcf / ((1 + wacc) ** i))
            
        # Terminal Value
        # MAJOR-004 FIX (Enhanced): 防止除零和異常終值
        spread = wacc - terminal_growth
        
        # 多層保護
        if spread <= 0:
            logger.error(f"WACC ({wacc:.2%}) <= Terminal Growth ({terminal_growth:.2%}). Invalid DCF parameters.")
            return None  # 返回 None 而非計算錯誤值
        
        if spread < 0.02:
            logger.warning(f"WACC-Growth spread ({spread:.2%}) too narrow. Clamping to 2% minimum.")
            spread = 0.02
        
        tv = (current_fcf * (1 + terminal_growth)) / spread
        tv_pv = tv / ((1 + wacc) ** 5)
        
        ev = sum(future_fcf) + tv_pv
        equity_val = ev - net_debt
        
        return equity_val / shares if shares > 0 else None

    def calculate_graham(self) -> Optional[float]:
        """葛拉漢數 / 公式 (Graham Number / Formula)"""
        eps = self.info.get('trailingEps', 0)
        bvps = self.info.get('bookValue', 0)
        
        if eps > 0 and bvps > 0:
            # Graham Number = Sqrt(22.5 * EPS * BVPS)
            return np.sqrt(22.5 * eps * bvps)
        return None

    def assess_value(self) -> ValuationResult:
        data_quality = "High"
        
        if not self._fetch_data():
             # Return empty result
             return ValuationResult(self.ticker, "Unknown", 0, 0, 0, "Error", {}, {}, data_quality="Critical")
             
        current_price = self.info.get('currentPrice', 0)
        if current_price == 0:
             # Fast info fallback
             t = yf.Ticker(self.ticker)
             current_price = t.fast_info.get('last_price', 0)
             
        # DCF Params
        sector = self.info.get('sector', 'default')
        bench = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['default'])
        
        # MAJOR-005 FIX: Dynamic WACC Calculation (Plan A)
        try:
            wacc_calc = WACCCalculator(self.ticker, self.info)
            wacc = wacc_calc.calculate()
        except Exception as e:
            logger.error(f"Dynamic WACC failed: {e}, using fallback.")
            wacc = 0.08
            data_quality = "Medium" # WACC Fallback

        # MAJOR-002 FIX: Growth Rate Estimation - Enhanced Logic
        # Strategy: Prioritize Analyst Estimates > Earnings Growth > Revenue Growth > Benchmark
        raw_growth = self.info.get('earningsGrowth')
        rev_growth = self.info.get('revenueGrowth')
        
        est_growth = 0.05 # Default
        
        if raw_growth is not None and isinstance(raw_growth, (int, float)):
             # Sanity check with Revenue Growth (earnings shouldn't vastly outpace revenue forever)
             if rev_growth is not None and raw_growth > rev_growth * 2 and rev_growth > 0:
                 logger.info(f"[{self.ticker}] Capping Earnings Growth ({raw_growth:.1%}) to 1.5x Revenue Growth ({rev_growth:.1%})")
                 est_growth = rev_growth * 1.5
             else:
                 est_growth = raw_growth
        else:
             # Fallback to sector benchmark
             est_growth = sum(bench.growth_range) / 2
             data_quality = "Medium" # Growth Fallback
             
        # Intelligent Clamping (Relaxed for High Growth, tightened for negative)
        # Allow up to 30% for high momentum, but decay is handled in DCF model implicitly by limited projection period
        if est_growth > 0.30:
            logger.warning(f"[{self.ticker}] Growth {est_growth:.1%} clamped to 30%")
            est_growth = 0.30
        elif est_growth < -0.15:
             logger.warning(f"[{self.ticker}] Growth {est_growth:.1%} clamped to -15%")
             est_growth = -0.15
             
        # 調試日誌
        logger.info(f"[{self.ticker}] DCF params: WACC={wacc:.1%}, Growth={est_growth:.1%}, Terminal={bench.terminal_growth:.1%}")
        
        # Models
        dcf = self.calculate_dcf(wacc=wacc, growth_rate=est_growth, terminal_growth=bench.terminal_growth)
        if dcf is None:
             # If DCF fails completely (e.g., negative FCF), degrade quality
             data_quality = "Low"
             
        graham = self.calculate_graham()
        
        # DDM Integration
        try:
            ddm_engine = DDMValuation(self.ticker)
            # Use same growth rate as DCF for consistency, or default DDM logic
            ddm_res = ddm_engine.gordon_growth(growth_rate=bench.terminal_growth) # 使用終值成長率作為永續成長率
            ddm_val = ddm_res.intrinsic_value
        except Exception as e:
            logger.warning(f"DDM Calculation failed: {e}")
            ddm_val = None
        
        # ===== 行業加權機制 =====
        # 解決 DCF vs Graham 分歧過大的問題
        # 科技股: 成長導向，DCF 權重高
        # 金融股: 資產導向，Graham 權重高
        sector_weights = {
            "Technology": {"DCF": 0.70, "Graham": 0.30},
            "Communication Services": {"DCF": 0.65, "Graham": 0.35},
            "Healthcare": {"DCF": 0.60, "Graham": 0.40},
            "Financial Services": {"DCF": 0.35, "Graham": 0.65},
            "Real Estate": {"DCF": 0.30, "Graham": 0.70},
            "default": {"DCF": 0.50, "Graham": 0.50}
        }
        
        weights = sector_weights.get(sector, sector_weights["default"])
        
        # Composite Weighted
        values = []
        model_res = {}
        weighted_sum = 0
        weight_total = 0
        
        if dcf and dcf > 0:
            model_res['DCF'] = round(dcf, 2)
            weighted_sum += dcf * weights["DCF"]
            weight_total += weights["DCF"]
            values.append(("DCF", dcf, weights["DCF"]))
            
        if graham and graham > 0:
            model_res['Graham'] = round(graham, 2)
            weighted_sum += graham * weights["Graham"]
            weight_total += weights["Graham"]
            values.append(("Graham", graham, weights["Graham"]))
            
        if ddm_val and ddm_val > 0:
            model_res['DDM'] = round(ddm_val, 2)
            # DDM 目前僅作參考，暫不計入加權平均，以免無股息股票拉低估值
            # 如需計入，需調整 sector_weights 邏輯
            
        if weight_total == 0:
            return ValuationResult(self.ticker, self.info.get('shortName', 'Unknown'), current_price, current_price, 0, "Unknown", {}, {}, data_quality="Low")
        
        # 加權公允價值
        fair_value = weighted_sum / weight_total
        margin = (fair_value - current_price) / fair_value if fair_value > 0 else 0
        
        # 計算置信區間 (模型間分歧)
        if len(values) >= 2:
            model_values = [v[1] for v in values]
            value_range = max(model_values) - min(model_values)
            divergence_pct = value_range / fair_value if fair_value > 0 else 0
            
            # Confidence Logic
            if divergence_pct < 0.3:
                 confidence = "High" 
            elif divergence_pct < 0.5:
                 confidence = "Medium"
            else:
                 confidence = "Low"
                 data_quality = "Low" # Divergence implies data/model mismatch
        else:
            divergence_pct = 0
            confidence = "Single Model"
        
        if margin > 0.3: status = "Undervalued (Strong)"
        elif margin > 0.1: status = "Undervalued"
        elif margin < -0.2: status = "Overvalued"
        else: status = "Fair Value"
        
        return ValuationResult(
            ticker=self.ticker,
            company_name=self.info.get('longName') or self.info.get('shortName') or self.ticker,
            current_price=current_price,
            fair_value=round(fair_value, 2),
            margin_of_safety=margin,
            status=status,
            models=model_res,
            details={
                "WACC": f"{wacc:.1%}",
                "Growth": f"{est_growth:.1%}",
                "Sector": sector,
                "Weights": f"DCF {weights['DCF']:.0%} / Graham {weights['Graham']:.0%}",
                "Confidence": confidence,
                "Divergence": f"{divergence_pct:.1%}"
            },
            data_quality=data_quality
        )

if __name__ == "__main__":
    v = ValuationEngine("AAPL")
    res = v.assess_value()
    print(res)
