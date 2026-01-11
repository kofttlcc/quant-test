"""
strategy_enhancements.py - 策略增強模組
=========================================
版本: v2.0 (Phase 2 Sprint 1)
功能:
1. 追蹤止損 (Trailing Stop Loss)
2. 滑點模型 (Slippage Model)
3. 波動率調倉 (Volatility Scaling)
4. RSI 反轉策略

移植自: old-system/strategies_enhanced.py
"""

import numpy as np
import pandas as pd
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_stop_loss(
    signal: pd.Series,
    prices: pd.Series,
    stop_loss_pct: float = 0.05
) -> pd.Series:
    """
    應用追蹤止損
    
    當從持倉以來的回撤超過止損線時，平倉
    
    Args:
        signal: 交易信號序列 (1=多, -1=空, 0=空倉)
        prices: 價格序列
        stop_loss_pct: 止損百分比 (默認 5%)
        
    Returns:
        調整後的信號序列
    """
    adjusted_signal = signal.copy()
    
    entry_price = None
    high_since_entry = None
    
    for i in range(1, len(signal)):
        current_sig = signal.iloc[i]
        prev_sig = signal.iloc[i-1]
        
        # 新開倉
        if current_sig != 0 and prev_sig == 0:
            entry_price = prices.iloc[i]
            high_since_entry = prices.iloc[i]
        
        # 持倉中
        elif current_sig != 0 and prev_sig != 0 and entry_price is not None:
            # 做多時
            if current_sig > 0:
                high_since_entry = max(high_since_entry, prices.iloc[i])
                drawdown = (high_since_entry - prices.iloc[i]) / high_since_entry
                if drawdown > stop_loss_pct:
                    adjusted_signal.iloc[i] = 0
                    entry_price = None
                    logger.debug(f"Stop loss triggered at index {i}, drawdown: {drawdown:.2%}")
            # 做空時
            elif current_sig < 0:
                low_since_entry = min(high_since_entry, prices.iloc[i])
                runup = (prices.iloc[i] - low_since_entry) / low_since_entry
                if runup > stop_loss_pct:
                    adjusted_signal.iloc[i] = 0
                    entry_price = None
        
        # 平倉
        elif current_sig == 0:
            entry_price = None
            high_since_entry = None
    
    return adjusted_signal


def apply_slippage(
    signal: pd.Series,
    returns: pd.Series,
    volume: Optional[pd.Series] = None,
    order_pct: float = 0.01,
    base_slippage_bps: float = 5.0
) -> pd.Series:
    """
    應用滑點模型 (Market Impact Model)
    
    使用平方根法則估計衝擊成本:
    滑點 = base_bps * sqrt(order_volume / avg_volume)
    
    Args:
        signal: 交易信號
        returns: 毛收益序列
        volume: 成交量序列 (可選)
        order_pct: 訂單佔成交量比例
        base_slippage_bps: 基礎滑點 (基點)
        
    Returns:
        扣除滑點後的淨收益
    """
    slippage_rate = base_slippage_bps / 10000.0
    
    if volume is not None and len(volume) > 20:
        avg_volume = volume.rolling(20).mean()
        impact_multiplier = np.sqrt(order_pct * volume / (avg_volume + 1))
        slippage = slippage_rate * impact_multiplier.clip(0.5, 3.0)
    else:
        slippage = slippage_rate
    
    turnover = signal.diff().abs().fillna(0)
    slippage_cost = turnover * slippage
    
    return returns - slippage_cost


def apply_volatility_scaling(
    signal: pd.Series,
    returns: pd.Series,
    target_vol: float = 0.15,
    window: int = 20
) -> pd.Series:
    """
    根據波動率調整倉位 (Volatility Targeting)
    
    倉位 = target_vol / realized_vol
    
    Args:
        signal: 交易信號
        returns: 收益序列
        target_vol: 目標年化波動率
        window: 計算波動率的窗口
        
    Returns:
        調整後的信號
    """
    realized_vol = returns.rolling(window).std() * np.sqrt(252)
    leverage = (target_vol / (realized_vol + 1e-8)).clip(0.5, 1.5)
    adjusted_signal = signal * leverage.shift(1)  # shift(1) 避免前視偏差
    
    return adjusted_signal


class RSIReversionStrategy:
    """
    RSI 反轉策略
    
    邏輯:
    - RSI < lower (超賣) -> 做多
    - RSI > upper (超買) -> 做空/平倉
    """
    
    def __init__(self, rsi_period: int = 14, rsi_lower: int = 30, rsi_upper: int = 70):
        self.rsi_period = rsi_period
        self.rsi_lower = rsi_lower
        self.rsi_upper = rsi_upper
        
    def _calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """計算 RSI"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號
        
        Args:
            df: 包含 'Close' 列的 DataFrame
            
        Returns:
            帶有 Signal 和 Position 列的 DataFrame
        """
        if df.empty or 'Close' not in df.columns:
            return df
            
        strat_df = df.copy()
        strat_df['RSI'] = self._calculate_rsi(strat_df['Close'])
        
        # 信號生成
        strat_df['Signal'] = 0
        strat_df.loc[strat_df['RSI'] < self.rsi_lower, 'Signal'] = 1  # 超賣買入
        strat_df.loc[strat_df['RSI'] > self.rsi_upper, 'Signal'] = -1  # 超買賣出
        
        # 持倉 (前向填充)
        strat_df['Position'] = np.nan
        strat_df.loc[strat_df['Signal'] == 1, 'Position'] = 1.0
        strat_df.loc[strat_df['Signal'] == -1, 'Position'] = 0.0
        strat_df['Position'] = strat_df['Position'].ffill().fillna(0.0)
        
        return strat_df[['Close', 'RSI', 'Signal', 'Position']]


if __name__ == "__main__":
    print("--- SELF-TEST: strategy_enhancements.py ---")
    
    # 測試數據
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 0.5)
    df = pd.DataFrame({'Close': prices})
    
    # 測試 RSI 策略
    print("\n[TEST] RSI Reversion Strategy")
    rsi_strat = RSIReversionStrategy(rsi_period=10, rsi_lower=30, rsi_upper=70)
    result = rsi_strat.generate_signals(df)
    print(f"RSI Range: {result['RSI'].min():.1f} - {result['RSI'].max():.1f}")
    print(f"Buy Signals: {(result['Signal'] == 1).sum()}")
    print(f"Sell Signals: {(result['Signal'] == -1).sum()}")
    
    # 測試止損
    print("\n[TEST] Stop Loss")
    signal = pd.Series([0, 1, 1, 1, 1, 1, 0])
    test_prices = pd.Series([100, 100, 105, 110, 95, 90, 90])  # 從110跌到90，>10%回撤
    adjusted = apply_stop_loss(signal, test_prices, stop_loss_pct=0.10)
    print(f"Original signal: {signal.tolist()}")
    print(f"Adjusted signal: {adjusted.tolist()}")
    
    print("\n--- SELF-TEST COMPLETE ---")
