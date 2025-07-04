# PRO VETERAN+++ FIX PATCHES BASED ON TEST REPORT
# Reference: test report.txt | Date: 2025-07-04
# Authoritative Patch Script for Savage Leo QuantOps Stack

import os
import shutil

# === 1. Fix Python 3.13 Incompatibility: Replace Python 3.13 with 3.11 ===
# This issue causes async signal errors, breaking most modules.
# Auto action: alert user and exit if version mismatch

def check_python_version():
    import sys
    if not sys.version.startswith("3.11"):
        raise RuntimeError("❌ Savage Leo requires Python 3.11. Downgrade from 3.13 ASAP.")

# === 2. Rename `signal/` folder to avoid shadowing built-in signal module ===
# Critical fix: resolves import errors in FastAPI, AnyIO, asyncio

def rename_signal_folder():
    if os.path.exists("signal"):
        os.rename("signal", "signal_custom")
        print("✅ Renamed 'signal/' to 'signal_custom/' to avoid conflict with Python stdlib.")

# === 3. Patch missing dependencies: plotly, feedparser, schedule ===
# Fixes: dashboard apps, news feed parser, auto schedulers

def install_required_dependencies():
    os.system("pip install plotly feedparser schedule")
    print("✅ Installed: plotly, feedparser, schedule")

# === 4. Fix incorrect import in test_fusion.py and python test_fusion.py ===
# Invalid argument `symbol=` to `fuse_signals()`

def patch_test_fusion():
    path = "test_fusion.py"
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        content = content.replace("symbol=symbol, timeframe=timeframe", "symbol, timeframe")
        with open(path, "w") as f:
            f.write(content)
        print("✅ Patched: test_fusion.py to correct fuse_signals() args")

# === 5. Fix fusion_engine.py typo: decide_entry_t_ => decide_entry_type ===


def patch_fusion_typo():
    path = "bot_engine/fusion_engine.py"
    if os.path.exists(path):
        with open(path, "r") as f:
            code = f.read()
        code = code.replace("decide_entry_t_", "decide_entry_type")
        with open(path, "w") as f:
            f.write(code)
        print("✅ Patched typo in fusion_engine.py")

# === 6. Fix wrong import in multisymbol_manager.py ===
# Wrong module path: signal_fusion doesn't exist


def patch_multisymbol_import():
    path = "bot_engine/multisymbol_manager.py"
    if os.path.exists(path):
        with open(path, "r") as f:
            code = f.read()
        code = code.replace("from bot_engine.signal_fusion", "from bot_engine.fusion_engine")
        with open(path, "w") as f:
            f.write(code)
        print("✅ Fixed import in multisymbol_manager.py")

# === 7. Auto-fix missing parent imports in forecast_engine/backtest.py ===

def fix_backtest_import():
    path = "forecast_engine/backtest.py"
    if os.path.exists(path):
        with open(path, "r") as f:
            code = f.read()
        code = code.replace("from .prophet_model", "from forecast_engine.prophet_model")
        with open(path, "w") as f:
            f.write(code)
        print("✅ Fixed relative import in backtest.py")


if __name__ == "__main__":
    check_python_version()
    rename_signal_folder()
    install_required_dependencies()
    patch_fusion_typo()
    patch_test_fusion()
    patch_multisymbol_import()
    fix_backtest_import()
    print("\n🏁 All Pro Veteran+++ auto-fixes complete. Rerun `python run_all_modules.py` to verify.")
