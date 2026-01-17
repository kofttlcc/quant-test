
import sys
import os

# Add src to path just like main.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

print(f"Python Executable: {sys.executable}")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not Set')}")

print("\n--- Diagnostic Import Check ---")

try:
    print("Attempting to import Backtester...")
    from src.backend.backtest_engine import Backtester
    print("✅ Backtester imported.")
except ImportError as e:
    print(f"❌ Backtester failed: {e}")
except Exception as e:
    print(f"❌ Backtester failed (Exception): {e}")

try:
    print("Attempting to import AlphaBetaAnalyzer...")
    from src.models.alpha_beta import AlphaBetaAnalyzer
    print("✅ AlphaBetaAnalyzer imported.")
except ImportError as e:
    print(f"❌ AlphaBetaAnalyzer failed: {e}")
except Exception as e:
    print(f"❌ AlphaBetaAnalyzer failed (Exception): {e}")

try:
    print("Attempting to import statsmodels.api...")
    import statsmodels.api as sm
    print("✅ statsmodels.api imported.")
except ImportError as e:
    print(f"❌ statsmodels.api failed: {e}")
except Exception as e:
    print(f"❌ statsmodels.api failed (Exception): {e}")

try:
    print("Attempting to import ResultStorage...")
    from src.backend.storage import ResultStorage
    print("✅ ResultStorage imported.")
except ImportError as e:
    print(f"❌ ResultStorage failed: {e}")
except Exception as e:
    print(f"❌ ResultStorage failed (Exception): {e}")
    
print("\n--- End Diagnostic ---")
