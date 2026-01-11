
import sys
import os
import logging
from flask import Flask

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Phase4_Verifier")

def verify_api():
    logger.info("=== Starting Phase 4 Verification (Backend API) ===")
    
    try:
        from src.api.main import app
    except ImportError as e:
        logger.error(f"❌ Failed to import src.api.main: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Exception during import: {e}")
        # Note: Might fail if environment variables (API Key) are missing, but main.py warns instead of crash usually
        sys.exit(1)

    # 1. Check Routes
    routes = [str(p) for p in app.url_map.iter_rules()]
    logger.info(f"Loaded Routes: {len(routes)}")
    
    required_routes = [
        '/api/v1/macro/overview',
        '/api/v1/arena/adversarial'
    ]
    
    missing = []
    for r in required_routes:
        found = any(r in route for route in routes)
        if found:
            logger.info(f"✅ Route Found: {r}")
        else:
            logger.error(f"❌ Route Missing: {r}")
            missing.append(r)
            
    if missing:
        sys.exit(1)
        
    # 2. Test Client (Bypassing Auth for checking basic functionality logic if possible, or just connectivity)
    # We will just verify imports and route registration for now to avoid side effects (API Keys etc)
    
    logger.info("🎉 PHASE 4 VERIFICATION COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    verify_api()
