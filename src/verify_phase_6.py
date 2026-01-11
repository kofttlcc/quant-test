
import os
import subprocess
import sys

def run_script(script_path):
    print(f"\n{'='*60}")
    print(f"Running: {script_path}")
    print(f"{'='*60}")
    try:
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"✅ {script_path} Passed")
        return True
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(e.stderr)
        print(f"❌ {script_path} Failed")
        return False

def main():
    root = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        "models/verify_sentinel.py",
        "models/verify_valuation.py",
        "models/verify_backtest.py",
        "models/ml/verify_ml.py"
    ]
    
    success_count = 0
    for script in scripts:
        path = os.path.join(root, script)
        if run_script(path):
            success_count += 1
            
    print(f"\n{'='*60}")
    print(f"Phase 6 Verification Summary: {success_count}/{len(scripts)} Passed")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
