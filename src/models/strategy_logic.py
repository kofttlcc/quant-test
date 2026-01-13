
import pandas as pd
import numpy as np
import logging
try:
    from src.models.indicators import calculate_rsi, calculate_bollinger
    from src.models.macro.regime_detector import RegimeDetector
except ImportError:
    # Fallback for direct execution
    from indicators import calculate_rsi, calculate_bollinger
    from regime_detector import RegimeDetector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MomentumStrategy:
    """
    Dynamic Momentum Strategy compatible with Phase 1 PRD.
    Logic:
    1. Trend Filter: Price > SMA(50) -> Bullish Bias
    2. Momentum: RSI(14) < 30 (Oversold Buy) or > 70 (Overbought Sell)
    3. Volatility: Reduce size if Volatility > Threshold
    """
    def __init__(self, rsi_period=14, sma_period=50, vol_window=20, window=None):
        self.rsi_period = rsi_period
        # Arena compatibility: 'window' overrides 'sma_period'
        self.sma_period = window if window is not None else sma_period
        self.vol_window = vol_window
        self.regime_detector = RegimeDetector()
        
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate signals: 1 (Buy), -1 (Sell), 0 (Neutral).
        Returns DataFrame with 'Signal' column.
        """
        if df.empty:
            return df
        
        # Ensure we work on a copy
        strat_df = df.copy()
        
        # 1. Calc Indicators
        strat_df['RSI'] = calculate_rsi(strat_df['Close'], self.rsi_period)
        strat_df['SMA'] = strat_df['Close'].rolling(self.sma_period).mean()
        
        # 2. Logic
        # Signal init
        strat_df['Signal'] = 0
        
        # Bullish Regime: Close > SMA
        bullish_mask = strat_df['Close'] > strat_df['SMA']
        
        # Logic: 
        # Buy if Bullish AND RSI < 45 (Aggressive dip buy)
        # Sell if RSI > 75 (Profit Take) OR Trend Break
        
        buy_cond = bullish_mask & (strat_df['RSI'] < 45) 
        sell_cond = (strat_df['RSI'] > 75) | (~bullish_mask) 
        
        strat_df.loc[buy_cond, 'Signal'] = 1
        strat_df.loc[sell_cond, 'Signal'] = -1
        
        # Create Target Position
        strat_df['Position'] = np.nan
        strat_df.loc[strat_df['Signal'] == 1, 'Position'] = 1.0
        strat_df.loc[strat_df['Signal'] == -1, 'Position'] = 0.0
        
        # Forward fill position to hold trades
        strat_df['Position'] = strat_df['Position'].ffill().fillna(0.0)
        
        # [CRIT-002] Fix: Detect non-trading gaps (> 5 days) and reset position
        # Calculate time delta between rows
        if isinstance(strat_df.index, pd.DatetimeIndex):
            time_diff = strat_df.index.to_series().diff()
            # If gap > 5 days (e.g. market closed for week++, or missing data), force exit
            gap_mask = time_diff > pd.Timedelta(days=5)
            if gap_mask.any():
                strat_df.loc[gap_mask, 'Position'] = 0.0
                # Re-ffill zeros if needed? No, we just cut the hold.
                # Actually if we set to 0.0, we are Flat.
                # But we need to ensure we don't hold through the gap.
                # If gap is at index t, it means t is far from t-1.
                # So at t, we should not inherit t-1's position unless reaffirmed.
                # Setting Position at t to 0.0 achieves this.

        
        # 3. Phase 5: Regime Filter (GMM)
        # Phase 6 Update: Use Expanding Window to prevent Look-ahead Bias
        returns = strat_df['Close'].pct_change().fillna(0)
        volatility = returns.rolling(window=20).std().fillna(0)
        
        if len(strat_df) > 60:
            # Detect Regimes with Walk-Forward Validation
            # 0=Bull, 1=Volatile, 2=Bear
            regime_labels = self.regime_detector.fit_predict_expanding(
                returns.values, 
                volatility.values, 
                min_window=60
            )
            
            # Filter: If Bear (2), Force Cash
            is_bear = regime_labels == 2
            strat_df.loc[is_bear, 'Position'] = 0.0
        
        # 4. Volatility Filter (Scaling)
        strat_df['Ret'] = strat_df['Close'].pct_change()
        strat_df['Vol'] = strat_df['Ret'].rolling(self.vol_window).std() * np.sqrt(252) # Annualized
        
        # If Vol > 50% (0.5), Reduce position by half
        high_vol_mask = strat_df['Vol'] > 0.50
        strat_df.loc[high_vol_mask, 'Position'] = strat_df.loc[high_vol_mask, 'Position'] * 0.5
        
        return strat_df[['Close', 'RSI', 'SMA', 'Signal', 'Position', 'Vol']]

if __name__ == "__main__":
    print("--- SELF-TEST START: strategy_logic.py ---")
    
    # Create Dummy Data: Sine wave to simulate trend + dip
    x = np.linspace(0, 100, 200)
    prices = 100 + 10 * np.sin(x/10) + x/2  # Trend UP + Sine
    # Add some noise
    noise = np.random.normal(0, 1, 200)
    prices = prices + noise
    
    df = pd.DataFrame({'Close': prices})
    
    strategy = MomentumStrategy(rsi_period=10, sma_period=20)
    result = strategy.generate_signals(df)
    
    print("[TEST] Strategy Output Head:")
    print(result.tail(5))
    
    # Check if we have non-zero positions
    if result['Position'].abs().sum() > 0:
        print(f"[TEST] SUCCESS: Strategy generated positions. Avg Vol: {result['Vol'].mean():.2%}")
    else:
        print("[TEST] WARNING: Strategy stayed flat (might be expected for short data).")
        
    print("--- SELF-TEST END ---")
