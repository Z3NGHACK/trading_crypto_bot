import ccxt
from config import EXCHANGE_ID, API_KEY, API_SECRET, SANDBOX_MODE

class ExchangeConnector:
    def __init__(self):
        exchange_class = getattr(ccxt, EXCHANGE_ID)
        self.exchange = exchange_class({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })
        
        if SANDBOX_MODE:
            self.exchange.set_sandbox_mode(True)
    
    def fetch_ohlcv(self, symbol, timeframe, limit=500):
        '''Fetch OHLCV data'''
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_balance(self):
        '''Get account balance'''
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def fetch_order_book(self, symbol, limit=10):
        '''Fetch order book for order flow analysis'''
        try:
            return self.exchange.fetch_order_book(symbol, limit=limit)
        except Exception as e:
            print(f"Error fetching order book for {symbol}: {e}")
            return None