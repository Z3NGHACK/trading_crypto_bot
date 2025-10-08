from config.settings import *

class RiskManager:
    def __init__(self, capital):
        self.capital = capital
        self.max_risk_per_trade = MAX_POSITION_SIZE
        self.stop_loss_percent = STOP_LOSS_PERCENT
        self.take_profit_percent = TAKE_PROFIT_PERCENT
    
    def calculate_position_size(self, entry_price, stop_loss_price):
        risk_amount = self.capital * self.max_risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size
    
    def calculate_stop_loss(self, entry_price, direction, atr=None):
        if direction == 'long':
            if atr:
                return entry_price - (atr * 2)
            return entry_price * (1 - self.stop_loss_percent)
        else:  # short
            if atr:
                return entry_price + (atr * 2)
            return entry_price * (1 + self.stop_loss_percent)
    
    def calculate_take_profit(self, entry_price, direction):
        if direction == 'long':
            return entry_price * (1 + self.take_profit_percent)
        else:
            return entry_price * (1 - self.take_profit_percent)
    
    def validate_trade(self, entry, stop_loss, take_profit, direction):
        if direction == 'long':
            risk = entry - stop_loss
            reward = take_profit - entry
        else:
            risk = stop_loss - entry
            reward = entry - take_profit
        
        if risk <= 0:
            return False, "Invalid stop loss"
        
        risk_reward = reward / risk
        
        if risk_reward < MIN_RISK_REWARD_RATIO:
            return False, f"Risk/Reward ratio too low: {risk_reward:.2f}"
        
        return True, f"Risk/Reward: {risk_reward:.2f}"