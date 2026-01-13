"""
stat_arb/engine.py - 統計套利核心引擎
=========================================
功能:
1. 協整測試 (Engle-Granger Cointegration Test)
2. 價差計算 (Spread Calculation)
3. Z-Score 信號生成

Skill: quant-stat-arb
"""

import numpy as np
import pandas as pd
import logging
from typing import Tuple, Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import coint
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger.warning("statsmodels not found. Using simplified Hurst Exponent fallback.")

class StatArbEngine:
    """
    統計套利引擎
    由 Pairs Trading (配對交易) 邏輯驅動
    """
    
    def __init__(self, p_value_threshold: float = 0.05, z_entry: float = 2.0, z_exit: float = 0.5):
        """
        Args:
            p_value_threshold: 協整測試顯著性閾值 (默認 0.05)
            z_entry: 開倉 Z-Score 閾值 (默認 2.0)
            z_exit: 平倉 Z-Score 閾值 (默認 0.5 - 回歸均值)
        """
        self.p_value_threshold = p_value_threshold
        self.z_entry = z_entry
        self.z_exit = z_exit
        
    def _calculate_hurst(self, ts: np.array) -> float:
        """計算 Hurst Exponent (簡化版)"""
        lags = range(2, 20)
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0] * 2.0

    def calculate_ou_params(self, spread: pd.Series) -> Dict[str, float]:
        """
        [MED-003] 計算 OU 過程參數與半衰期
        d(Spread) = theta * (mu - Spread) * dt + sigma * dW
        """
        if len(spread) < 10:
             return {"theta": 0, "mu": 0, "sigma": 0, "half_life": np.inf}
             
        # 回歸: S(t) - S(t-1) vs S(t-1)
        # dx = S(t) - S(t-1)
        # x = S(t-1)
        # dx = theta*mu*dt - theta*dt * x
        # linear reg: dx = alpha + beta * x
        # theta = -beta / dt (assume dt=1)
        # mu = alpha / (theta * dt) = alpha / -beta
        
        spread_np = spread.values
        x = spread_np[:-1]
        dx = spread_np[1:] - x
        
        alpha, beta = np.polyfit(x, dx, 1)
        
        theta = -beta
        if theta <= 1e-8: # Mean reverting speed too slow
             half_life = np.inf
        else:
             half_life = np.log(2) / theta
        
        mu = alpha / theta if theta > 1e-8 else 0
        sigma = np.std(dx - (alpha + beta * x))
        
        return {
            "theta": theta,
            "mu": mu,
            "sigma": sigma,
            "half_life": half_life
        }

    def test_cointegration(self, series_x: pd.Series, series_y: pd.Series) -> Tuple[bool, float, float]:
        """
        執行 Engle-Granger 兩步協整測試
        
        或者直接使用 statsmodels.tsa.stattools.coint
        Fallback: 使用簡單的線性回歸 + Hurst 指數判斷殘差平穩性
        
        Returns:
            (is_cointegrated, p_value, hedge_ratio)
        """
        # 對齊數據
        df = pd.concat([series_x, series_y], axis=1).dropna()
        if df.shape[0] < 50:
             return False, 1.0, 0.0
            
        x = df.iloc[:, 0].values
        y = df.iloc[:, 1].values
        
        # Calculate Hedge Ratio (Beta) using Numpy OLS
        # y = beta * x + c
        A = np.vstack([x, np.ones(len(x))]).T
        beta, c = np.linalg.lstsq(A, y, rcond=None)[0]
        
        if STATSMODELS_AVAILABLE:
            try:
                # 1. 使用 statsmodels coint
                score, p_value, _ = coint(y, x)
                is_coint = p_value < self.p_value_threshold
                return is_coint, p_value, beta
            except Exception as e:
                logger.warning(f"Statsmodels error: {e}, falling back.")
        
        # Fallback Logic: Check Mean Reversion of Spread using Hurst
        spread = y - beta * x
        hurst = self._calculate_hurst(spread)
        
        # Hurst < 0.5 implies mean reverting
        # p-value is faked as Hurst for API consistency
        is_mean_reverting = hurst < 0.5
        
        return is_mean_reverting, hurst, beta

    def calculate_spread(self, series_x: pd.Series, series_y: pd.Series, hedge_ratio: float) -> pd.Series:
        """
        計算價差: Spread = Y - HedgeRatio * X
        注意: 這是一個簡化的價差定義，實際可能包含截距或 log 價格
        """
        return series_y - hedge_ratio * series_x

    def generate_signals(self, spread: pd.Series) -> pd.DataFrame:
        """
        基於 Spread 的 Z-Score 生成交易信號
        
        Returns:
            DataFrame with columns: [Spread, ZScore, Signal X, Signal Y]
            Signal: 1 (Long), -1 (Short), 0 (Flat)
        """
        # 使用滾動窗口計算 Z-Score (避免前視偏差)
        # Window size 應該與半衰期 (Half-life) 相關，這裡默認 60
        window = 60
        
        mean = spread.rolling(window=window).mean()
        std = spread.rolling(window=window).std()
        
        z_score = (spread - mean) / std
        
        # [MED-003] 計算並報告半衰期
        ou_params = self.calculate_ou_params(spread.dropna())
        hl = ou_params.get("half_life", np.inf)
        if hl > 50 or hl < 1:
             logger.warning(f"[MED-003] Spread Half-Life {hl:.2f} is outside ideal range (1-50 days).")
        
        # 信號邏輯
        # 當 Spread Z > 2: Spread 過高 -> Short Spread -> Short Y, Long X
        # 當 Spread Z < -2: Spread 過低 -> Long Spread -> Long Y, Short X
        
        signals = pd.DataFrame(index=spread.index)
        signals['Spread'] = spread
        signals['ZScore'] = z_score
        
        # [MED-003] Expose Half-Life for UI
        signals['HalfLife'] = hl
        signals['Theta'] = ou_params.get("theta", 0)
        signals['Sigma'] = ou_params.get("sigma", 0)
        
        # 初始化信號
        signals['Signal_Y'] = 0 # 主動資產
        signals['Signal_X'] = 0 # 對沖資產 (通常相反)
        
        short_spread = z_score > self.z_entry
        long_spread = z_score < -self.z_entry
        exit_cond = z_score.abs() < self.z_exit
        
        # 狀態機式信號生成 (向量化實現較難處理持倉狀態，這裡使用迭代或狀態標記)
        # 簡單起見，這裡生成 raw signals，具體持倉管理交給 Backtester
        
        signals.loc[short_spread, 'Signal_Y'] = -1
        signals.loc[short_spread, 'Signal_X'] = 1
        
        signals.loc[long_spread, 'Signal_Y'] = 1
        signals.loc[long_spread, 'Signal_X'] = -1
        
        # 平倉信號 (Signal = 0) 
        # 注意: 這裡的實現是 instantaneous signal，實際回測需要處理 "保持持倉" 直到 exit
        # 這部分邏輯通常在 Selector 或 Strategy Wrapper 中處理
        
        return signals

if __name__ == "__main__":
    # Self-test
    np.random.seed(42)
    x = np.cumsum(np.random.randn(200)) + 100
    # 構造一個協整序列 Y: Y = 1.5 * X + Noise
    noise = np.random.randn(200) * 0.5
    y = 1.5 * x + noise + 10
    
    s_x = pd.Series(x, name='X')
    s_y = pd.Series(y, name='Y')
    
    engine = StatArbEngine()
    is_coint, p_val, beta = engine.test_cointegration(s_x, s_y)
    
    print(f"Cointegration Test: {is_coint} (p={p_val:.4f})")
    print(f"Hedge Ratio (Beta): {beta:.4f}")
    
    if is_coint:
        spread = engine.calculate_spread(s_x, s_y, beta)
        sigs = engine.generate_signals(spread)
        print("\nSignals Head:")
        print(sigs.tail())
