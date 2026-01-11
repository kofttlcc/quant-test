import unittest
import pandas as pd
import numpy as np
import sys
import os

# Create a proper package structure for tests to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.portfolio import Portfolio
from src.utils.metrics import calculate_sortino_ratio, calculate_calmar_ratio, calculate_omega_ratio

class MockStrategy:
    def __init__(self, position_val):
        self.position_val = position_val
        
    def generate_signals(self, df):
        df = df.copy()
        df['Position'] = self.position_val
        return df

class TestPhase1(unittest.TestCase):
    
    def setUp(self):
        # Create dummy data
        dates = pd.date_range(start='2023-01-01', periods=10, freq='D')
        self.df = pd.DataFrame({
            'Open': [100]*10,
            'High': [105]*10,
            'Low': [95]*10,
            'Close': [100]*10,
            'Volume': [1000]*10
        }, index=dates)
        
    def test_portfolio_combination(self):
        """Test if Portfolio correctly combines weights"""
        # Strat 1: Full Long (1.0)
        s1 = MockStrategy(1.0)
        # Strat 2: Cash (0.0)
        s2 = MockStrategy(0.0)
        
        # 50/50 Portfolio
        portfolio = Portfolio(strategies=[s1, s2], weights=[0.5, 0.5])
        
        res = portfolio.generate_signals(self.df)
        
        # Expected position: 1.0 * 0.5 + 0.0 * 0.5 = 0.5
        self.assertTrue(np.allclose(res['Position'], 0.5))
        print(f"Portfolio Combined Position: {res['Position'].iloc[0]} (Expected 0.5)")

    def test_sortino_ratio(self):
        """Test Sortino Ratio Calculation"""
        # Case 1: All positive returns -> Sortino Inf
        ret_pos = np.array([0.01, 0.02, 0.01])
        s_pos = calculate_sortino_ratio(ret_pos)
        self.assertEqual(s_pos, np.inf)
        
        # Case 2: Mixed
        ret_mixed = np.array([0.01, -0.02, 0.03, -0.01])
        s_mixed = calculate_sortino_ratio(ret_mixed)
        self.assertTrue(s_mixed > -10 and s_mixed < 10) # Just check it's a valid float
        print(f"Sortino Ratio: {s_mixed}")

    def test_calmar_ratio(self):
        """Test Calmar Ratio"""
        # Annualized return approx 10% (0.0004 daily), Max DD 0.2
        ret = np.array([0.0004] * 252) # 10% annual
        calmar = calculate_calmar_ratio(ret, 0.2)
        # 0.1 / 0.2 = 0.5
        self.assertAlmostEqual(calmar, 0.528, places=1) # (1.0004^252 - 1) approx 0.105 / 0.2
        print(f"Calmar Ratio: {calmar}")

if __name__ == '__main__':
    unittest.main()
