
"""
verify_ui_integration.py - UI Data Exposure Verification
=========================================================
Changes verified:
1. AI Trainer -> Feature Importance
2. StatArb -> Half-Life & OU Params
3. Backtester -> Total Commission
"""
import sys
import os
import pandas as pd
import numpy as np
import logging

# Add root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.models.arena.ai_optimizer import get_ai_trainer
from src.strategies.stat_arb.engine import StatArbEngine
from src.strategies.stat_arb.selector import PairsSelector
from src.backend.backtest_engine import Backtester
from src.data_loader.downloader import fetch_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyUI")

def test_ai_feature_importance():
    logger.info("--- Testing AI Feature Importance ---")
    trainer = get_ai_trainer()
    
    # Mock training params
    params = {
        "n_estimators": 10,
        "max_depth": 3,
        "learning_rate": 0.1
    }
    
    # Needs real data to compute importance?
    # We can rely on fetch_data in trainer.
    # Start a job
    job_id = trainer.start_training_job("lightgbm", "AAPL", params)
    
    # Wait for completion (timeout 30s)
    import time
    max_wait = 30
    start = time.time()
    while time.time() - start < max_wait:
        status = trainer.get_job_status(job_id)
        if status['status'] in ['completed', 'failed']:
            break
        time.sleep(1)
        
    status = trainer.get_job_status(job_id)
    if status['status'] == 'completed':
        res = status.get('result', {})
        fi = res.get('feature_importance')
        if fi:
            logger.info(f"✅ Feature Importance Found: {list(fi.keys())[:3]}...")
            return True
        else:
            logger.error("❌ Feature Importance Missing in Result")
            return False
    else:
        logger.error(f"❌ Training Failed or Timed Out: {status.get('error')}")
        return False

def test_statarb_halflife():
    logger.info("--- Testing StatArb Half-Life Exposure ---")
    
    # Generate cointegrated data (High Correlation)
    np.random.seed(42)
    x = np.cumsum(np.random.randn(200))
    # Y is effectively X with small spread: Y = 1.0*X + small_noise
    # This ensures high correlation of returns
    y = x + np.random.randn(200) * 0.1 
    
    df = pd.DataFrame({'A': x, 'B': y}, index=pd.date_range('2023-01-01', periods=200))
    
    selector = PairsSelector()
    pairs = selector.find_best_pairs(df, top_n=1)
    
    if not pairs:
        logger.error("❌ No pairs found")
        return False
        
    p = pairs[0]
    hl = p.get('half_life')
    
    if hl is not None:
        logger.info(f"✅ Half-Life Exposed in Selector: {hl:.2f}")
    else:
        logger.error("❌ Half-Life Missing in Selector Result")
        return False
        
    # Test Engine Signals
    engine = StatArbEngine()
    s1 = df['A']
    s2 = df['B']
    spread = engine.calculate_spread(s1, s2, p['beta'])
    signals = engine.generate_signals(spread)
    
    if 'HalfLife' in signals.columns:
        logger.info(f"✅ Half-Life Exposed in Signals: {signals['HalfLife'].iloc[-1]:.2f}")
        return True
    else:
        logger.error("❌ Half-Life Column Missing in Signals")
        return False

def test_backtest_commission():
    logger.info("--- Testing Backtest Total Commission ---")
    
    dates = pd.date_range('2023-01-01', periods=100)
    df = pd.DataFrame({
        'Close': np.linspace(100, 200, 100),
        'Open': np.linspace(100, 200, 100), # Simple
        'volume': 1000
    }, index=dates)
    
    class MockStrat:
        def generate_signals(self, d):
            d = d.copy()
            d['Position'] = 1.0 # Buy and Hold
            d['Position'].iloc[50:] = 0.0 # Sell
            return d
            
    bt = Backtester(commission_bps=10)
    res = bt.run_backtest(df, MockStrat())
    
    metrics = res['metrics']
    comm = metrics.get('Total_Commission')
    
    if comm is not None and comm > 0:
        logger.info(f"✅ Total Commission Exposed: {comm:.4f}")
        return True
    else:
        logger.error(f"❌ Total Commission Missing or Zero: {comm}")
        return False

if __name__ == "__main__":
    tests = [
        test_statarb_halflife(),
        test_backtest_commission(),
        test_ai_feature_importance() # Run last as it takes time
    ]
    
    if all(tests):
        print("\n🟢 ALL UI VERIFICATION TESTS PASSED")
        sys.exit(0)
    else:
        print("\n🔴 SOME TESTS FAILED")
        sys.exit(1)
