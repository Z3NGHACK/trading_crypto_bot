import os
import json
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/settings.log',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console)

load_dotenv()

# Exchange Configuration
EXCHANGE_ID = os.getenv('EXCHANGE_ID', 'binance')
API_KEY = os.getenv('EXCHANGE_API_KEY')
API_SECRET = os.getenv('EXCHANGE_API_SECRET')
SANDBOX_MODE = os.getenv('SANDBOX_MODE', 'true').lower() == 'true'

# Trading Parameters
try:
    TRADING_PAIRS_RAW = os.getenv('TRADING_PAIRS', '["BTC/USDT","ETH/USDT","SOL/USDT","ADA/USDT","BNB/USDT","XRP/USDT","DOGE/USDT","LINK/USDT","DOT/USDT","UNI/USDT"]')
    logging.debug(f"Raw TRADING_PAIRS value: {TRADING_PAIRS_RAW}")
    TRADING_PAIRS = json.loads(TRADING_PAIRS_RAW)
except json.JSONDecodeError as e:
    logging.error(f"Failed to parse TRADING_PAIRS: {e} - Raw value: {TRADING_PAIRS_RAW}")
    TRADING_PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT", "BNB/USDT", "XRP/USDT", "DOGE/USDT", "LINK/USDT", "DOT/USDT", "UNI/USDT"]

try:
    TIMEFRAMES_RAW = os.getenv('TIMEFRAMES', '["5m","15m","1h","4h"]')
    logging.debug(f"Raw TIMEFRAMES value: {TIMEFRAMES_RAW}")
    TIMEFRAMES = json.loads(TIMEFRAMES_RAW)
except json.JSONDecodeError as e:
    logging.error(f"Failed to parse TIMEFRAMES: {e} - Raw value: {TIMEFRAMES_RAW}")
    TIMEFRAMES = ["5m", "15m", "1h", "4h"]

PRIMARY_TIMEFRAME = os.getenv('PRIMARY_TIMEFRAME', '15m')

# Risk Management
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 10000))
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.02))
STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', 0.02))
TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', 0.04))
MAX_OPEN_TRADES = int(os.getenv('MAX_OPEN_TRADES', 10))
MIN_RISK_REWARD_RATIO = float(os.getenv('MIN_RISK_REWARD_RATIO', 2.0))
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.8))
LEVERAGE = int(os.getenv('LEVERAGE', 1))
MAX_RISK_PER_TRADE = float(os.getenv('MAX_RISK_PER_TRADE', 0.1))

# Strategy Parameters
MIN_VOLUME_RATIO = float(os.getenv('MIN_VOLUME_RATIO', 1.5))
ORDER_BLOCK_LOOKBACK = int(os.getenv('ORDER_BLOCK_LOOKBACK', 50))
STRUCTURE_BREAK_THRESHOLD = float(os.getenv('STRUCTURE_BREAK_THRESHOLD', 0.001))
RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

logging.info("Configuration loaded successfully")