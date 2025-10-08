import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def __init__(self, df):
        self.df = df.copy()
    
    def calculate_ema(self, period):
        '''Exponential Moving Average'''
        return self.df['close'].ewm(span=period, adjust=False).mean()
    
    def calculate_rsi(self, period=14):
        '''Relative Strength Index'''
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def calculate_macd(self):
        '''MACD Indicator'''
        exp1 = self.df['close'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal
    
    def calculate_bollinger_bands(self, period=20, std=2):
        '''Bollinger Bands'''
        sma = self.df['close'].rolling(window=period).mean()
        std_dev = self.df['close'].rolling(window=period).std()
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        return upper, sma, lower
    
    def calculate_atr(self, period=14):
        '''Average True Range'''
        high = self.df['high']
        low = self.df['low']
        close = self.df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr