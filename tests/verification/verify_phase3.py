
import sys
import os
import logging
import pandas as pd
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase3_Verifier")

def verify_arena():
    logger.info("=== Starting Phase 3 Validation (Adversarial Arena) ===")
    
    from src.models.arena.adversarial_arena import AdversarialArena
    
    # 1. Create Data
    dates = pd.date_range("2024-01-01", periods=300)
    prices = [100 + i*0.05 + np.sin(i/5)*5 for i in range(300)] # Wavy trend
    df = pd.DataFrame({
        "Open": prices, "High": prices, "Low": prices, "Close": prices, "Volume": 1000
    }, index=dates)
    
    # 2. Run Arena
    arena = AdversarialArena()
    res_df, res_meta = arena.run_battle(df)
    
    # 3. Checks
    if res_meta is None:
        logger.error("❌ Arena Battle Returned None")
        sys.exit(1)
        
    weights = res_meta.weights
    if abs(sum(weights.values()) - 1.0) > 0.01:
        logger.error(f"❌ Weights do not sum to 1: {weights}")
        sys.exit(1)
        
    logger.info(f"✅ Weights Logic: {weights}")
    
    if "Signal_Hybrid" not in res_df.columns:
        logger.error("❌ Signal_Hybrid column missing")
        sys.exit(1)
        
    logger.info("✅ Hybrid Signal Generated")
    
    # Check Model Persistence (Mock check)
    # Ideally check if models saved, but here we check execution flow
    
    logger.info("🎉 PHASE 3 VERIFICATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    verify_arena()
