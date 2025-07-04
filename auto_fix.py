import sys
if sys.version_info >= (3, 13) or sys.version_info < (3, 11):
    raise RuntimeError("❌ Savage Leo requires Python 3.11.x only. Downgrade to 3.11.")
# auto_fix.py – LLM-Driven Auto Repair Engine for Savage Leo
import os, traceback, json, requests
from datetime import datetime
from dotenv import load_dotenv
import subprocess, tempfile, shutil

# === CONFIG ===
MODEL = "deepseek/deepseek-chat-v3-0324:free"  # or "openai/gpt-4o"
TARGET_FILE = "autonomous_run.py"
PATCH_OUTPUT = "last_ai_fix.txt"
AUTO_APPLY_PATCH = False

# Load environment
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def run_target_script():
    try:
        with open(TARGET_FILE, "r", encoding="utf-8") as f:
            code = f.read()
        exec(code, {})
    except Exception:
        err_trace = traceback.format_exc()
        print("❌ Runtime exception captured.")
        return code, err_trace
    return None, None

def call_llm_for_fix(code, error):
    print("🧠 Sending request to OpenRouter LLM...")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": f"""
You are an elite Python quant systems engineer.

This code crashed:
--- CODE START ---
{code}
--- CODE END ---

Error trace:
--- ERROR ---
{error}
--- ERROR END ---

Return a FULLY FIXED, clean version of the Python script.
ONLY return raw code. No comments, no explanations.
""".strip()
        }]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    fixed_code = response.json()['choices'][0]['message']['content']
    with open(PATCH_OUTPUT, "w", encoding="utf-8") as f:
        f.write(fixed_code)
    return fixed_code

def write_patch(code):
    with open(PATCH_OUTPUT, "w", encoding="utf-8") as f:
        f.write(code)

def apply_patch(new_code: str):
    backup = f"{TARGET_FILE}.bak.{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    shutil.copy(TARGET_FILE, backup)
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.write(new_code)
    print(f"⚡ Patched {TARGET_FILE} ✅ (backup → {backup})")

def notify_patch_event(file, msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    text = f"🛠 Patch Status for `{file}`:\n{msg}"
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    })

# === MAIN LOGIC ===
if __name__ == "__main__":
    code, error = run_target_script()
    if error:
        fixed_code = call_llm_for_fix(code, error)
        write_patch(fixed_code)

        # 🔎 Run tests in isolated temp environment
        with tempfile.TemporaryDirectory() as tmp:
            tmp_file = os.path.join(tmp, TARGET_FILE)
            os.makedirs(os.path.dirname(tmp_file), exist_ok=True)
            with open(tmp_file, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            env = os.environ.copy()
            env["PYTHONPATH"] = f"{tmp}{os.pathsep}{env.get('PYTHONPATH', '')}"
            passed = subprocess.run(["python", "run_tests.py"], env=env).returncode == 0

        if passed and AUTO_APPLY_PATCH:
            apply_patch(fixed_code)
            notify_patch_event(TARGET_FILE, "✅ Tests green – patch auto‑applied")
        elif passed:
            notify_patch_event(TARGET_FILE, "✅ Tests green – patch saved (manual apply)")
        else:
            notify_patch_event(TARGET_FILE, "❌ Tests failed – patch NOT applied")
    else:
        print("✅ No errors detected in target script.")
