
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase2_Verifier")

def verify_macro():
    logger.info("=== Starting Phase 2 Verification ===")
    
    from src.models.macro.macro_dashboard import get_macro_snapshot
    
    try:
        snapshot = get_macro_snapshot(force_refresh=True)
        
        # Check Critical Fields
        required = ['risk_score', 'risk_mode', 'vix_value', 'yield_spread', 'sentiment_score']
        for r in required:
            if r not in snapshot:
                logger.error(f"❌ Missing Field: {r}")
                sys.exit(1)
                
        # Check Logic Consistency
        score = snapshot['risk_score']
        if not (0 <= score <= 100):
            logger.error(f"❌ Risk Score Out of Range: {score}")
            sys.exit(1)
            
        logger.info(f"✅ Macro Snapshot: Risk Score {score} ({snapshot['risk_mode']})")
        logger.info(f"   VIX: {snapshot['vix_value']}")
        logger.info(f"   Spread: {snapshot['yield_spread']}")
        logger.info(f"   Sentiment: {snapshot['sentiment_score']}")
        logger.info(f"   Quality: {snapshot['data_quality']}")
        
    except Exception as e:
        logger.error(f"❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    logger.info("🎉 PHASE 2 VERIFICATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    verify_macro()
