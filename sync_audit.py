import os
from pathlib import Path

EXPECTED_FILES = {
    "main.py",
    ".env",
    "requirements.txt",
    "validate_all.py",
    "validate_modules.py",
    "telegram_test_alert.py",
    "print_chat_id.py",
    "signal/entry_signal.json",
    "logs/",
    "bot_engine/__init__.py",
    "bot_engine/fusion_engine.py",
    "bot_engine/smc_engine.py",
    "forecast_engine/__init__.py",
    "forecast_engine/informer_stub.py",
    "alerts/__init__.py",
    "alerts/telegram_alerts.py",
    "journal/__init__.py",
    "journal/logger.py",
}

def list_all_files(base_path):
    all_files = set()
    for root, dirs, files in os.walk(base_path):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), base_path)
            all_files.add(rel_path.replace("\\", "/"))
    return all_files

def audit_sync(base_dir="."):
    print("🔍 Scanning project structure...\n")

    actual_files = list_all_files(base_dir)
    expected = set(EXPECTED_FILES)

    missing = expected - actual_files
    extra = actual_files - expected

    print("📁 Expected Files:")
    for f in sorted(expected):
        print(f"  ✅ {f}" if f in actual_files else f"  ❌ {f}")

    print("\n🗂️ Actual Files in Project:")
    for f in sorted(actual_files):
        prefix = "✅" if f in expected else "🟡"
        print(f"  {prefix} {f}")

    print("\n📉 MISSING FILES:")
    if missing:
        for f in sorted(missing):
            print(f"  ❌ {f}")
    else:
        print("  ✅ None")

    print("\n📈 UNEXPECTED (EXTRA) FILES:")
    if extra:
        for f in sorted(extra):
            print(f"  🟡 {f}")
    else:
        print("  ✅ None")

    # Sync Health Summary
    if not missing and not extra:
        print("\n✅ SYNC STATUS: FULLY IN SYNC")
    elif not missing:
        print("\n🟡 SYNC STATUS: IN SYNC (with extras)")
    else:
        print("\n🚨 SYNC STATUS: BROKEN — fix missing modules")

# Run it
if __name__ == "__main__":
    audit_sync(".")
