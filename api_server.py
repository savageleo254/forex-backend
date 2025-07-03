from fastapi import FastAPI, Query
from pydantic import BaseModel
from bot_engine.fusion_engine import fuse_signals

app = FastAPI()

class SignalInput(BaseModel):
    smc_score: float
    forecast: float
    sentiment_score: float
    symbol: str = "EURUSD"
    timeframe: str = "M5"

@app.post("/fuse")
def fuse(input: SignalInput):
    smc_ctx = {"bias_score": input.smc_score}
    sentiment = {"sentiment_score": input.sentiment_score}
    result = fuse_signals(smc_ctx, input.forecast, sentiment, symbol=input.symbol, timeframe=input.timeframe)
    return result