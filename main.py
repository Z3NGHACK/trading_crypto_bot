import logging
import time
import pandas as pd
from data.exchange import ExchangeConnector
from data.fetcher import DataFetcher
from execution.trader import Trader
from config.settings import TRADING_PAIRS, PRIMARY_TIMEFRAME, RSI_OVERSOLD, RSI_OVERBOUGHT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/main.log'),
        logging.StreamHandler()
    ]
)

class TradingBot:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchange = ExchangeConnector()
        self.fetcher = DataFetcher()
        self.trader = Trader(self.exchange, self.fetcher)
        self.logger.info("Trading bot initialized")

    def calculate_rsi(self, df, periods=14):
        try:
            close = df['close']
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return None

    def generate_signal(self, symbol, df):
        try:
            rsi = self.calculate_rsi(df)
            if rsi is None:
                return 'HOLD', 0.5
            latest_rsi = rsi.iloc[-1]
            if latest_rsi < RSI_OVERSOLD:
                return 'BUY', 0.85
            elif latest_rsi > RSI_OVERBOUGHT:
                return 'SELL', 0.85
            else:
                return 'HOLD', 0.5
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return 'HOLD', 0.5

    def run(self):
        self.logger.info("Trading bot started")
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                self.logger.info(f"Starting cycle {cycle_count}")
                for symbol in TRADING_PAIRS:
                    df = self.fetcher.fetch_and_store(symbol, PRIMARY_TIMEFRAME, limit=100)
                    if df.empty:
                        self.logger.warning(f"No data for {symbol}")
                        continue
                    signal, confidence = self.generate_signal(symbol, df)
                    self.logger.info(f"Generated signal for {symbol}: {signal} (Confidence: {confidence})")
                    if signal in ['BUY', 'SELL']:
                        price = self.exchange.get_current_price(symbol)  # Changed from self.fetcher to self.exchange
                        if price:
                            self.trader.execute_trade(symbol, signal, confidence, price)
                        else:
                            self.logger.warning(f"Failed to fetch price for {symbol}, skipping trade")
                self.logger.info(f"Completed cycle {cycle_count}. Sleeping for 30 seconds (testing)")
                time.sleep(30)  # Reduced for testing; restore to 15 * 60 for production
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()