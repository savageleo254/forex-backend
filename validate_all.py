import os
import importlib
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === Define module/function/paths ===
MODULES = {
    "bot_engine.fusion_engine": "fuse_signals",
    "bot_engine.smc_engine": "analyze_market_state",
    "forecast_engine.informer_stub": "forecast_signal",
    "alerts.telegram_alerts": "maybe_alert",
    "journal.logger": "log_fusion_result"
}

REQUIRED_DIRS = [
    "bot_engine", "alerts", "forecast_engine", "journal", "logs", "signal"
]

ENV_KEYS = [
    "TELEGRAM_TOKEN",
    "TELEGRAM_CHAT_ID",
    "SENTIMENT_WEIGHT",
    "FORECAST_WEIGHT",
    "SMC_WEIGHT"
]

AUTO_STUBS = {
    "bot_engine.smc_engine": """def analyze_market_state(ohlc, symbol, timeframe):\n    return {"bias": "bullish"}\n""",
    "forecast_engine.informer_stub": """def forecast_signal(symbol, timeframe, ohlc):\n    return 0.25\n""",
    "alerts.telegram_alerts": """def maybe_alert(result):\n    print("[ALERT]", result['symbol'], result['fused_score'])\n""",
    "journal.logger": """def log_fusion_result(result):\n    print("[LOGGED]", result['symbol'])\n"""
}

# === Helper Utilities ===

def create_stub(module_path, code):
    parts = module_path.split('.')
    py_path = Path("/".join(parts)) .with_suffix(".py")
    py_path.parent.mkdir(parents=True, exist_ok=True)
    if not py_path.exists():
        with open(py_path, 'w') as f:
            f.write(code)
        print(f"🛠️  Created stub: {py_path}")
    else:
        print(f"✅ Stub already exists: {py_path}")

def ensure_init(path):
    init_path = Path(path) / "__init__.py"
    if not init_path.exists():
        init_path.touch()
        print(f"🛠️  Created __init__.py in {path}")

def check_module(mod, fn):
    try:
        m = importlib.import_module(mod)
        if not hasattr(m, fn):
            print(f"❌ `{mod}` loaded but missing function: `{fn}`")
            return False
        print(f"✅ Module `{mod}.{fn}` OK")
        return True
    except Exception as e:
        print(f"❌ Failed to import {mod}: {e}")
        return False

def check_env():
    print("\n🔐 Checking .env keys...")
    missing = []
    for k in ENV_KEYS:
        if os.getenv(k) is None:
            print(f"❌ Missing: {k}")
            missing.append(k)
        else:
            print(f"✅ Found: {k}")
    return missing

def run_validation(auto_fix=True):
    print("🔍 Starting full QuantOps validation...\n")
    all_good = True

    # Check folders & __init__
    for d in REQUIRED_DIRS:
        path = Path(d)
        if not path.exists():
            if auto_fix:
                path.mkdir(parents=True)
                print(f"🛠️  Created missing folder: {d}")
        ensure_init(path)

    # Check modules & generate stubs
    for mod, fn in MODULES.items():
        if not check_module(mod, fn):
            if auto_fix and mod in AUTO_STUBS:
                create_stub(mod, AUTO_STUBS[mod])
                all_good = False
            else:
                all_good = False

    # Check .env keys
    missing_keys = check_env()
    if missing_keys:
        print("\n⚠️ Missing env keys. Add these to your .env:")
        for k in missing_keys:
            print(f"  - {k}")
        all_good = False

    # Final result
    if all_good and not missing_keys:
        print("\n✅ All systems GO. Ready to run `main.py`.")
    else:
        print("\n🚨 Fix the above issues before running main loop.")

# === Entry Point ===
if __name__ == "__main__":
    run_validation(auto_fix=True)
