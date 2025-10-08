import pandas as pd
import time
import os
import logging
from datetime import datetime

# Import from config
from config import (
    TRADING_PAIRS,
    PRIMARY_TIMEFRAME,
    SANDBOX_MODE,
    get_leverage,
    MAX_POSITION_RISK,
    MAX_OPEN_TRADES,
    STOP_LOSS_ATR_MULTIPLIER,
    TAKE_PROFIT_RATIO,
    CONFIDENCE_THRESHOLD,
    ANALYSIS_INTERVAL,
)

# Import bot components
from data.exchange import ExchangeConnector
from strategy.risk_management import RiskManager
from execution.portfolio import Portfolio
from execution.trader import Trader

# Setup configuration
LEVERAGE = get_leverage()
STOP_LOSS_PERCENT = STOP_LOSS_ATR_MULTIPLIER * 0.01
TAKE_PROFIT_PERCENT = TAKE_PROFIT_RATIO * STOP_LOSS_PERCENT

# Setup logging - FIXED: No emojis, proper encoding
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/market_analysis.log", mode="a", encoding='utf-8'),
        logging.StreamHandler(),  # This will use system encoding
    ],
)

# Cache file
CACHE_FILE = "data/cache.txt"
os.makedirs("data", exist_ok=True)

# Clear cache file on startup
try:
    with open(CACHE_FILE, "w") as f:
        f.write("")
    logging.info(f"Cleared cache file: {CACHE_FILE}")
except Exception as e:
    logging.error(f"Failed to clear cache file: {e}")


class TradingBot:
    def __init__(self, initial_capital=10000):
        self.exchange = ExchangeConnector()
        self.risk_manager = RiskManager(initial_capital)
        self.portfolio = Portfolio(initial_capital)
        self.trader = Trader(self.exchange, self.risk_manager)
        self.running = False
        self.initial_capital = initial_capital

        # Log configuration - FIXED: No emojis
        logging.info("=== Trading Bot Configuration ===")
        logging.info(f"Trading Pairs: {TRADING_PAIRS}")
        logging.info(f"Primary Timeframe: {PRIMARY_TIMEFRAME}")
        logging.info(f"Sandbox Mode: {SANDBOX_MODE}")
        logging.info(f"Leverage: {LEVERAGE}x")
        logging.info(f"Stop Loss: {STOP_LOSS_PERCENT*100:.1f}%")
        logging.info(f"Take Profit: {TAKE_PROFIT_PERCENT*100:.1f}%")
        logging.info(f"Max Open Trades: {MAX_OPEN_TRADES}")
        logging.info(f"Max Position Risk: {MAX_POSITION_RISK*100}%")
        logging.info("=================================")

    def analyze_market(self, symbol, timeframe):
        """Analyze market for a specific symbol and timeframe"""
        logging.info(f"Analyzing {symbol} on {timeframe}...")

        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
            if not ohlcv or len(ohlcv) < 50:
                logging.error(f"Insufficient data fetched for {symbol}")
                return None

            latest_candle = ohlcv[-1]
            latest_price = latest_candle[4]

            # Prepare data
            df = pd.DataFrame(
                ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            # Simple signal generation (replace with your actual logic)
            signal = self.generate_simple_signal(df, symbol)

            # Calculate trade parameters
            entry_price = latest_price
            if signal["signal"] == "BUY":
                sl = entry_price * (1 - STOP_LOSS_PERCENT)
                tp = entry_price * (1 + TAKE_PROFIT_PERCENT)
            elif signal["signal"] == "SELL":
                sl = entry_price * (1 + STOP_LOSS_PERCENT)
                tp = entry_price * (1 - TAKE_PROFIT_PERCENT)
            else:
                sl = tp = 0

            # Calculate position size - FIXED: Only 3 arguments now
            position_size = self.risk_manager.calculate_position_size(
                entry_price, sl  # Removed MAX_POSITION_RISK parameter
            )
            market_size = (
                entry_price * position_size * LEVERAGE
                if signal["signal"] in ["BUY", "SELL"]
                else 0
            )

            # Calculate price change for moving info
            price_change = 0
            if len(df) > 1:
                price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2] * 100

            # Prepare moving info
            moving_info = f"Change%={price_change:.2f}%"

            # Cache entry - fixed format for monitor.html
            cache_entry = (
                f"{datetime.now()}|{symbol}|{signal['signal']}|"
                f"Open={entry_price:.2f}|Range={entry_price-10:.2f}-{entry_price+10:.2f}|"
                f"SL={sl:.2f}|TP={tp:.2f}|Leverage={LEVERAGE}x|"
                f"Conf={signal['confidence']*100:.0f}%|"
                f"MarketSize={market_size:.2f}|Moving={moving_info}|"
                f"Reasons={signal['reason']}\n"
            )

            try:
                with open(CACHE_FILE, "a", encoding='utf-8') as f:
                    f.write(cache_entry)
                logging.debug(f"Cached: {symbol} - {signal['signal']}")
            except Exception as e:
                logging.error(f"Failed to write cache for {symbol}: {e}")

            logging.info(
                f"{symbol}: Signal={signal['signal']}, Confidence={signal['confidence']*100:.0f}%"
            )

            return {
                "symbol": symbol,
                "signal": signal,
                "entry_price": entry_price,
                "stop_loss": sl,
                "take_profit": tp,
                "position_size": position_size,
                "market_size": market_size,
                "df": df
            }

        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    def generate_simple_signal(self, df, symbol):
        """Simple signal generation (replace with your actual strategy)"""
        # This is a placeholder - replace with your actual signal logic
        current_price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-2] if len(df) > 1 else current_price

        price_change = (current_price - prev_price) / prev_price

        # Simple strategy based on price movement
        if price_change > 0.005:  # 0.5% increase
            return {"signal": "BUY", "confidence": 0.75, "reason": "Bullish momentum"}
        elif price_change < -0.005:  # 0.5% decrease
            return {"signal": "SELL", "confidence": 0.75, "reason": "Bearish momentum"}
        elif price_change > 0.002:  # 0.2% increase
            return {"signal": "BUY", "confidence": 0.65, "reason": "Slight bullish"}  # Increased to 0.65
        elif price_change < -0.002:  # 0.2% decrease
            return {"signal": "SELL", "confidence": 0.65, "reason": "Slight bearish"}  # Increased to 0.65
        else:
            return {
                "signal": "HOLD",
                "confidence": 0.3,
                "reason": "No significant movement",
            }

    def execute_trade(self, analysis_result):
        """Execute trade based on analysis result"""
        if not analysis_result:
            return None

        symbol = analysis_result["symbol"]
        signal = analysis_result["signal"]

        # Check if we should execute the trade
        if (
            signal["signal"] in ["BUY", "SELL"]
            and signal["confidence"] >= CONFIDENCE_THRESHOLD
            and self.portfolio.get_open_positions_count() < MAX_OPEN_TRADES
        ):

            # Execute trade through trader
            trade = self.trader.execute_trade(signal, symbol, analysis_result["df"], analysis_result)
            
            if trade:
                self.portfolio.add_position(trade)
                # FIXED: No emojis in logging
                logging.info(
                    f"TRADE EXECUTED: {symbol} {signal['signal']} @ ${analysis_result['entry_price']:.2f}"
                )
                logging.info(f"Position Size: {analysis_result['position_size']:.6f}")
                logging.info(f"Market Size: ${analysis_result['market_size']:.2f}")
                logging.info(f"Stop Loss: ${analysis_result['stop_loss']:.2f}")
                logging.info(f"Take Profit: ${analysis_result['take_profit']:.2f}")
                logging.info(f"Reason: {signal['reason']}")
                return trade
        else:
            if signal["signal"] in ["BUY", "SELL"]:
                # FIXED: No emojis in logging
                logging.info(f"SKIP TRADE: {symbol} - Confidence: {signal['confidence']:.2f} < {CONFIDENCE_THRESHOLD} or max trades reached")
            return None

    def update_portfolio_values(self):
        """Update portfolio with current prices"""
        current_prices = {}
        for symbol in TRADING_PAIRS:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, "1m", limit=1)
                if ohlcv and len(ohlcv) > 0:
                    current_prices[symbol] = ohlcv[0][4]
                    logging.debug(f"Current price for {symbol}: ${current_prices[symbol]:.2f}")
            except Exception as e:
                logging.error(f"Error fetching price for {symbol}: {e}")

        if current_prices:
            portfolio_value = self.portfolio.update_portfolio(current_prices)
            total_profit = portfolio_value - self.initial_capital
            open_positions = self.portfolio.get_open_positions_count()

            logging.info(
                f"PORTFOLIO UPDATE: ${portfolio_value:.2f} | Profit: ${total_profit:.2f} | Positions: {open_positions}/{MAX_OPEN_TRADES}"
            )
            
            # Log profit for monitor.html to read
            logging.info(f"Total Profit: ${total_profit:.2f}")
            
            return portfolio_value
        return None

    def run(self):
        """Main trading loop"""
        self.running = True
        # FIXED: No emojis in logging
        logging.info("Trading Bot Started!")
        logging.info(f"Monitoring {len(TRADING_PAIRS)} trading pairs")
        logging.info(f"Analysis interval: {ANALYSIS_INTERVAL} seconds")

        analysis_count = 0
        last_portfolio_update = 0

        try:
            while self.running:
                analysis_count += 1
                logging.info(f"--- Analysis Cycle #{analysis_count} ---")

                # Analyze all trading pairs
                for symbol in TRADING_PAIRS:
                    try:
                        analysis_result = self.analyze_market(symbol, PRIMARY_TIMEFRAME)
                        if analysis_result and SANDBOX_MODE:
                            self.execute_trade(analysis_result)
                    except Exception as e:
                        logging.error(f"Error processing {symbol}: {e}")
                        continue

                # Update portfolio values every 3 cycles or every 3 minutes
                if analysis_count % 3 == 0 or (time.time() - last_portfolio_update) > 180:
                    self.update_portfolio_values()
                    last_portfolio_update = time.time()

                # Wait for next analysis cycle
                logging.info(f"Waiting {ANALYSIS_INTERVAL} seconds for next analysis...")
                
                # Break the sleep into smaller chunks to allow for KeyboardInterrupt
                for i in range(ANALYSIS_INTERVAL):
                    if not self.running:
                        break
                    time.sleep(1)

        except KeyboardInterrupt:
            # FIXED: No emojis in logging
            logging.info("Bot stopped by user")
            self.running = False
        except Exception as e:
            # FIXED: No emojis in logging
            logging.error(f"Error in main loop: {e}")
            import traceback
            logging.error(traceback.format_exc())
            self.running = False
        finally:
            logging.info("Final Portfolio Summary:")
            self.update_portfolio_values()
            logging.info("Trading Bot Shutdown Complete")


if __name__ == "__main__":
    try:
        # Test imports first
        import pandas as pd
        import ccxt
        from dotenv import load_dotenv
        
        logging.info("All imports successful")
        
        # Create bot and run
        bot = TradingBot(initial_capital=10000)
        bot.run()
        
    except ImportError as e:
        logging.error(f"Import error: {e}")
        print(f"Please install missing dependencies: {e}")
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        import traceback
        logging.error(traceback.format_exc())