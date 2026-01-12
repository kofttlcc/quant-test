
import sys
import os
import requests
import json
import warnings
from datetime import datetime

# Define backend URL
BACKEND_URL = "http://localhost:8000"

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.HEADER}{'='*60}")
    print(f" {title}")
    print(f"{'='*60}{Colors.ENDC}")

def get_macro_report():
    print(f"{Colors.BLUE}Fetching Macro Analysis (Sentinel)...{Colors.ENDC}")
    # In a real scenario, we'd hit the API. 
    # For this script to work standalone (without forcing user to run uvicorn separately), 
    # we will import the logic directly if connection fails, simulating a dual-mode client.
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/macro/report", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"{Colors.WARNING}⚠️ API unreachable ({e}), switching to local Library mode...{Colors.ENDC}")
        
    # Local fallback
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if root_dir not in sys.path:
        sys.path.append(root_dir)
    from src.models.sentinel import StrategicSentinel
    from src.models.ml.ensemble import MLEnsemble
    
    sentinel = StrategicSentinel()
    bm, vix = sentinel.fetch_market_data()
    result = sentinel.analyze(bm, vix)
    if not result: return None
    return {
        "verdict": result.verdict,
        "risk_score": result.risk_score,
        "valuation_status": result.val_status,
        "reasons": result.reasons
    }

def get_valuation(ticker):
    print(f"{Colors.BLUE}Calculating Intrinsic Value for {ticker}...{Colors.ENDC}")
    try:
        response = requests.get(f"{BACKEND_URL}/api/stock/{ticker}/valuation", timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        from src.models.valuation_enhanced import EnhancedValuationEngine
        engine = EnhancedValuationEngine(ticker)
        res = engine.assess_value()
        if not res: return None
        return {
            "current_price": res.current_price,
            "composite_value": res.composite_value,
            "margin_of_safety": res.margin_of_safety,
            "status": res.status,
            "confidence": res.confidence,
            "method_values": {
                 "dcf": res.dcf_value,
                 "graham": res.graham_value
            }
        }

def get_ml_signal(ticker):
    print(f"{Colors.BLUE}Generatng ML Alpha Signal for {ticker}...{Colors.ENDC}")
    try:
        response = requests.get(f"{BACKEND_URL}/api/stock/{ticker}/ml-signal", timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception:
        # Fallback requires loading ML models which might be slow
        print("  (Local ML inference might take a moment...)")
        from src.models.ml.ensemble import MLEnsemble
        import yfinance as yf
        
        # MEM-002 FIX: 使用函數屬性而非 globals() 存儲
        if not hasattr(get_ml_signal, '_ensemble'):
            get_ml_signal._ensemble = MLEnsemble(target_vol=0.15, use_ensemble=False)
        
        data = yf.download(ticker, period="1y", progress=False)
        if isinstance(data.columns, pd.MultiIndex): data = data.xs(ticker, axis=1, level=0)
        signal = get_ml_signal._ensemble.generate_signal(data, ticker=ticker, include_alpha=True)
        return {
            "regime": signal.regime_name,
            "signal": float(signal.final_signal.iloc[-1]),
            "confidence": signal.confidence,
            "position_size": float(signal.position_size.iloc[-1])
        }


def cleanup_ml_resources():
    """MEM-002 FIX: 清理 ML 資源"""
    if hasattr(get_ml_signal, '_ensemble'):
        del get_ml_signal._ensemble
    import gc
    gc.collect()

def generate_report():
    print_header("ALPHA-1 FUND MANAGER BRIEFING")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 1. Macro
    macro = get_macro_report()
    if macro:
        print_header("MACRO MARKET DIAGNOSTIC")
        print(f"Market Verdict: {Colors.BOLD}{macro['verdict']}{Colors.ENDC}")
        print(f"Risk Score:     {macro['risk_score']}/100")
        print(f"Valuation:      {macro['valuation_status']}")
        print("Key Factors:")
        for r in macro['reasons']:
            print(f" - {r}")
    
    # 2. Portfolio Focus (Watchlist)
    watchlist = ["AAPL", "NVDA", "TSLA", "MSFT"]
    print_header("WATCHLIST ANALYSIS")
    
    print(f"{'TICKER':<8} {'PRICE':<10} {'INT. VAL':<10} {'MARGIN':<10} {'VALUATION':<10} {'ML SIGNAL':<12} {'REGIME':<10}")
    print("-" * 85)
    
    for ticker in watchlist:
        val = get_valuation(ticker)
        if not val:
            print(f"{ticker:<8} {'N/A':<10}")
            continue
            
        ml = get_ml_signal(ticker)
        ml_disp = "N/A"
        regime = "N/A"
        if ml:
            sig = ml['signal']
            color = Colors.GREEN if sig > 0.3 else (Colors.FAIL if sig < -0.3 else Colors.WARNING)
            ml_disp = f"{color}{sig:+.2f}{Colors.ENDC}"
            regime = ml['regime']

        # Format rows
        mos = val['margin_of_safety']
        mos_str = f"{mos:+.1%}"
        mos_color = Colors.GREEN if mos > 0.1 else (Colors.FAIL if mos < -0.1 else Colors.WARNING)
        
        print(f"{ticker:<8} ${val['current_price']:<9.2f} ${val['composite_value']:<9.2f} {mos_color}{mos_str:<10}{Colors.ENDC} {val['status']:<10} {ml_disp:<21} {regime:<10}")

    print("\n" + "="*60)
    print("END OF BRIEFING")
    print("="*60)

if __name__ == "__main__":
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import pandas as pd # Ensure pandas loaded
    generate_report()
