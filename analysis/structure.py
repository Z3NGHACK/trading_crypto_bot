import pandas as pd
import logging

class MarketStructure:
    def __init__(self, df):
        self.df = df
        self.logger = logging.getLogger(__name__)

    def find_swing_points(self):
        highs = []
        lows = []
        try:
            for i in range(1, len(self.df) - 1):
                if self.df['high'].iloc[i] > self.df['high'].iloc[i - 1] and self.df['high'].iloc[i] > self.df['high'].iloc[i + 1]:
                    highs.append(self.df['high'].iloc[i])
                if self.df['low'].iloc[i] < self.df['low'].iloc[i - 1] and self.df['low'].iloc[i] < self.df['low'].iloc[i + 1]:
                    lows.append(self.df['low'].iloc[i])
            self.logger.debug(f"Found {len(highs)} swing highs and {len(lows)} swing lows")
        except Exception as e:
            self.logger.error(f"Error finding swing points: {e}")
        return highs, lows

    def detect_trend(self, highs, lows):
        try:
            if len(highs) >= 2 and len(lows) >= 2:
                if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
                    return 'bullish'
                elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                    return 'bearish'
            return 'neutral'
        except Exception as e:
            self.logger.error(f"Error detecting trend: {e}")
            return 'neutral'