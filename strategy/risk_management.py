import logging
from config.settings import (
    MAX_POSITION_SIZE, STOP_LOSS_PERCENT, TAKE_PROFIT_PERCENT,
    MAX_OPEN_TRADES, MIN_RISK_REWARD_RATIO, CONFIDENCE_THRESHOLD,
    MAX_RISK_PER_TRADE
)

class RiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.max_position_size = MAX_POSITION_SIZE
        self.stop_loss_percent = STOP_LOSS_PERCENT
        self.take_profit_percent = TAKE_PROFIT_PERCENT
        self.max_open_trades = MAX_OPEN_TRADES
        self.min_risk_reward_ratio = MIN_RISK_REWARD_RATIO
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.max_risk_per_trade = MAX_RISK_PER_TRADE
        self.logger = logging.getLogger(__name__)

    def calculate_position_size(self, entry_price, stop_loss):
        try:
            risk_per_trade = self.initial_capital * self.max_risk_per_trade
            risk_per_unit = abs(entry_price - stop_loss)
            position_size = risk_per_trade / risk_per_unit if risk_per_unit != 0 else 0.01
            self.logger.debug(f"Calculated position size: {position_size} for entry {entry_price}, stop {stop_loss}")
            return min(position_size, self.initial_capital * self.max_position_size)
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return 0.01

    def validate_trade(self, signal):
        try:
            risk_reward = abs((signal['take_profit'] - signal['entry_price']) / (signal['entry_price'] - signal['stop_loss']))
            valid = risk_reward >= self.min_risk_reward_ratio and signal['confidence'] >= self.confidence_threshold
            self.logger.debug(f"Trade validation for {signal['symbol']}: R:R={risk_reward}, Valid={valid}")
            return valid
        except Exception as e:
            self.logger.error(f"Error validating trade: {e}")
            return False