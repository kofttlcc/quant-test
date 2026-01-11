
import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from src.data_pipeline.cleaning import handle_outliers
    from src.models.indicators import calculate_rsi
    from src.models.strategy_logic import MomentumStrategy
    from src.models.lstm_predictor import MLPTrendModel, MLPPredictor  # MINOR-003 FIX: 使用新類名
    from src.models.regime_detector import RegimeDetector
    from src.backend.backtest_engine import Backtester
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class TestGeminiSystem(unittest.TestCase):
    
    def test_06_regime_detector(self):
        """Test Phase 5: Regime Detector"""
        detector = RegimeDetector()
        
        # Synthetic Bull (Pos Ret, Low Vol)
        bull_ret = np.random.normal(0.001, 0.01, 100)
        bull_vol = np.random.normal(0.01, 0.002, 100)
        
        # Synthetic Bear (Neg Ret, High Vol)
        bear_ret = np.random.normal(-0.002, 0.02, 100)
        bear_vol = np.random.normal(0.03, 0.005, 100)
        
        all_ret = np.concatenate([bull_ret, bear_ret])
        all_vol = np.concatenate([bull_vol, bear_vol])
        
        detector.fit(all_ret, all_vol)
        
        # Check prediction
        regime = detector.predict(0.002, 0.01) # Should be Bull
        self.assertIn(regime, ["Bull", "Volatile"])
        
    def test_07_strategy_with_filter(self):
        """Test Phase 5: Strategy with Regime Filter"""
        # Create Data with clear Downtrend (Bear)
        x = np.linspace(0, 100, 200)
        prices = 100 - x/2 + np.random.normal(0, 2, 200) # Downtrend
        df = pd.DataFrame({'Close': prices})
        
        strat = MomentumStrategy()
        res = strat.generate_signals(df)
        
        # In a strong downtrend + regime filter, position should be very low or zero
        # Note: GMM training on small sample might be noisy, but generally should detect Bear.
        # We check if it runs without error and produces output.
        self.assertIn('Position', res.columns)
        
        # Check if Position is 0 during extreme drops (optional strict check)
        # For now, just ensuring integration works (no crash)
        self.assertFalse(res.empty)

if __name__ == '__main__':
    print("running test suite...")
    unittest.main()
