import json
import os

# Replace this with your actual MT5 'Files' folder path
MT5_FILES_PATH = r"C:\Users\pc\AppData\Roaming\MetaQuotes\Terminal\776D2ACDFA4F66FAF3C8985F75FA9FF6\MQL5\Files"

override_command = {
    "trade_id": "12345",
    "action": "close"
}

file_path = os.path.join(MT5_FILES_PATH, "override_12345.json")

try:
    with open(file_path, "w") as f:
        json.dump(override_command, f)
    print(f"✅ File written: {file_path}")
except Exception as e:
    print(f"❌ Failed to write file: {e}")
