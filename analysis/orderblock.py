import pandas as pd
import numpy as np

class OrderBlockDetector:
    def __init__(self, df, lookback=50):
        self.df = df
        self.lookback = lookback
    
    def detect_bullish_order_blocks(self):
        order_blocks = []
        
        for i in range(self.lookback, len(self.df) - 1):
            # Strong bearish candle
            is_bearish = self.df['close'].iloc[i] < self.df['open'].iloc[i]
            bearish_body = abs(self.df['open'].iloc[i] - self.df['close'].iloc[i])
            avg_body = abs(self.df['close'] - self.df['open']).iloc[i-20:i].mean()
            
            if is_bearish and bearish_body > avg_body * 1.5:
                # Check for bullish reversal
                next_move = self.df['close'].iloc[i+1] - self.df['close'].iloc[i]
                if next_move > 0:
                    # Volume confirmation
                    avg_volume = self.df['volume'].iloc[i-20:i].mean()
                    if self.df['volume'].iloc[i] > avg_volume * 1.2:
                        order_blocks.append({
                            'index': i,
                            'timestamp': self.df.index[i],
                            'type': 'bullish',
                            'top': self.df['open'].iloc[i],
                            'bottom': self.df['close'].iloc[i],
                            'strength': bearish_body / self.df['close'].iloc[i],
                            'volume': self.df['volume'].iloc[i]
                        })
        
        return order_blocks
    
    def detect_bearish_order_blocks(self):
        order_blocks = []
        
        for i in range(self.lookback, len(self.df) - 1):
            # Strong bullish candle
            is_bullish = self.df['close'].iloc[i] > self.df['open'].iloc[i]
            bullish_body = abs(self.df['close'].iloc[i] - self.df['open'].iloc[i])
            avg_body = abs(self.df['close'] - self.df['open']).iloc[i-20:i].mean()
            
            if is_bullish and bullish_body > avg_body * 1.5:
                # Check for bearish reversal
                next_move = self.df['close'].iloc[i+1] - self.df['close'].iloc[i]
                if next_move < 0:
                    # Volume confirmation
                    avg_volume = self.df['volume'].iloc[i-20:i].mean()
                    if self.df['volume'].iloc[i] > avg_volume * 1.2:
                        order_blocks.append({
                            'index': i,
                            'timestamp': self.df.index[i],
                            'type': 'bearish',
                            'top': self.df['close'].iloc[i],
                            'bottom': self.df['open'].iloc[i],
                            'strength': bullish_body / self.df['close'].iloc[i],
                            'volume': self.df['volume'].iloc[i]
                        })
        
        return order_blocks
    
    def get_active_order_blocks(self, bullish_obs, bearish_obs):
        current_price = self.df['close'].iloc[-1]
        active = []
        
        for ob in bullish_obs[-5:]:  # Last 5
            if ob['bottom'] < current_price < ob['bottom'] * 1.05:
                active.append(ob)
        
        for ob in bearish_obs[-5:]:
            if ob['top'] * 0.95 < current_price < ob['top']:
                active.append(ob)
        
        return active