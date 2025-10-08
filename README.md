Trading Crypto Bot
A Python-based trading bot for cryptocurrency markets using technical analysis, market structure, and order block detection. Runs on Binance Testnet with real-time data, manages a $10,000 portfolio, and displays signals in a web interface.
Features

Fetches real-time market data via CCXT (Binance Testnet).
Performs technical analysis (EMA, RSI, ATR).
Detects market structure and order blocks.
Generates BUY/SELL/HOLD signals with confidence scores.
Manages risk (2% per trade, stop-loss, take-profit).
Visualizes portfolio and signals via a web interface (monitor.html).
Sandbox mode for testing (no real funds).

Project Structure
trading_crypto_bot/
├── config/
│   └── settings.py        # Configuration (trading pairs, leverage, etc.)
├── data/
│   └── cache.txt         # Cache for monitor (excluded in .gitignore)
├── logs/
│   └── market_analysis.log # Bot logs (excluded in .gitignore)
├── strategy/
│   └── signals.py        # Signal generation logic
├── main.py               # Main bot script
├── monitor.html          # Web interface for monitoring signals
├── requirements.txt      # Python dependencies
├── .gitignore            # Excludes sensitive files
└── .env                  # API keys (excluded in .gitignore)

Prerequisites

Python 3.8+
Git
Binance Testnet account (for API keys)

Setup

Clone the Repository:
git clone https://github.com/Z3NGHACK/trading_crypto_bot.git
cd trading_crypto_bot


Create and Activate Virtual Environment:
python -m venv trading_bot_env


Windows:trading_bot_env\Scripts\activate


Linux/Mac:source trading_bot_env/bin/activate




Install Dependencies:
pip install -r requirements.txt


Set Up API Keys:

Create a .env file in the project root:echo EXCHANGE_API_KEY=your_api_key_here > .env
echo EXCHANGE_API_SECRET=your_api_secret_here >> .env


Get keys from Binance Testnet.


Run the Bot:
python main.py


Start Web Server:
python -m http.server 8000


View Monitor:

Open http://localhost:8000/monitor.html in a browser.
Displays latest signal per token (10 tokens: BTC/USDT, ETH/USDT, etc.), including Signal (BUY/SELL/HOLD), Market Size ($), and Total Profit.



Usage

Bot: Analyzes 10 tokens (BTC, ETH, SOL, ADA, BNB, XRP, DOGE, LINK, DOT, UNI) every 60s on Binance Testnet (15m timeframe).
Signals: BUY/SELL (50%+ confidence, ~$10,000 market size with 10x leverage) or HOLD ($0 market size).
Portfolio: $10,000 initial capital, max 3 open trades (2% risk per trade, $200 max loss).
Monitor: Updates every 2s, shows Signal (green/red/gray), Market Size, and Total Profit. New rows highlight green.

Troubleshooting

Table shows "undefined" or code:
Check data/cache.txt:type data\cache.txt


Expected: 2025-10-07 16:34:00|BTC/USDT|SELL|Open=123830.01|...|MarketSize=10000.00|...
If empty/corrupted, clear it:del data\cache.txt




Verify main.py and monitor.html versions (see artifacts).


No trades:
Check MAX_OPEN_TRADES in config/settings.py (default: 3).
Increase to 5 for more positions:MAX_OPEN_TRADES = 5




Log errors:type logs\market_analysis.log | findstr "Error"


Testnet pairs:python -c "from data.exchange import ExchangeConnector; print(list(ExchangeConnector().exchange.load_markets().keys()))"


Replace unsupported pairs in config/settings.py.



Notes

Use SANDBOX_MODE = True in config/settings.py for testing.
Leverage (default: 10x) amplifies market size (~$10,000 per trade). Set LEVERAGE = 1 for spot trading.
Accuracy: ~60% (backtests). Verify signals vs. TradingView (Binance Testnet, 15m).

Contributing

Fork the repository.
Create a branch: git checkout -b feature-name.
Commit changes: git commit -m "Add feature".
Push: git push origin feature-name.
Open a pull request.

License
MIT License
