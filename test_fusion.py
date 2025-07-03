import sys
import os

# Ensure the project root is in the import path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from bot_engine.fusion_engine import fuse_signals

smc_ctx = {"bias_score": 0.62}
forecast = 0.28
sentiment = {"sentiment_score": 0.41}
symbol = "EURUSD"
timeframe = "M5"

result = fuse_signals(smc_ctx, forecast, sentiment, symbol=symbol, timeframe=timeframe)
print(result)