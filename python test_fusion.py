import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()
from bot_engine.fusion_engine import fuse_signals

smc_ctx = {"bias_score": 0.62}
forecast = 0.28
sentiment = {"sentiment_score": 0.41}
symbol = "EURUSD"
timeframe = "M5"

result = fuse_signals(sentiment, forecast, structure, market_state)
print(result)