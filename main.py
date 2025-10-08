import pandas as pd
from data.exchange import ExchangeConnector
from data.fetcher import DataFetcher
from data.preprocessor import DataPreprocessor
from analysis.technical import TechnicalAnalyzer
from analysis.structure import MarketStructure
from analysis.orderblock import OrderBlockDetector
from analysis.volume import VolumeAnalyzer
from strategy.signals import SignalGenerator
from strategy.risk_management import RiskManager
from execution.trader import Trader
from execution.portfolio import Portfolio
from visualization.charts import ChartVisualizer
import time
import os
import logging
from config.settings import TRADING_PAIRS, PRIMARY_TIMEFRAME, SANDBOX_MODE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT, LEVERAGE
from datetime import datetime

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/market_analysis.log', mode='a')
    ]
)
terminal_handler = logging.StreamHandler()
terminal_handler.setLevel(logging.INFO)
terminal_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
logging.getLogger().addHandler(terminal_handler)

# Cache file
CACHE_FILE = 'data/cache.txt'
os.makedirs('data', exist_ok=True)

# Clear cache file on startup
try:
    with open(CACHE_FILE, 'w') as f:
        f.write('')
    logging.info(f"Cleared cache file: {CACHE_FILE}")
except Exception as e:
    logging.error(f"Failed to clear cache file: {e}")

class TradingBot:
    def __init__(self, initial_capital=10000):
        self.exchange = ExchangeConnector()
        self.fetcher = DataFetcher()
        self.risk_manager = RiskManager(initial_capital)
        self.portfolio = Portfolio(initial_capital)
        self.trader = Trader(self.exchange, self.risk_manager)
        self.signal_generator = SignalGenerator()
        self.running = False
        self.initial_capital = initial_capital
    
    def prepare_data(self, ohlcv):
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        preprocessor = DataPreprocessor(df)
        return preprocessor.clean_data()
    
    def analyze_market(self, symbol, timeframe):
        logging.info(f"Analyzing {symbol} on {timeframe}...")
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
            if not ohlcv:
                logging.error(f"No data fetched for {symbol}")
                return None
        
            latest_candle = ohlcv[-1]
            latest_time = pd.to_datetime(latest_candle[0], unit='ms')
            latest_price = latest_candle[4]
            logging.debug(f"Latest candle for {symbol}: Time={latest_time}, Close={latest_price}")
            
            logging.debug(f"Raw OHLCV for {symbol}: {ohlcv[-5:]}")
            
            df = self.prepare_data(ohlcv)
            
            logging.debug(f"Preprocessed DF head for {symbol}: \n{df.head()}")
            
            tech = TechnicalAnalyzer(df)
            df['ema_20'] = tech.calculate_ema(20)
            df['ema_50'] = tech.calculate_ema(50)
            df['rsi'] = tech.calculate_rsi()
            df['atr'] = tech.calculate_atr()
            
            logging.debug(f"EMA_20 (last): {df['ema_20'].iloc[-1]}, EMA_50 (last): {df['ema_50'].iloc[-1]}")
            logging.debug(f"RSI (last): {df['rsi'].iloc[-1]}, ATR (last): {df['atr'].iloc[-1]}")
            
            structure = MarketStructure(df)
            highs, lows = structure.find_swing_points()
            trend = structure.detect_trend(highs, lows)
            
            logging.debug(f"Swing highs: {highs[-3:]}, Swing lows: {lows[-3:]}")
            logging.debug(f"Detected trend: {trend}")
            
            ob_detector = OrderBlockDetector(df)
            bullish_obs = ob_detector.detect_bullish_order_blocks()
            bearish_obs = ob_detector.detect_bearish_order_blocks()
            
            logging.debug(f"Bullish order blocks: {bullish_obs[-3:]}")
            logging.debug(f"Bearish order blocks: {bearish_obs[-3:]}")
            
            volume = VolumeAnalyzer(df)
            volume_spike = volume.detect_volume_spike()
            
            logging.debug(f"Volume spike detected: {volume_spike}")
            
            analysis = {
                'trend': trend,
                'bullish_order_blocks': bullish_obs,
                'bearish_order_blocks': bearish_obs,
                'volume_spike': volume_spike,
                'highs': highs,
                'lows': lows
            }
            signal = self.signal_generator.generate_signal(df, analysis, tech)
            
            logging.debug(f"Signal generated: {signal['signal']}, Score: {signal['score']}, Confidence: {signal['confidence']:.2f}")
            logging.debug(f"Reasons learned from data: {', '.join(signal['reasons'])}")
            
            # Cache entry with trade details
            entry_price = latest_price
            atr = df['atr'].iloc[-1] if 'atr' in df else 0
            range_open = f"{entry_price - atr:.2f}-{entry_price + atr:.2f}"
            sl = entry_price * (1 - STOP_LOSS_PERCENT) if signal['signal'] == 'BUY' else entry_price * (1 + STOP_LOSS_PERCENT)
            tp = entry_price * (1 + TAKE_PROFIT_PERCENT) if signal['signal'] == 'BUY' else entry_price * (1 - TAKE_PROFIT_PERCENT)
            position_size = self.risk_manager.calculate_position_size(entry_price, 0.02)
            market_size = entry_price * position_size if signal['signal'] in ['BUY', 'SELL'] else 0
            moving = f"EMA20={df['ema_20'].iloc[-1]:.2f}, EMA50={df['ema_50'].iloc[-1]:.2f}, Change%={(df['close'].iloc[-1] - df['close'].iloc[-2])/df['close'].iloc[-2]*100:.2f}%"
            cache_entry = f"{datetime.now()}|{symbol}|{signal['signal']}|Open={entry_price:.2f}|Range={range_open}|SL={sl:.2f}|TP={tp:.2f}|Leverage={LEVERAGE}x|Conf={signal['confidence']*100:.0f}%|MarketSize={market_size:.2f}|Moving={moving}|Reasons={', '.join(signal['reasons'])}\n"
            try:
                with open(CACHE_FILE, 'a') as f:
                    f.write(cache_entry)
                    f.flush()
                logging.debug(f"Wrote cache entry for {symbol}: {cache_entry.strip()}")
            except Exception as e:
                logging.error(f"Failed to write to cache for {symbol}: {e}")
            
            logging.info(f"{symbol}: Trend={analysis['trend']}, Signal={signal['signal']}, Confidence={signal['confidence']*100:.0f}%")
            
            return {
                'df': df,
                'trend': trend,
                'signal': signal,
                'highs': highs,
                'lows': lows,
                'order_blocks': bullish_obs + bearish_obs,
                'entry_price': entry_price,
                'stop_loss': sl,
                'take_profit': tp,
                'position_size': position_size
            }
        
        except Exception as e:
            logging.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def execute_trade(self, signal, symbol, df):
        trade = self.trader.execute_trade(signal, symbol, df)
        if trade:
            self.portfolio.add_position(trade)
            logging.info(f"\n📊 TRADE SIGNAL\nSymbol: {trade['symbol']}\nDirection: {trade['direction']}\nEntry: ${trade['entry_price']:.2f}\nStop Loss: ${trade['stop_loss']:.2f}\nTake Profit: ${trade['take_profit']:.2f}\nPosition Size: {trade['position_size']:.4f}\nMarket Size: ${trade['entry_price'] * trade['position_size']:.2f}\nReasons: {', '.join(signal['reasons'])}")
            logging.info(f"Added position: {trade['symbol']} {trade['direction'].lower()} @ {trade['entry_price']}")
    
    def run(self):
        self.running = True
        logging.info("Trading Bot Started!")
        
        while self.running:
            try:
                for symbol in TRADING_PAIRS:
                    analysis = self.analyze_market(symbol, PRIMARY_TIMEFRAME)
                    if not analysis:
                        continue
                    
                    if analysis['signal']['signal'] in ['BUY', 'SELL'] and SANDBOX_MODE:
                        logging.info(f"Signal detected: {analysis['signal']['signal']} for {symbol}")
                        self.execute_trade(analysis['signal'], symbol, analysis['df'])
                
                # Update portfolio
                current_prices = {}
                for symbol in TRADING_PAIRS:
                    df = self.fetcher.fetch_and_store(symbol, PRIMARY_TIMEFRAME)
                    if df is not None:
                        current_prices[symbol] = df['close'].iloc[-1]
                    else:
                        logging.error(f"Failed to fetch price for {symbol}")
                portfolio_value = self.portfolio.update_portfolio(current_prices)
                total_profit = portfolio_value - self.initial_capital
                logging.info(f"Portfolio Value: ${portfolio_value:.2f}, Total Profit: ${total_profit:.2f}")
                
                time.sleep(60)
                
            except KeyboardInterrupt:
                logging.info("Bot stopped by user")
                self.running = False
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(30)

if __name__ == '__main__':
    bot = TradingBot()
    bot.run()