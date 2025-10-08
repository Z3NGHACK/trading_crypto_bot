import pandas as pd

class VolumeAnalyzer:
    def __init__(self, df, lookback=20):
        self.df = df
        self.lookback = lookback
    
    def detect_volume_spike(self, threshold=1.5):
        '''Detect volume spikes above average'''
        avg_volume = self.df['volume'].rolling(window=self.lookback).mean()
        current_volume = self.df['volume'].iloc[-1]
        if current_volume > avg_volume.iloc[-1] * threshold:
            return True
        return False