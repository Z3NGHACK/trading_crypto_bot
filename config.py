import os
from dotenv import load_dotenv

load_dotenv()

# Simple configuration without dataclasses
EXCHANGE_ID = 'binance'
API_KEY = os.getenv('EXCHANGE_API_KEY', 'test_key')
API_SECRET = os.getenv('EXCHANGE_API_SECRET', 'test_secret')
SANDBOX_MODE = True

TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT']
PRIMARY_TIMEFRAME = '15m'

print("Configuration loaded successfully")