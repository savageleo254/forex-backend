import pandas as pd
from .prophet_model import ProphetModel

def backtest_prophet(train_df, test_df):
    model = ProphetModel()
    model.fit(train_df)
    forecast = model.predict(test_df[['ds']])
    forecast = forecast.set_index('ds')
    actual = test_df.set_index('ds')
    merged = forecast.join(actual[['y']], how='left')
    merged['error'] = merged['y'] - merged['yhat']
    mae = merged['error'].abs().mean()
    return {
        "mae": mae,
        "forecast": merged.reset_index().to_dict(orient='records')
    }