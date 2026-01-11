
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

print("--- VERIFYING HOTFIX ---")
try:
    print("1. Testing LightGBM Import...")
    from src.models.arena.tree_predictor import LightGBMPredictor
    print("✅ LightGBM Import Success")
except ImportError as e:
    print(f"❌ LightGBM Import Failed: {e}")
    sys.exit(1)

try:
    print("2. Testing MLP Import...")
    from src.models.arena.lstm_predictor import MLPPredictor
    print("✅ MLP Import Success")
except ImportError as e:
    print(f"❌ MLP Import Failed: {e}")
    sys.exit(1)

print("--- HOTFIX VERIFIED ---")
