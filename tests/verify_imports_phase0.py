
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ImportVerifier")

def test_imports():
    try:
        logger.info("Testing Data Loader...")
        from src.data_loader.validator import DataValidator
        from src.data_loader.downloader import fetch_data
        logger.info("✅ Data Loader OK")
        
        logger.info("Testing Macro Module...")
        from src.models.macro.macro_dashboard import get_macro_snapshot
        logger.info("✅ Macro Module OK")
        
        logger.info("Testing Arena Models...")
        from src.models.arena.tree_predictor import LightGBMPredictor
        from src.models.arena.lstm_predictor import MLPPredictor
        from src.models.arena.ai_optimizer import get_ai_trainer
        logger.info("✅ Arena Models OK")
        
        logger.info("Testing API Main...")
        # Just import, don't run
        import src.api.main
        logger.info("✅ API Main OK")
        
        logger.info("🎉 ALL IMPORTS PASSED")
        
    except ImportError as e:
        logger.error(f"❌ Import Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
