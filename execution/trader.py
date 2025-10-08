import logging
import time
from config.settings import INITIAL_CAPITAL, MAX_POSITION_SIZE, LEVERAGE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT

class Trader:
    def __init__(self, exchange, fetcher):
        self.logger = logging.getLogger(__name__)
        self.exchange = exchange
        self.fetcher = fetcher
        self.initial_capital = INITIAL_CAPITAL
        self.max_position_size = MAX_POSITION_SIZE
        self.leverage = LEVERAGE
        self.stop_loss_percent = STOP_LOSS_PERCENT
        self.take_profit_percent = TAKE_PROFIT_PERCENT
        self.logger.info("Trader initialized")

    def execute_trade(self, symbol, signal, confidence, price):
        try:
            if confidence < 0.8:
                self.logger.info(f"Skipping trade for {symbol}: Confidence {confidence} below threshold")
                return None

            if signal not in ['BUY', 'SELL']:
                self.logger.info(f"Skipping trade for {symbol}: Invalid signal {signal}")
                return None

            # Calculate position size
            position_size = self.initial_capital * self.max_position_size
            quantity = position_size / price if price else 0

            # Get step size from market info
            step_size = self.exchange.markets[symbol]['info'].get('quantityPrecision', 4)
            step_size = 10 ** -step_size
            quantity = self.exchange.round_step_size(quantity, step_size)

            # Calculate stop loss and take profit
            stop_loss = price * (1 - self.stop_loss_percent) if signal == 'BUY' else price * (1 + self.stop_loss_percent)
            take_profit = price * (1 + self.take_profit_percent) if signal == 'BUY' else price * (1 - self.take_profit_percent)

            # Place order
            order_type = 'MARKET'
            order = self.exchange.place_order(
                symbol=symbol,
                side=signal,
                order_type=order_type,
                quantity=quantity
            )

            # Write to cache even if order fails to ensure dashboard updates
            self._write_to_cache(symbol, signal, price, stop_loss, take_profit, confidence, quantity)

            if order:
                self.logger.info(f"Successfully executed {signal} trade for {symbol}: {quantity} @ {price}")
                return order
            else:
                self.logger.error(f"Failed to execute trade for {symbol}")
                return None

        except Exception as e:
            self.logger.error(f"Error executing trade for {symbol}: {e}")
            self._write_to_cache(symbol, signal, price, stop_loss, take_profit, confidence, quantity)
            return None

    def _write_to_cache(self, symbol, signal, price, stop_loss, take_profit, confidence, quantity):
        try:
            timestamp = int(time.time() * 1000)
            cache_line = (
                f"{timestamp}|{symbol}|{signal}|Open={price:.2f}|"
                f"Range=-|SL={stop_loss:.2f}|TP={take_profit:.2f}|"
                f"Leverage={self.leverage}|Conf={confidence*100:.0f}%|"
                f"MarketSize={quantity*price:.2f}|Moving=0.0%|"
                f"Strategy Execution|Accuracy={confidence*100:.0f}%"
            )
            with open('data/cache.txt', 'a') as f:
                f.write(cache_line + '\n')
            self.logger.debug(f"Wrote to cache: {cache_line}")
        except Exception as e:
            self.logger.error(f"Error writing to cache: {e}")