import json
import os
from datetime import datetime
from fastapi import FastAPI, Body, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

app = FastAPI(
    title="EA Override API",
    description="API for sending real-time override commands to MT5 EA",
    version="1.0.0"
)

# Config - move sensitive stuff to env vars for real deployment
MT5_FILES_PATH = r"C:\OverrideCommands"
VALID_ACTIONS = {"close", "partial_close", "move_sl", "move_tp", "hedge"}
API_KEY = "savage"  # CHANGE THIS TO STRONG ENV VAR in prod!

# Ensure override folder exists, fail fast if not writable
try:
    os.makedirs(MT5_FILES_PATH, exist_ok=True)
    test_path = os.path.join(MT5_FILES_PATH, ".__write_test__")
    with open(test_path, "w") as f:
        f.write("test")
    os.remove(test_path)
except Exception as e:
    logging.critical(f"Cannot write to override folder {MT5_FILES_PATH}: {e}")
    raise RuntimeError(f"Permission or path issue on {MT5_FILES_PATH}")

# CORS - lock this down to trusted domains in prod
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in prod
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Logger setup (optional)
logging.basicConfig(level=logging.INFO)

@app.post("/trade/override")
async def trade_override(
    trade_id: str = Body(..., embed=True),
    action: str = Body(..., embed=True),
    x_api_key: str = Header(None)
):
    # 🔐 API key check (case sensitive)
    if x_api_key != API_KEY:
        logging.warning(f"Unauthorized access attempt with API key: {x_api_key}")
        raise HTTPException(status_code=403, detail="Unauthorized 🔒 Invalid API Key")

    # 🛡️ Validate action strictly
    if action not in VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid action: {action}")

    # Sanitize trade_id: simple alphanumeric check to prevent path issues
    if not trade_id.isalnum():
        raise HTTPException(status_code=400, detail="trade_id must be alphanumeric")

    timestamp = datetime.utcnow().isoformat()
    override_command = {
        "trade_id": trade_id,
        "action": action,
        "timestamp": timestamp
    }

    file_path = os.path.join(MT5_FILES_PATH, f"override_{trade_id}.json")

    # 🚫 Prevent accidental overwrite - this is critical
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail="⚠️ Override already exists for this trade ID")

    try:
        # Write override file atomically
        temp_file = file_path + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(override_command, f)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_file, file_path)  # atomic move to avoid race conditions

        # Append to override journal safely (could use a DB for scale)
        with open("override_journal.csv", "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp},{trade_id},{action}\n")

        logging.info(f"Override issued for trade_id={trade_id}, action={action}")

        return {
            "status": "✅ Override issued",
            "command": override_command,
            "file_path": file_path
        }

    except Exception as e:
        logging.error(f"Error writing override file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"❌ Error writing file: {e}")

# 🧪 Health check with minimal info, no sensitive data
@app.get("/healthcheck")
def healthcheck():
    folder_accessible = os.access(MT5_FILES_PATH, os.W_OK | os.R_OK)
    return JSONResponse(content={
        "status": "✅ API running",
        "override_folder": MT5_FILES_PATH,
        "folder_accessible": folder_accessible
    })
