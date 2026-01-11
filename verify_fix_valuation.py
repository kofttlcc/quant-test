
import requests
import json
import time

def verify_valuation(ticker):
    print(f"\n--- Verifying {ticker} ---")
    try:
        url = f"http://localhost:5001/api/v1/stock/valuation?ticker={ticker}"
        start = time.time()
        res = requests.get(url, timeout=10)
        data = res.json()
        elapsed = time.time() - start
        
        if "error" in data:
            print(f"❌ Error: {data['error']}")
            return
            
        details = data.get("details", {})
        print(f"✅ Status Code: {res.status_code} ({elapsed:.2f}s)")
        print(f"   Company: {data.get('company_name', 'N/A')}")
        print(f"   Fair Value: ${data.get('fair_value')}")
        print(f"   WACC: {details.get('WACC')} (Should be dynamic)")
        print(f"   Growth: {details.get('Growth')} (Should be optimized)")
        print(f"   Models: {data.get('models')}")
        
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    verify_valuation("NVDA") # High Growth
    verify_valuation("KO")   # Stable Dividend
    verify_valuation("TSLA") # Volatile
