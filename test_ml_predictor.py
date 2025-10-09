import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)
from analysis.ml_predictor import MLPredictor
from data.exchange import ExchangeConnector

# Fetch sample data
exchange = ExchangeConnector()
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '15m', limit=500)
df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df.set_index("timestamp", inplace=True)

mlp = MLPredictor(df)
print(mlp.predict_next())