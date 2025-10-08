import pandas as pd
import os
from data.exchange import ExchangeConnector
from config.settings import TRADING_PAIRS, TIMEFRAMES

class DataFetcher:
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.data_path = 'data_storage'
        os.makedirs(self.data_path, exist_ok=True)
    
    def fetch_and_store(self, symbol, timeframe, limit=500):
        '''Fetch OHLCV data and store locally'''
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit)
        if ohlcv:
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            file_path = os.path.join(self.data_path, f"{symbol.replace('/', '_')}_{timeframe}.csv")
            df.to_csv(file_path)
            return df
        return None
    
    def load_local_data(self, symbol, timeframe):
        '''Load data from local storage'''
        file_path = os.path.join(self.data_path, f"{symbol.replace('/', '_')}_{timeframe}.csv")
        if os.path.exists(file_path):
            return pd.read_csv(file_path, index_col='timestamp', parse_dates=True)
        return None