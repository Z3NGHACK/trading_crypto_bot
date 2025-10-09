import pandas as pd

class VolumeAnalyzer:
    def __init__(self, df, lookback=20, spike_threshold=1.5):
        self.df = df
        self.lookback = lookback
        self.spike_threshold = spike_threshold
    
    def detect_volume_spike(self):
        '''Detect volume spikes above average'''
        avg_volume = self.df['volume'].rolling(window=self.lookback).mean()
        current_volume = self.df['volume'].iloc[-1]
        if current_volume > avg_volume.iloc[-1] * self.spike_threshold:
            return True
        return False
    
    def calculate_obv(self):
        # On-Balance Volume for divergence detection
        obv = [0]
        for i in range(1, len(self.df)):
            if self.df['close'].iloc[i] > self.df['close'].iloc[i-1]:
                obv.append(obv[-1] + self.df['volume'].iloc[i])
            elif self.df['close'].iloc[i] < self.df['close'].iloc[i-1]:
                obv.append(obv[-1] - self.df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=self.df.index)
    
    def detect_obv_divergence(self):
        # Bullish/bearish divergence for prediction
        obv = self.calculate_obv()
        price_trend = self.df['close'].pct_change().rolling(5).sum().iloc[-1]
        obv_trend = obv.pct_change().rolling(5).sum().iloc[-1]
        if price_trend < 0 and obv_trend > 0:
            return 'bullish_divergence'  # Higher chance of reversal up
        elif price_trend > 0 and obv_trend < 0:
            return 'bearish_divergence'
        return None
    
    def calculate_volume_profile(self, bins=20):
        # Volume at price levels (high volume = strong support/resistance)
        price_bins = pd.cut(self.df['close'], bins=bins)
        vp = self.df.groupby(price_bins)['volume'].sum()
        poc = vp.idxmax()  # Point of Control (highest volume price)
        return vp, poc