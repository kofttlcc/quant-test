import unittest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.portfolio import Portfolio
from src.backend.paper_trade import PaperTradingEngine
from src.backend.backtest_engine import Backtester
# Mock strategies to avoid dependency on real data/libs
class MockMomStrategy:
    def generate_signals(self, df):
        df = df.copy()
        df['Position'] = 1.0 # Long
        return df

class MockRSIStrategy:
    def generate_signals(self, df):
        df = df.copy()
        df['Position'] = -1.0 # Short
        return df

class TestIntegrationV1_1(unittest.TestCase):
    
    def setUp(self):
        dates = pd.date_range(start='2023-01-01', periods=50, freq='D')
        self.df = pd.DataFrame({
            'Open': [100]*50,
            'High': [105]*50,
            'Low': [95]*50,
            'Close': [100]*50,
            'Volume': [1000]*50,
            'Date': dates
        }, index=dates)

    def test_portfolio_backtest(self):
        """Test Backtester with Portfolio (Duck Typing)"""
        p = Portfolio(strategies=[MockMomStrategy(), MockRSIStrategy()], weights=[0.5, 0.5])
        
        # Mom = 1.0, RSI = -1.0. 50/50 => 0.0 Net Position
        bt = Backtester()
        res = bt.run_backtest(self.df, p)
        
        # If position is 0, returns should be 0 (minus costs if turnover)
        # Turnover: Day 1 pos goes 0->0. No turnover except maybe first day?
        # Actually generate_signals sets position.
        # Backtest loop: 
        # Position 0 -> Equity constant (approx)
        
        final_eq = res['metrics']['Final_Equity']
        # Should be close to initial (100000)
        self.assertTrue(99000 < final_eq < 101000)
        print(f"Portfolio Backtest Final Equity: {final_eq}")

    @patch('src.backend.paper_trade.yf.download')
    def test_paper_trade_with_portfolio(self, mock_download):
        """Test Paper Trading Engine with Portfolio"""
        mock_download.return_value = self.df
        
        p = Portfolio(strategies=[MockMomStrategy(), MockRSIStrategy()], weights=[0.8, 0.2])
        # 0.8 * 1.0 + 0.2 * (-1.0) = 0.6 Net Long
        
        engine = PaperTradingEngine(p, "AAPL", state_file="test_integration_state.json")
        engine.execute_step()
        
        # Expect position to be positive (0.6 exposure)
        # engine.execute_step calls fetch_latest, then strategy.generate, then buys/sells
        # check state
        self.assertGreater(engine.state['positions'], 0)
        print(f"Paper Trade Engine Position after step: {engine.state['positions']}")
        
        # Cleanup
        if os.path.exists("test_integration_state.json"):
            os.remove("test_integration_state.json")

if __name__ == '__main__':
    unittest.main()
