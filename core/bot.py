import logging
import json
import time
from config.settings import INITIAL_CAPITAL, TRADING_PAIRS, PRIMARY_TIMEFRAME
from data.exchange import ExchangeConnector
from data.fetcher import DataFetcher
from execution.portfolio import Portfolio
from execution.trader import Trader
from strategy.signals import SignalGenerator
from strategy.risk_management import RiskManager

class TradingBot:
    def __init__(self):
        self.running = False
        self.exchange = ExchangeConnector()
        self.data_fetcher = DataFetcher()
        self.portfolio = Portfolio(INITIAL_CAPITAL)
        self.trader = Trader(self.exchange, self.portfolio)
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager(INITIAL_CAPITAL)
        self.logger = logging.getLogger(__name__)

    def analyze_and_execute(self, symbol):
        try:
            self.logger.debug(f"Analyzing {symbol}...")
            df = self.data_fetcher.fetch_and_store(symbol, PRIMARY_TIMEFRAME)
            if df is None or df.empty:
                self.logger.warning(f"No data for {symbol}")
                return
            self.logger.debug(f"DataFrame for {symbol}: {list(df.columns)}, Rows: {len(df)}")
            self.logger.debug(f"Last row: {df.tail(1).to_dict()}")
            df['symbol'] = symbol
            signal = self.signal_generator.generate_signal(df)
            self.logger.debug(f"Signal for {symbol}: {signal}")
            if signal['confidence'] >= self.risk_manager.confidence_threshold and self.risk_manager.validate_trade(signal):
                self.trader.execute_trade(signal)
                self.logger.info(f"Executed trade for {symbol}: {signal['direction']} (Confidence: {signal['confidence']})")
            else:
                self.logger.debug(f"Skipped trade for {symbol}: Low confidence {signal['confidence']} or invalid trade")
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")

    def update_portfolio_values(self):
        try:
            current_prices = {}
            for symbol in TRADING_PAIRS:
                price = self.exchange.get_current_price(symbol)
                if price:
                    current_prices[symbol] = price
                else:
                    self.logger.warning(f"No price data for {symbol}")
                open_orders = self.exchange.get_open_orders(symbol)
                self.trader.sync_open_orders(symbol, open_orders)
            if current_prices:
                portfolio_value = self.portfolio.update_portfolio(current_prices)
                total_profit = portfolio_value - INITIAL_CAPITAL
                open_positions = self.portfolio.get_open_positions_count()
                self.logger.info(f"Portfolio value: ${portfolio_value:.2f}, Total Profit: ${total_profit:.2f}, Positions: {open_positions}")
            else:
                self.logger.warning("No valid price data for portfolio update")
        except Exception as e:
            self.logger.error(f"Error updating portfolio: {e}")

    def save_portfolio_state(self):
        try:
            with open('data/portfolio_state.json', 'w') as f:
                json.dump({
                    'positions': self.portfolio.positions,
                    'closed_positions': self.portfolio.closed_positions,
                    'initial_capital': INITIAL_CAPITAL
                }, f)
            self.logger.info("Portfolio state saved.")
        except Exception as e:
            self.logger.error(f"Error saving portfolio state: {e}")

    def get_performance_metrics(self):
        try:
            closed_positions = self.portfolio.closed_positions
            total_trades = len(closed_positions)
            wins = sum(1 for pos in closed_positions if pos.get('profit', 0) > 0)
            losses = total_trades - wins
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
            avg_confidence = sum(pos.get('confidence', 0) for pos in closed_positions if pos.get('confidence', 0) >= 0.8) / total_trades if total_trades > 0 else 0.0
            return {
                'total_trades': total_trades,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'avg_confidence': avg_confidence
            }
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return {'total_trades': 0, 'wins': 0, 'losses': 0, 'win_rate': 0.0, 'avg_confidence': 0.0}