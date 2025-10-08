import os
from dotenv import load_dotenv

load_dotenv()

# Exchange Configuration
EXCHANGE_ID = "binance"
API_KEY = os.getenv("EXCHANGE_API_KEY")
API_SECRET = os.getenv("EXCHANGE_API_SECRET")
SANDBOX_MODE = os.getenv("SANDBOX_MODE", "true").lower() == "true"

# Trading Parameters
TRADING_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "ADA/USDT",
    "BNB/USDT",
    "XRP/USDT",
    "DOGE/USDT",
    "LINK/USDT",
    "DOT/USDT",
    "UNI/USDT",
]
TIMEFRAMES = ["5m", "15m", "1h", "4h"]
PRIMARY_TIMEFRAME = "15m"
ANALYSIS_INTERVAL = 60  # seconds

# Risk Management
MAX_POSITION_RISK = 0.02  # 2% of portfolio per trade
MAX_OPEN_TRADES = 3
MAX_PORTFOLIO_RISK = 0.06  # 6% total portfolio risk
STOP_LOSS_ATR_MULTIPLIER = 2.0
TAKE_PROFIT_RATIO = 2.0  # Risk:Reward ratio
LEVERAGE = 10
MAX_LEVERAGE = 20

# Strategy Parameters
ORDER_BLOCK_LOOKBACK = 50
STRUCTURE_BREAK_THRESHOLD = 0.001
VOLUME_SPIKE_THRESHOLD = 2.0
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_MIDLINE = 50
EMA_FAST = 9
EMA_MEDIUM = 21
EMA_SLOW = 50
ATR_PERIOD = 14
ATR_MULTIPLIER = 2.0
MIN_VOLUME_RATIO = 1.5
VOLUME_MA_PERIOD = 20
CONFIDENCE_THRESHOLD = 0.6
MIN_CONFIRMATIONS = 2

# Monitoring
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PERFORMANCE_UPDATE_INTERVAL = 30  # seconds


def validate_environment():
    """Validate environment configuration"""
    if not API_KEY or not API_SECRET:
        raise ValueError(
            "Missing required environment variables: EXCHANGE_API_KEY and EXCHANGE_API_SECRET\n"
            "Please set them in your .env file or environment variables."
        )

    return {
        "exchange": {
            "api_key_set": bool(API_KEY),
            "api_secret_set": bool(API_SECRET),
            "sandbox_mode": SANDBOX_MODE,
        },
        "trading": {
            "pairs_configured": len(TRADING_PAIRS),
            "primary_timeframe": PRIMARY_TIMEFRAME,
        },
    }


def get_config_summary():
    """Get a summary of the current configuration"""
    return {
        "exchange": {
            "id": EXCHANGE_ID,
            "sandbox": SANDBOX_MODE,
            "type": "future",
        },
        "trading": {
            "pairs": TRADING_PAIRS,
            "timeframe": PRIMARY_TIMEFRAME,
            "analysis_interval": ANALYSIS_INTERVAL,
        },
        "risk_management": {
            "position_risk": f"{MAX_POSITION_RISK * 100}%",
            "max_trades": MAX_OPEN_TRADES,
            "leverage": f"{LEVERAGE}x",
            "risk_reward": f"1:{TAKE_PROFIT_RATIO}",
        },
        "strategy": {
            "confidence_threshold": f"{CONFIDENCE_THRESHOLD * 100}%",
            "rsi_levels": f"{RSI_OVERSOLD}/{RSI_OVERBOUGHT}",
            "order_block_lookback": ORDER_BLOCK_LOOKBACK,
        },
    }


def get_leverage():
    """Get configured leverage with safety checks"""
    return min(LEVERAGE, MAX_LEVERAGE)


def is_sandbox_mode():
    """Check if running in sandbox mode"""
    return SANDBOX_MODE


def get_trading_type():
    """Get the trading type"""
    return "future"


# Initialize and validate on import
try:
    ENV_STATUS = validate_environment()
    CONFIG_SUMMARY = get_config_summary()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise
