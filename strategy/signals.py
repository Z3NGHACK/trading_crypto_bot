import pandas as pd
import logging
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

class SignalGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_signal(self, df):
        try:
            symbol = df['symbol'].iloc[0] if 'symbol' in df.columns else 'unknown'
            self.logger.debug(f"Generating signal for {symbol} with {len(df)} candles")
            self.logger.debug(f"DataFrame columns: {list(df.columns)}")
            self.logger.debug(f"Last row: {df.tail(1).to_dict()}")
            if df.empty or len(df) < 14:
                self.logger.warning(f"Insufficient data for {symbol}: {len(df)} candles")
                return {'symbol': symbol, 'direction': 'HOLD', 'confidence': 0.0}

            # Simple RSI-based strategy
            df['rsi'] = self.calculate_rsi(df['close'], 14)
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            signal = 'HOLD'
            confidence = 0.5
            entry_price = latest['close']
            stop_loss = entry_price * (1 - 0.02)  # 2% stop loss
            take_profit = entry_price * (1 + 0.04)  # 4% take profit
            market_size = entry_price * 100  # Example position size
            moving = '0.00%'
            reasons = []
            range_val = f"{latest['low']:.2f}-{latest['high']:.2f}"
            timestamp = int(latest['timestamp'].timestamp() * 1000) if 'timestamp' in df.columns and pd.notnull(latest['timestamp']) else int(pd.Timestamp.now().timestamp() * 1000)

            if latest['rsi'] < RSI_OVERSOLD and prev['rsi'] >= RSI_OVERSOLD:
                signal = 'BUY'
                confidence = 0.85
                reasons.append('RSI Oversold Crossover')
            elif latest['rsi'] > RSI_OVERBOUGHT and prev['rsi'] <= RSI_OVERBOUGHT:
                signal = 'SELL'
                confidence = 0.85
                reasons.append('RSI Overbought Crossover')

            price_change = ((latest['close'] - prev['close']) / prev['close'] * 100)
            moving = f"{price_change:+.2f}%"
            accuracy = confidence * 100  # Simplified for display

            signal_data = {
                'symbol': symbol,
                'direction': signal,
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'confidence': confidence,
                'range': range_val,
                'leverage': 1,
                'market_size': market_size,
                'moving': moving,
                'reasons': ', '.join(reasons) if reasons else 'No clear signal',
                'accuracy': accuracy,
                'timestamp': timestamp
            }
            self.logger.info(f"Generated signal for {symbol}: {signal_data['direction']} (Confidence: {confidence})")
            return signal_data
        except Exception as e:
            self.logger.error(f"Error generating signal for {symbol}: {e}")
            return {'symbol': symbol, 'direction': 'HOLD', 'confidence': 0.0}

    def calculate_rsi(self, prices, period=14):
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return pd.Series([0] * len(prices))