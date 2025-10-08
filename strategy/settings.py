import os
import json
from dotenv import load_dotenv

load_dotenv()

# Exchange Configuration
EXCHANGE_ID = os.getenv('EXCHANGE_ID')
API_KEY = os.getenv('EXCHANGE_API_KEY')
API_SECRET = os.getenv('EXCHANGE_API_SECRET')
SANDBOX_MODE = os.getenv('SANDBOX_MODE', 'true').lower() == 'true'

# Trading Parameters
TRADING_PAIRS = json.loads(os.getenv('TRADING_PAIRS', '[]'))
TIMEFRAMES = json.loads(os.getenv('TIMEFRAMES', '[]'))
PRIMARY_TIMEFRAME = os.getenv('PRIMARY_TIMEFRAME')

# Risk Management
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 10000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.1))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 0.2))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 0.4))
MAX_OPEN_TRADES = int(os.getenv('MAX_OPEN_TRADES', 10))
MIN_RISK_REWARD_RATIO = float(os.getenv('MIN_RISK_REWARD_RATIO', 4.0))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.8))
LEVERAGE = int(os.getenv('LEVERAGE', 15))
MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.1))

# Strategy Parameters
MIN_VOLUME_RATIO = float(os.getenv('MIN_VOLUME_RATIO', 1.5))
ORDER_BLOCK_LOOKBACK = int(os.getenv('ORDER_BLOCK_LOOKBACK', 50))
STRUCTURE_BREAK_THRESHOLD = float(os.getenv('STRUCTURE_BREAK_THRESHOLD', 0.001))
RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')