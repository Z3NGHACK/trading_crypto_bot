import pandas as pd
import numpy as np

class MarketStructure:
    def __init__(self, df):
        self.df = df
    
    def find_swing_points(self, window=5):
        '''Identify swing highs and lows'''
        highs = []
        lows = []
        
        for i in range(window, len(self.df) - window):
            # Swing High
            if all(self.df['high'].iloc[i] > self.df['high'].iloc[i-window:i]) and \
               all(self.df['high'].iloc[i] > self.df['high'].iloc[i+1:i+window+1]):
                highs.append((i, self.df['high'].iloc[i]))
            
            # Swing Low
            if all(self.df['low'].iloc[i] < self.df['low'].iloc[i-window:i]) and \
               all(self.df['low'].iloc[i] < self.df['low'].iloc[i+1:i+window+1]):
                lows.append((i, self.df['low'].iloc[i]))
        
        return highs, lows
    
    def detect_trend(self, highs, lows):
        '''Detect market trend: bullish, bearish, or ranging'''
        if len(highs) < 2 or len(lows) < 2:
            return 'ranging'
        
        recent_highs = [h[1] for h in highs[-3:]]
        recent_lows = [l[1] for l in lows[-3:]]
        
        higher_highs = all(recent_highs[i] < recent_highs[i+1] 
                          for i in range(len(recent_highs)-1))
        higher_lows = all(recent_lows[i] < recent_lows[i+1] 
                         for i in range(len(recent_lows)-1))
        
        lower_highs = all(recent_highs[i] > recent_highs[i+1] 
                         for i in range(len(recent_highs)-1))
        lower_lows = all(recent_lows[i] > recent_lows[i+1] 
                        for i in range(len(recent_lows)-1))
        
        if higher_highs and higher_lows:
            return 'bullish'
        elif lower_highs and lower_lows:
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