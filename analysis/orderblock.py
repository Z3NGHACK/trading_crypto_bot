import pandas as pd
import numpy as np

class OrderBlockDetector:
    def __init__(self, df, lookback=50, body_multiplier=1.5, volume_multiplier=1.2, avg_period=20, sustain_candles=2):
        self.df = df
        self.lookback = lookback
        self.body_multiplier = body_multiplier
        self.volume_multiplier = volume_multiplier
        self.avg_period = avg_period
        self.sustain_candles = sustain_candles
    
    def detect_bullish_order_blocks(self):
        order_blocks = []
        
        for i in range(self.lookback, len(self.df) - self.sustain_candles):
            # Strong bearish candle
            is_bearish = self.df['close'].iloc[i] < self.df['open'].iloc[i]
            bearish_body = abs(self.df['open'].iloc[i] - self.df['close'].iloc[i])
            avg_body = abs(self.df['close'] - self.df['open']).iloc[i-self.avg_period:i].mean()
            
            if is_bearish and bearish_body > avg_body * self.body_multiplier:
                # Check for sustained bullish reversal
                reversal_sustained = all(self.df['close'].iloc[i+j+1] > self.df['close'].iloc[i+j] for j in range(self.sustain_candles))
                if reversal_sustained:
                    # Volume confirmation
                    avg_volume = self.df['volume'].iloc[i-self.avg_period:i].mean()
                    if self.df['volume'].iloc[i] > avg_volume * self.volume_multiplier:
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
        
        for i in range(self.lookback, len(self.df) - self.sustain_candles):
            # Strong bullish candle
            is_bullish = self.df['close'].iloc[i] > self.df['open'].iloc[i]
            bullish_body = abs(self.df['close'].iloc[i] - self.df['open'].iloc[i])
            avg_body = abs(self.df['close'] - self.df['open']).iloc[i-self.avg_period:i].mean()
            
            if is_bullish and bullish_body > avg_body * self.body_multiplier:
                # Check for sustained bearish reversal
                reversal_sustained = all(self.df['close'].iloc[i+j+1] < self.df['close'].iloc[i+j] for j in range(self.sustain_candles))
                if reversal_sustained:
                    # Volume confirmation
                    avg_volume = self.df['volume'].iloc[i-self.avg_period:i].mean()
                    if self.df['volume'].iloc[i] > avg_volume * self.volume_multiplier:
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
    
    def score_order_block(self, ob, swing_highs, swing_lows):
        # Score based on proximity to swings (higher score = better prediction chance)
        score = ob['strength'] * (ob['volume'] / self.df['volume'].mean())
        # Check distance to nearest swing
        nearest_swing_dist = min(abs(ob['index'] - sh[0]) for sh in swing_highs + swing_lows)
        if nearest_swing_dist < 10:
            score *= 1.2  # Boost if close to swing
        return score