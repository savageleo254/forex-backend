from bot_engine.fusion_engine import fuse_signals

def test_fuse_signals_basic():
    smc_ctx = {"bias_score": 0.5}
    forecast = 0.3
    sentiment = {"sentiment_score": 0.2}
    result = fuse_signals(smc_ctx, forecast, sentiment)
    assert "fused_score" in result
    assert isinstance(result["fused_score"], float)
    print("test_fuse_signals_basic passed.")

def test_fuse_signals_weights():
    smc_ctx = {"bias_score": 1}
    forecast = 0
    sentiment = {"sentiment_score": 0}
    result = fuse_signals(smc_ctx, forecast, sentiment)
    # If only SMC has value, fused_score should equal SMC's weight
    assert abs(result["fused_score"] - 0.5) < 1e-6
    print("test_fuse_signals_weights passed.")

if __name__ == "__main__":
    test_fuse_signals_basic()
    test_fuse_signals_weights()
    print("All tests passed!")