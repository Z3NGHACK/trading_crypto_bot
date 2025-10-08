import os
from dotenv import load_dotenv

load_dotenv()

# Exchange Configuration
EXCHANGE_ID = 'binance'
API_KEY = os.getenv('EXCHANGE_API_KEY')
API_SECRET = os.getenv('EXCHANGE_API_SECRET')
SANDBOX_MODE = True

# Trading Parameters
TRADING_PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'BNB/USDT', 'XRP/USDT', 'DOGE/USDT', 'LINK/USDT', 'DOT/USDT', 'UNI/USDT']  # 10 tokens
TIMEFRAMES = ['5m', '15m', '1h', '4h']
PRIMARY_TIMEFRAME = '15m'

# Risk Management
MAX_POSITION_SIZE = 0.02
STOP_LOSS_PERCENT = 0.02
TAKE_PROFIT_PERCENT = 0.04
MAX_OPEN_TRADES = 3
MIN_RISK_REWARD_RATIO = 2.0
LEVERAGE = 1  # 1x for spot; increase for futures (if switched)

# Strategy Parameters
MIN_VOLUME_RATIO = 1.5
ORDER_BLOCK_LOOKBACK = 50
STRUCTURE_BREAK_THRESHOLD = 0.001
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70