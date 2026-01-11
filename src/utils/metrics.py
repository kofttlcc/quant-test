import numpy as np
import pandas as pd

def calculate_sortino_ratio(returns, risk_free_rate=0.0, target_return=0.0):
    """
    Calculate Sortino Ratio.
    Sortino Ratio = (Average Return - Risk Free Rate) / Downside Deviation
    
    Args:
        returns (pd.Series or np.array): Daily returns.
        risk_free_rate (float): Annualized risk-free rate (default 0).
        target_return (float): Minimum acceptable return (MAR) for downside deviation (default 0).
        
    Returns:
        float: Sortino Ratio.
    """
    if len(returns) < 2:
        return 0.0
        
    # Annualize returns
    avg_return = np.mean(returns) * 252
    
    # Calculate Downside Deviation
    # Filter only negative returns relative to target
    downside_returns = returns[returns < target_return]
    
    if len(downside_returns) == 0:
        return np.inf # No downside risk
        
    # Downside deviation calculation
    downside_std = np.std(downside_returns) * np.sqrt(252)
    
    if downside_std == 0:
        return np.inf
        
    sortino = (avg_return - risk_free_rate) / downside_std
    return sortino

def calculate_calmar_ratio(returns, max_drawdown):
    """
    Calculate Calmar Ratio.
    Calmar Ratio = Annualized Return / Abs(Max Drawdown)
    
    Args:
        returns (pd.Series or np.array): Daily returns.
        max_drawdown (float): Maximum Drawdown (positive value e.g. 0.20 for 20% DD, or negative).
                              Function handles sign.
        
    Returns:
        float: Calmar Ratio.
    """
    if max_drawdown == 0:
        return np.inf
        
    avg_return = np.mean(returns) * 252
    return avg_return / abs(max_drawdown)

def calculate_omega_ratio(returns, threshold=0.0):
    """
    Calculate Omega Ratio.
    Omega Ratio = Probability of winning / Probability of losing (weighted by magnitude).
    Formula: sum(returns > threshold) / sum(abs(returns < threshold))
    
    Args:
        returns (pd.Series or np.array): Daily returns.
        threshold (float): Threshold return (default 0).
        
    Returns:
        float: Omega Ratio.
    """
    if len(returns) == 0:
        return 0.0
        
    gains = returns[returns > threshold] - threshold
    losses = returns[returns < threshold] - threshold
    
    sum_gains = np.sum(gains)
    sum_losses = np.sum(np.abs(losses))
    
    if sum_losses == 0:
        return np.inf
        
    return sum_gains / sum_losses

def calculate_tail_ratio(returns, percentile=95):
    """
    Calculate Tail Ratio.
    Ratio of right tail (gains) to left tail (losses).
    Usually defined as: |95th percentile| / |5th percentile|
    
    Args:
        returns (pd.Series): Returns.
        
    Returns:
        float: Tail Ratio.
    """
    if len(returns) == 0:
        return 0.0
        
    right_tail = np.percentile(returns, percentile)
    left_tail = np.abs(np.percentile(returns, 100 - percentile))
    
    if left_tail == 0:
        return np.inf
        
    return right_tail / left_tail
