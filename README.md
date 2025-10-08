Trading Bot
A Python-based trading bot for cryptocurrency markets using technical analysis and order block detection.
Setup

Clone the repository.
Create a virtual environment: python -m venv venv
Activate the virtual environment:
Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate


Install dependencies: pip install -r requirements.txt
Create a .env file with your exchange API keys:EXCHANGE_API_KEY=your_api_key_here
EXCHANGE_API_SECRET=your_api_secret_here


Run the bot: python main.py

Features

Fetches real-time market data using CCXT
Performs technical analysis (EMA, RSI, ATR, etc.)
Detects market structure and order blocks
Generates trading signals based on multiple factors
Manages risk and portfolio
Visualizes analysis with Plotly

Notes

Use sandbox mode (SANDBOX_MODE = True) for testing.
Ensure you have valid API keys for your exchange.



cmd too run 

cd C:\Users\NATO123\web\testing\ai-crypto
python -m http.server 8000


cd C:\Users\NATO123\web\testing\ai-crypto
trading_bot_env\Scripts\activate
python main.py

http://localhost:8000/monitor.html - link