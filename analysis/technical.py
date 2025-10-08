import pandas as pd
import logging
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

class TechnicalAnalyzer:
    def __init__(self, df):
        self.df = df
        self.logger = logging.getLogger(__name__)

    def calculate_rsi(self):
        try:
            delta = self.df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            self.logger.debug(f"Calculated RSI: {rsi.iloc[-1]}")
            return rsi
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return pd.Series(50.0, index=self.df.index)

    def calculate_atr(self):
        try:
            high_low = self.df['high'] - self.df['low']
            high_close = (self.df['high'] - self.df['close'].shift()).abs()
            low_close = (self.df['low'] - self.df['close'].shift()).abs()
            tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = tr.rolling(window=14).mean()
            self.logger.debug(f"Calculated ATR: {atr.iloc[-1]}")
            return atr
        except Exception as e:
            self.logger.error(f"Error calculating ATR: {e}")
            return pd.Series(0.0, index=self.df.index)