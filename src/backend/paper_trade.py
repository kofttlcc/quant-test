import pandas as pd
import numpy as np
import yfinance as yf
import json
import os
import logging
from datetime import datetime
import time

# Configure logging
logger = logging.getLogger(__name__)

class PaperTradingEngine:
    """
    Paper Trading Engine for simulating real-time trading.
    - Fetches "live" data via yfinance.
    - Executes strategy signals.
    - Manages virtual account state.
    - Persists state to JSON.
    """
    def __init__(self, strategy, ticker, initial_capital=100000.0, state_file="paper_trade_state.json"):
        """
        Args:
            strategy: Strategy instance (must have generate_signals).
            ticker (str): Symbol to trade (Single asset for MVP).
            initial_capital (float): Starting cash.
            state_file (str): Path to JSON persistence file.
        """
        self.strategy = strategy
        self.ticker = ticker
        self.state_file = state_file
        
        # Default State
        self.state = {
            "cash": initial_capital,
            "positions": 0.0,  # Number of shares
            "avg_price": 0.0,
            "equity": initial_capital,
            "market_history": [],  # List of {time, price, equity}
            "history": [],
            "last_update": None,
            "strategy_name": strategy.__class__.__name__ # Store strategy name
        }
        
        self.load_state()
        self.save_state()  # Ensure state file exists immediately

    def load_state(self):
        """Load state from JSON file if exists."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded paper trade state from {self.state_file}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

    def save_state(self):
        """Save current state to JSON."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=4, default=str)
            logger.info("State saved.")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def fetch_latest_data(self, period="5d", interval="1h"):
        """
        Fetch latest data window for strategy.
        Interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        """
        try:
            df = yf.download(self.ticker, period=period, interval=interval, progress=False)
            if df.empty:
                logger.warning(f"No data fetched for {self.ticker}")
                return None
            return df
        except Exception as e:
            logger.error(f"Data fetch error: {e}")
            return None

    def execute_step(self):
        """
        Main simulation step:
        1. Get Data
        2. Run Strategy
        3. Check Signals
        4. Execute Order
        5. Update State
        """
        logger.info(f"--- Paper Trade Step: {datetime.now()} ---")
        
        # 1. Get Data
        df = self.fetch_latest_data()
        if df is None or df.empty:
            return

        current_price = df['Close'].iloc[-1]
        timestamp = df.index[-1]
        
        # 2. Run Strategy
        # Strategy expects a DF and returns a DF with "Position" column
        try:
            strat_result = self.strategy.generate_signals(df)
            target_position_pct = strat_result['Position'].iloc[-1] # Target % weight (e.g. 1.0 or 0.0)
            
            # Simple assumption: Position is target weight of Total Equity
            # If strategy returns share counts, logic differs. Assuming weight here (0 to 1).
            
        except Exception as e:
            logger.error(f"Strategy execution failed: {e}")
            return

        # 3. Calculate Actions
        total_equity = self.state["cash"] + (self.state["positions"] * current_price)
        target_value = total_equity * target_position_pct
        current_value = self.state["positions"] * current_price
        
        diff_value = target_value - current_value
        
        # Threshold to avoid noise (e.g. < $10 trade driven by float noise)
        if abs(diff_value) < 100: 
            self._update_equity(current_price, timestamp)
            return

        # 4. Execute (calculate shares)
        # Assuming no fractional shares for simplicity, unless API supports it
        shares_to_trade = int(diff_value / current_price)
        
        if shares_to_trade == 0:
            self._update_equity(current_price, timestamp)
            return
            
        trade_type = "BUY" if shares_to_trade > 0 else "SELL"
        cost = shares_to_trade * current_price
        
        # Update Cash & Position
        self.state["cash"] -= cost
        self.state["positions"] += shares_to_trade
        
        # Log Trade
        trade_rec = {
            "time": str(datetime.now()), # Real time execution
            "candle_time": str(timestamp), 
            "type": trade_type,
            "shares": shares_to_trade,
            "price": float(current_price),
            "value": float(cost),
            "resulting_position": float(self.state["positions"])
        }
        self.state["history"].append(trade_rec)
        
        logger.info(f"Executed {trade_type} {abs(shares_to_trade)} shares at {current_price:.2f}")

        # 5. Update Equity & Save
        self._update_equity(current_price, timestamp)

    def _update_equity(self, current_price, timestamp=None):
        """Update Net Liquidity Value."""
        equity = self.state["cash"] + (self.state["positions"] * current_price)
        self.state["equity"] = float(equity)
        self.state["last_update"] = str(datetime.now())
        
        # Add to Market History (for Chart)
        snapshot = {
            "time": str(timestamp) if timestamp else str(datetime.now()),
            "price": float(current_price),
            "equity": float(equity)
        }
        
        # Prevent duplicate entries for same time
        if not self.state.get("market_history"):
             self.state["market_history"] = []
             
        # Simple append
        self.state["market_history"].append(snapshot)
        
        # Limit history size to prevent bloat (optional, e.g. last 1000 candles)
        if len(self.state["market_history"]) > 2000:
             self.state["market_history"].pop(0)

        self.save_state()
        logger.info(f"Current Equity: {equity:.2f} | Cash: {self.state['cash']:.2f} | Pos: {self.state['positions']}")
