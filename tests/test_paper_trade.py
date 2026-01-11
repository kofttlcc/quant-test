import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.backend.paper_trade import PaperTradingEngine

class MockStrategy:
    def generate_signals(self, df):
        df = df.copy()
        # Always return 1.0 position (Long)
        df['Position'] = 1.0 
        return df

class TestPaperTrade(unittest.TestCase):
    
    def setUp(self):
        self.test_file = "test_state.json"
        
        # Mock Data
        self.dates = pd.date_range(start='2023-01-01', periods=50, freq='H')
        self.df = pd.DataFrame({
            'Open': [100]*50,
            'High': [105]*50,
            'Low': [95]*50,
            'Close': [100]*50,
            'Volume': [1000]*50
        }, index=self.dates)
        
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch('src.backend.paper_trade.yf.download')
    def test_execution_flow(self, mock_download):
        """Test full execution step: fetch -> strategy -> trade -> save"""
        
        # 1. Setup Mock Data Return
        mock_download.return_value = self.df
        
        # 2. Init Engine
        strat = MockStrategy()
        engine = PaperTradingEngine(strat, "AAPL", initial_capital=10000, state_file=self.test_file)
        
        # Check Initial State
        self.assertEqual(engine.state["cash"], 10000)
        self.assertEqual(engine.state["positions"], 0)
        
        # 3. Execute Step (Should Buy)
        # Strategy returns Position=1.0 (Full allocation)
        # Price is 100. Shares = 10000 / 100 = 100
        engine.execute_step()
        
        # Verify State after Buy
        # Cash should be near 0 (minus small diff due to integer division or float precision)
        # Positions should be 100
        self.assertEqual(engine.state["positions"], 100)
        self.assertLess(engine.state["cash"], 100) # Remainder
        self.assertTrue(os.path.exists(self.test_file))
        
        # 4. Persistence Check
        with open(self.test_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data["positions"], 100)
            self.assertEqual(len(data["history"]), 1)
            self.assertEqual(data["history"][0]["type"], "BUY")
            
        print("Paper Trade Single Step Test Passed")

    def test_persistence_loading(self):
        """Test if engine loads existing state"""
        # Create a pre-existing state
        initial_state = {
            "cash": 5000.0,
            "positions": 50.0,
            "equity": 10000.0,
            "history": [],
            "last_update": None
        }
        with open(self.test_file, 'w') as f:
            json.dump(initial_state, f)
            
        engine = PaperTradingEngine(MockStrategy(), "AAPL", state_file=self.test_file)
        self.assertEqual(engine.state["cash"], 5000.0)
        self.assertEqual(engine.state["positions"], 50.0)
        
        print("Paper Trade Persistence Loading Passed")

if __name__ == '__main__':
    unittest.main()
