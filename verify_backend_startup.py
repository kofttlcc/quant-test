
import sys
import os
import unittest

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src/backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from src.api.main import app
    print("SUCCESS: api_server (src.api.main) imported successfully.")
except ImportError as e:
    print(f"FAILURE: Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Startup failed: {e}")
    sys.exit(1)
