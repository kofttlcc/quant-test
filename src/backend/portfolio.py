import pandas as pd
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Portfolio:
    """
    Multi-Strategy Portfolio Combiner.
    Acts as a meta-strategy that aggregates signals from multiple sub-strategies.
    """
    def __init__(self, strategies=None, weights=None):
        """
        Initialize Portfolio.
        
        Args:
            strategies (list): List of strategy instances. Each must have generate_signals(df).
            weights (list): List of weights (float). Must sum to 1.0. If None, equal weights.
        """
        self.strategies = strategies if strategies else []
        self.weights = weights
        self._validate_config()
        
    def _validate_config(self):
        """Validate strategies and weights configuration."""
        if not self.strategies:
            logger.warning("Portfolio initialized with no strategies.")
            return

        if self.weights is None:
            n = len(self.strategies)
            self.weights = [1.0 / n] * n
        else:
            if len(self.weights) != len(self.strategies):
                raise ValueError(f"Number of weights ({len(self.weights)}) must match strategies ({len(self.strategies)})")
            if not np.isclose(sum(self.weights), 1.0):
                logger.warning(f"Weights sum to {sum(self.weights)}, normalizing to 1.0")
                total = sum(self.weights)
                self.weights = [w / total for w in self.weights]

    def add_strategy(self, strategy, weight=None):
        """
        Add a strategy to the portfolio.
        Note: Re-calculates weights if not provided.
        """
        self.strategies.append(strategy)
        if weight:
            self.weights.append(weight)
            # Re-normalize
            total = sum(self.weights)
            self.weights = [w / total for w in self.weights]
        else:
            # Reset to equal weights
            n = len(self.strategies)
            self.weights = [1.0 / n] * n

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate combined signals from all sub-strategies.
        
        Args:
            df (pd.DataFrame): OHLCV data.
            
        Returns:
            pd.DataFrame: DataFrame with aggregated 'Position' and 'Signal'.
        """
        if not self.strategies:
            return df
        
        # Initialize combined position
        combined_position = pd.Series(0.0, index=df.index)
        
        # Store individual strategy results for debugging/analysis
        self.strategy_results = {}
        
        for i, strategy in enumerate(self.strategies):
            weight = self.weights[i]
            try:
                # Generate signale for sub-strategy
                strat_res = strategy.generate_signals(df)
                
                # Check if Position exists
                if 'Position' in strat_res.columns:
                    pos = strat_res['Position'].fillna(0.0)
                    combined_position += pos * weight
                    self.strategy_results[f"Strat_{i}"] = strat_res
                else:
                    logger.warning(f"Strategy {i} did not return 'Position' column.")
            except Exception as e:
                logger.error(f"Error in strategy {i}: {e}")
                
        # Create result DataFrame
        result_df = df.copy()
        result_df['Position'] = combined_position
        
        # Determine consolidated Signal (change in position)
        # Signal is mostly for display/event-trigger, Position is for equity calc
        # 1 = Buy, -1 = Sell, but for continuous mult-strat, we act on Position change
        result_df['Signal'] = np.sign(result_df['Position'].diff().fillna(0))
        
        return result_df
