import pandas as pd
import numpy as np
from scipy.stats import linregress

class MarketStructure:
    def __init__(self, df, swing_window=5):
        self.df = df
        self.swing_window = swing_window
    
    def find_swing_points(self):
        '''Identify swing highs and lows'''
        highs = []
        lows = []
        
        for i in range(self.swing_window, len(self.df) - self.swing_window):
            # Swing High
            if all(self.df['high'].iloc[i] > self.df['high'].iloc[i-self.swing_window:i]) and \
               all(self.df['high'].iloc[i] > self.df['high'].iloc[i+1:i+self.swing_window+1]):
                highs.append((i, self.df['high'].iloc[i]))
            
            # Swing Low
            if all(self.df['low'].iloc[i] < self.df['low'].iloc[i-self.swing_window:i]) and \
               all(self.df['low'].iloc[i] < self.df['low'].iloc[i+1:i+self.swing_window+1]):
                lows.append((i, self.df['low'].iloc[i]))
        
        return highs, lows
    
    def detect_trend(self, highs, lows):
        '''Detect market trend with slope for better accuracy'''
        if len(highs) < 2 or len(lows) < 2:
            return 'ranging'
        
        # Calculate slope of recent highs and lows
        high_indices = [h[0] for h in highs[-3:]]
        high_values = [h[1] for h in highs[-3:]]
        low_indices = [l[0] for l in lows[-3:]]
        low_values = [l[1] for l in lows[-3:]]
        
        if len(high_indices) >= 2:
            high_slope = linregress(high_indices, high_values).slope
        else:
            high_slope = 0
        
        if len(low_indices) >= 2:
            low_slope = linregress(low_indices, low_values).slope
        else:
            low_slope = 0
        
        if high_slope > 0 and low_slope > 0:
            return 'bullish'
        elif high_slope < 0 and low_slope < 0:
            return 'bearish'
        else:
            return 'ranging'
    
    def detect_breakout(self, current_price, resistance, support, threshold=0.001):
        '''Detect structure breakout'''
        if current_price > resistance * (1 + threshold):
            return 'bullish_breakout'
        elif current_price < support * (1 - threshold):
            return 'bearish_breakout'
        return None
    
    def get_support_resistance(self, highs, lows):
        # Calculate dynamic S/R from swings
        if highs:
            resistance = max(h[1] for h in highs[-3:])
        else:
            resistance = self.df['high'].max()
        if lows:
            support = min(l[1] for l in lows[-3:])
        else:
            support = self.df['low'].min()
        return support, resistance
    
    def detect_bos_choch(self, highs, lows, current_price):
        # BOS (bullish if breaks prev high), CHOCH (reversal if fails)
        if len(highs) < 2 or len(lows) < 2:
            return None
        prev_high = highs[-2][1]
        prev_low = lows[-2][1]
        if current_price > prev_high:
            return 'bos_bullish'  # Higher probability of uptrend continuation
        elif current_price < prev_low:
            return 'bos_bearish'
        elif current_price < prev_high and self.detect_trend(highs, lows) == 'bullish':
            return 'choch_bearish'  # Reversal signal
        elif current_price > prev_low and self.detect_trend(highs, lows) == 'bearish':
            return 'choch_bullish'
        return None