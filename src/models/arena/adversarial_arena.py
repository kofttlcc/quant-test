
"""
adversarial_arena.py - AI Model Battleground
============================================
Version: 3.0 (Phase 3)
Role: [MLE]
Function:
1. Orchestrate competition between Tree (LightGBM) and Deep (MLP/LSTM) models.
2. Evaluate performance on a common validation set.
3. Assign dynamic weights based on "Adversarial" performance.
4. Output final hybrid signal.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

try:
    from src.models.arena.tree_predictor import LightGBMPredictor
    from src.models.arena.lstm_predictor import MLPPredictor
except ImportError:
    # Fallback for local testing
    from tree_predictor import LightGBMPredictor
    from lstm_predictor import MLPPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArenaResult:
    winner: str
    weights: Dict[str, float]
    metrics: Dict[str, Dict[str, float]]
    timestamp: str

class AdversarialArena:
    """
    The Arena where models fight.
    Mechanism: 
    1. Split Data -> Train / Val (Last 30 days or 20%)
    2. Train Models independently.
    3. Eval on Val.
    4. Weight based on ROI/Sharpe.
    """
    
    def __init__(self):
        self.model_tree = LightGBMPredictor()
        self.model_deep = MLPPredictor()
        self.models = {
            "Tree_LightGBM": self.model_tree,
            "Deep_MLP": self.model_deep
        }
        self.last_result: ArenaResult = None
        
    def run_battle(self, df: pd.DataFrame, validation_window: int = 60) -> Tuple[pd.DataFrame, ArenaResult]:
        """
        Execute the battle.
        
        Args:
            df: OHLCV Data
            validation_window: Number of bars for validation (Default 60 days)
            
        Returns:
            start_df: DataFrame with 'Signal_Hybrid', 'Signal_Tree', 'Signal_Deep'
            result: ArenaResult
        """
        if len(df) < 200:
            logger.warning("Not enough data for Arena Battle (Need > 200).")
            return df, None
            
        logger.info(f"⚔️ Starting Arena Battle on {len(df)} rows...")
        
        # 1. Run Models (They handle their own training on historical data provided)
        # Note: predictors' generate_signals usually train on historical and predict on test.
        # We need to capture their output.
        
        # Deep Model
        df_deep = self.model_deep.generate_signals(df.copy())
        sig_deep = df_deep['Signal'].values if 'Signal' in df_deep else np.zeros(len(df))
        
        # Tree Model
        df_tree = self.model_tree.generate_signals(df.copy())
        sig_tree = df_tree['Signal'].values if 'Signal' in df_tree else np.zeros(len(df))
        
        # 2. Validation (Last N periods)
        # Define Validation Slice
        val_start_idx = len(df) - validation_window
        val_idx = df.index[val_start_idx:]
        
        y_true_returns = df['Close'].pct_change().fillna(0).values
        
        metrics = {}
        
        # Eval Tree
        m_tree = self._evaluate_signal(sig_tree, y_true_returns, val_start_idx)
        metrics["Tree_LightGBM"] = m_tree
        
        # Eval Deep
        m_deep = self._evaluate_signal(sig_deep, y_true_returns, val_start_idx)
        metrics["Deep_MLP"] = m_deep
        
        # 3. Dynamic Weighting (Softmax-ish or Proportional)
        # Score = Sharpe * ROI_Factor
        
        score_tree = max(0, m_tree['sharpe'] * 2 + m_tree['roi'] * 10)
        score_deep = max(0, m_deep['sharpe'] * 2 + m_deep['roi'] * 10)
        
        total_score = score_tree + score_deep + 1e-6
        w_tree = score_tree / total_score
        w_deep = score_deep / total_score
        
        # Safety: If both fail (score=0), default equal
        if score_tree == 0 and score_deep == 0:
            w_tree, w_deep = 0.5, 0.5
            
        weights = {"Tree_LightGBM": round(w_tree, 2), "Deep_MLP": round(w_deep, 2)}
        winner = "Tree_LightGBM" if w_tree >= w_deep else "Deep_MLP"
        
        logger.info(f"🏆 Battle Over: Winner {winner} (Tree: {w_tree:.2f}, Deep: {w_deep:.2f})")
        
        # 4. Hybrid Signal Generation
        # Weighted Signal
        hybrid_sig_raw = (sig_tree * w_tree) + (sig_deep * w_deep)
        
        # Thresholding (Robustness)
        # If > 0.3 -> Buy (1), < -0.3 -> Sell (-1), Else 0
        hybrid_final = np.zeros(len(df))
        hybrid_final[hybrid_sig_raw > 0.3] = 1
        hybrid_final[hybrid_sig_raw < -0.3] = -1
        
        # Append to Result DF
        result_df = df.copy()
        result_df['Signal_Tree'] = sig_tree
        result_df['Signal_Deep'] = sig_deep
        result_df['Signal_Hybrid'] = hybrid_final
        result_df['Signal'] = hybrid_final # Main Signal used by Backtester
        
        from datetime import datetime
        self.last_result = ArenaResult(
            winner=winner,
            weights=weights,
            metrics=metrics,
            timestamp=datetime.now().isoformat()
        )
        
        return result_df, self.last_result
        
    def _evaluate_signal(self, signal: np.ndarray, returns: np.ndarray, start_idx: int) -> Dict[str, float]:
        """Calculates ROI and Sharpe on validation set."""
        # Slice
        s = signal[start_idx:]
        r = returns[start_idx:]
        
        # Strategy Returns
        strat_ret = s * r   # Signal * Market Return (Shifted? Usually signal T predicts T+1 return? 
                            # Assuming generate_signals output aligns Signal T with Return T+1 or 
                            # Signal T is for position held during T return?
                            # Standard convention: Signal at T close affects T+1 return.
                            # BUT `generate_signals` usually aligns 'Signal' row with the date the signal is VALID for.
                            # Check predict logic: "X[t] predicts y[t+1]". 
                            # "strat_df.iloc[start_idx:] = test_signals".
                            # It seems Signal corresponds to prediction for NEXT move.
                            # So Strat Return = Signal[t] * Return[t+1].
                            # Let's shift Returns by -1 to align.
                            
        # Align: Signal at index i is action for Returns at index i+1
        # To simplify, let's assume `generate_signals` places signal on the bar generated.
        # Action is taken NEXT Open. 
        # For simplicity here: strategy properties usually align Signal with Date.
        # Let's perform a shift: Trade PnL = Signal[i] * Returns[i+1]
        
        # Calculate PnL Series
        pnl = []
        for i in range(len(s) - 1):
            pnl.append(s[i] * r[i+1])
            
        if not pnl: 
            return {'roi': 0.0, 'sharpe': 0.0}
            
        pnl = np.array(pnl)
        
        # Metrics
        total_roi = np.sum(pnl)
        std = np.std(pnl) 
        sharpe = (np.mean(pnl) / std * np.sqrt(252)) if std > 1e-6 else 0.0
        
        return {
            'roi': float(total_roi),
            'sharpe': float(sharpe)
        }

if __name__ == "__main__":
    print("--- SELF-TEST: adversarial_arena.py ---")
    
    # Mock Data
    dates = pd.date_range("2024-01-01", periods=300)
    # Trend up then down
    prices = [100 + i*0.1 + np.sin(i/10)*2 for i in range(300)]
    df = pd.DataFrame({
        "Open": prices, "High": prices, "Low": prices, "Close": prices, "Volume": 1000
    }, index=dates)
    
    arena = AdversarialArena()
    res_df, res_meta = arena.run_battle(df)
    
    if res_meta:
        print(f"Winner: {res_meta.winner}")
        print(f"Weights: {res_meta.weights}")
        print(f"Metrics: {res_meta.metrics}")
    else:
        print("Battle Failed.")
