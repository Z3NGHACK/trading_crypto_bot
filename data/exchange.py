import ccxt
from config.settings import *

class ExchangeConnector:
    def __init__(self):
        exchange_class = getattr(ccxt, EXCHANGE_ID)
        self.exchange = exchange_class({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}  # Changed to spot trading
        })
        
        if SANDBOX_MODE:
            self.exchange.set_sandbox_mode(True)
    
    def fetch_ohlcv(self, symbol, timeframe, limit=500):
        '''Fetch OHLCV data'''
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
    def get_balance(self):
        '''Get account balance'''
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
    
    def place_order(self, symbol, order_type, side, amount, price=None):
        '''Place an order'''
        try:
            if order_type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount)
            else:
                order = self.exchange.create_limit_order(symbol, side, amount, price)
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None