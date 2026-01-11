from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class BaseAnalyzer(ABC):
    """
    Base class for all analyzers.
    Follows Observer pattern to receive backtest data.
    """
    @abstractmethod
    def analyze(self, strat_df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform analysis on the backtest result DataFrame.
        args:
            strat_df: DataFrame containing 'Strat_Ret', 'Equity', 'Position', etc.
            context: dict with metadata (initial_capital, etc.)
        returns:
             Dictionary of metrics.
        """
        pass

class SharpeAnalyzer(BaseAnalyzer):
    def analyze(self, strat_df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        if 'Strat_Ret' not in strat_df.columns:
            return {"Sharpe_Ratio": 0.0}
            
        returns = strat_df['Strat_Ret']
        days = len(returns)
        if days < 2:
            return {"Sharpe_Ratio": 0.0}
            
        std_dev = returns.std() * np.sqrt(252)
        
        # Avoid division by zero
        if std_dev == 0:
            return {"Sharpe_Ratio": 0.0}
            
        total_return = (strat_df['Equity'].iloc[-1] / context.get('initial_capital', 100000)) - 1
        ann_return = (1 + total_return) ** (252/days) - 1
        
        sharpe = ann_return / std_dev
        return {"Sharpe_Ratio": float(sharpe), "Annualized_Return": float(ann_return)}

class DrawdownAnalyzer(BaseAnalyzer):
    def analyze(self, strat_df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        if 'Equity' not in strat_df.columns:
            return {"Max_Drawdown": 0.0}
            
        equity = strat_df['Equity']
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_dd = drawdown.min()
        
        return {"Max_Drawdown": float(max_dd)}

class TradeAnalyzer(BaseAnalyzer):
    def analyze(self, strat_df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        # This assumes 'trades' list is already extracted or extract it here
        # For V1 compatibility, we might pass the 'trades' list via context or re-calculate
        # Here we re-implement the trade extraction logic from Backtester to be self-contained
        # But efficiently, we should probably pass the trades list if it was generated during loop.
        
        # For now, let's assume we receive the 'trades' list in context, 
        # or we implement the basic stats if trades are available.
        trades = context.get('trades', [])
        if not trades:
            return {
                "Total_Trades": 0,
                "Win_Rate": 0.0,
                "Profit_Factor": 0.0
            }
            
        pnl_list = [t['pnl'] for t in trades if t['type'] == 'SELL']
        wins = [p for p in pnl_list if p > 0]
        losses = [p for p in pnl_list if p <= 0]
        
        total_trades = len(trades) # Total entries+exits or just round trips? 
        # V1 logic used len(trades) which mixes buys and sells. 
        # But 'Completed_Trades' was len(trade_returns).
        
        win_count = len(wins)
        total_completed = len(pnl_list)
        
        win_rate = win_count / total_completed if total_completed > 0 else 0
        
        total_profit = sum(wins)
        total_loss = abs(sum(losses))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return {
            "Total_Trades": len(trades),
            "Completed_Trades": total_completed,
            "Win_Rate": win_rate,
            "Profit_Factor": profit_factor
        }
