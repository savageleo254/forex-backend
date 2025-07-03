import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,  # Correct logging level, not a string
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("logs/backend.log"),
        logging.StreamHandler()
    ]
)

logging.info("Backend started")
logging.info("Trade executed!")
logging.warning("This is a warning")
logging.error("Failed to connect to MetaTrader!")