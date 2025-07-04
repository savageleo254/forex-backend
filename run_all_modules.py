# run_all_modules.py
"""
Run all Python modules in forex-backend to detect missing files, errors, or import issues.
"""

import os
import traceback
import importlib.util

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXCLUDE = {"venv", "__pycache__", "logs", "signal", "journal", "tests", ".git", "notebooks"}

def find_py_files(base):
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in EXCLUDE]
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def run_and_check(file_path):
    rel_path = os.path.relpath(file_path, ROOT_DIR)
    print(f"\n🧪 Testing: {rel_path}")
    try:
        spec = importlib.util.spec_from_file_location("mod", file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print(f"✅ SUCCESS: {rel_path}")
    except Exception:
        print(f"❌ ERROR in {rel_path}:")
        traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Scanning for Python modules...\n")
    for py_file in find_py_files(ROOT_DIR):
        run_and_check(py_file)
