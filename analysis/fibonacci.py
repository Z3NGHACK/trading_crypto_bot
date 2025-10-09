import pandas as pd

class FibonacciAnalyzer:
    def __init__(self, df):
        self.df = df
        self.levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    def calculate_retracement(self, swing_high, swing_low):
        diff = swing_high - swing_low
        retracements = {level: swing_high - (diff * level) for level in self.levels}
        return retracements
    
    def get_current_levels(self, highs, lows):
        if highs and lows:
            recent_high = highs[-1][1]
            recent_low = lows[-1][1]
            return self.calculate_retracement(recent_high, recent_low)
        return {}
    
    def predict_reversal(self, current_price, levels):
        for level, price in levels.items():
            if abs(current_price - price) / current_price < 0.005:  # Within 0.5%
                return f'reversal_at_{level}', 0.7  # High chance at golden ratio (0.618)
        return None