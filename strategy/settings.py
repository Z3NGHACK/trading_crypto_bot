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
MAX_POSITION_SIZE = 0.2  # 20% of portfolio per trade
STOP_LOSS_PERCENT = 0.02  # 2% stop loss
TAKE_PROFIT_PERCENT = 0.04 # 4% take profit
MAX_OPEN_TRADES = 100 # Increased to allow more trades
MIN_RISK_REWARD_RATIO = 2.0 # Minimum 2:1 risk-reward ratio
LEVERAGE = 50  # 1x for spot; increase for futures (if switched)

# Strategy Parameters
MIN_VOLUME_RATIO = 1.5
ORDER_BLOCK_LOOKBACK = 50
STRUCTURE_BREAK_THRESHOLD = 0.001
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70