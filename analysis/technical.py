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
    
    def calculate_stochastic(self, period=14, smooth_k=3, smooth_d=3):
        # Stochastic Oscillator
        low_min = self.df['low'].rolling(window=period).min()
        high_max = self.df['high'].rolling(window=period).max()
        k = 100 * ((self.df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=smooth_k).mean().rolling(window=smooth_d).mean()
        return k, d
    
    def calculate_ichimoku(self):
        # Ichimoku Cloud (simplified)
        high9 = self.df['high'].rolling(9).max()
        low9 = self.df['low'].rolling(9).min()
        tenkan = (high9 + low9) / 2
        
        high26 = self.df['high'].rolling(26).max()
        low26 = self.df['low'].rolling(26).min()
        kijun = (high26 + low26) / 2
        
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        senkou_b = ((self.df['high'].rolling(52).max() + self.df['low'].rolling(52).min()) / 2).shift(26)
        chikou = self.df['close'].shift(-26)
        return tenkan, kijun, senkou_a, senkou_b, chikou
    
    def get_confluence_signal(self):
        # Combine for higher prediction confidence (e.g., buy if 3+ conditions met)
        rsi = self.calculate_rsi()
        macd, signal = self.calculate_macd()
        upper_bb, mid_bb, lower_bb = self.calculate_bollinger_bands()
        k, d = self.calculate_stochastic()
        
        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1] - signal.iloc[-1]
        current_price = self.df['close'].iloc[-1]
        stoch_cross = k.iloc[-1] > d.iloc[-1] and k.iloc[-2] < d.iloc[-2]
        
        buy_conditions = sum([
            current_rsi < 30,  # Oversold
            current_macd > 0,  # Bullish momentum
            current_price < lower_bb.iloc[-1],  # Below lower BB
            stoch_cross and k.iloc[-1] < 20  # Stochastic buy in oversold
        ])
        sell_conditions = sum([
            current_rsi > 70,  # Overbought
            current_macd < 0,  # Bearish momentum
            current_price > upper_bb.iloc[-1],  # Above upper BB
            k.iloc[-1] < d.iloc[-1] and k.iloc[-2] > d.iloc[-2] and k.iloc[-1] > 80  # Stochastic sell in overbought
        ])
        
        if buy_conditions >= 3:
            return 'buy', buy_conditions / 4  # Probability-like score
        elif sell_conditions >= 3:
            return 'sell', sell_conditions / 4
        return 'neutral', 0