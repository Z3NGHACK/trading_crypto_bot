class RiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
    
    def calculate_position_size(self, entry_price, stop_loss, risk_percent=0.02):
        """
        Calculate position size based on risk management
        
        Args:
            entry_price: Entry price of the trade
            stop_loss: Stop loss price
            risk_percent: Risk percentage (default 2%)
        
        Returns:
            Position size in units
        """
        try:
            risk_amount = self.initial_capital * risk_percent
            price_risk = abs(entry_price - stop_loss)
            
            if price_risk > 0:
                position_size = risk_amount / price_risk
                return position_size
            else:
                return 0
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return 0