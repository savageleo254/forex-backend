import os
import importlib.util
from pathlib import Path

# === Expected modules and functions ===
REQUIRED_MODULES = {
    "bot_engine.fusion_engine": "fuse_signals",
    "bot_engine.smc_engine": "analyze_market_state",
    "forecast_engine.informer_stub": "forecast_signal",
    "alerts.telegram_alerts": "maybe_alert",
    "journal.logger": "log_fusion_result"
}

REQUIRED_PATHS = [
    "bot_engine",
    "alerts",
    "forecast_engine",
    "journal",
    "signal"
]

def check_importable(module_path, fn=None):
    try:
        module = importlib.import_module(module_path)
        if fn and not hasattr(module, fn):
            print(f"❌ Function `{fn}` missing in {module_path}")
            return False
        print(f"✅ Module `{module_path}` import OK")
        return True
    except Exception as e:
        print(f"❌ Failed to import `{module_path}` → {str(e)}")
        return False

def check_init_file(folder_path):
    init_path = os.path.join(folder_path, "__init__.py")
    if not os.path.isfile(init_path):
        print(f"⚠️  Missing __init__.py in `{folder_path}`")
        return False
    return True

def check_path_exists(path):
    if not os.path.exists(path):
        print(f"❌ Required path missing: `{path}`")
        return False
    return True

def run_module_diagnostics():
    print("🔍 Running module diagnostics...\n")

    all_good = True

    for mod, fn in REQUIRED_MODULES.items():
        ok = check_importable(mod, fn)
        all_good = all_good and ok

    for path in REQUIRED_PATHS:
        if not check_path_exists(path):
            all_good = False
        elif os.path.isdir(path):
            if not check_init_file(path):
                all_good = False

    if all_good:
        print("\n✅ All modules and paths look good. You're clear to run main.py.")
    else:
        print("\n🚨 One or more issues found. Fix them before running main.py.")

if __name__ == "__main__":
    run_module_diagnostics()
