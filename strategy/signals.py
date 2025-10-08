from .base import BaseStrategy
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT

class SignalGenerator(BaseStrategy):
    def __init__(self):
        super().__init__("Multi-Factor Strategy")
    
    def generate_signal(self, df, analysis, tech):
        trend = analysis.get('trend', 'ranging')
        rsi = df['rsi'].iloc[-1] if 'rsi' in df else 50
        bullish_obs = analysis.get('bullish_order_blocks', [])
        bearish_obs = analysis.get('bearish_order_blocks', [])
        volume_spike = analysis.get('volume_spike', False)
        breakout = analysis.get('breakout', None)
        highs = analysis.get('highs', [])
        lows = analysis.get('lows', [])
        
        current_price = df['close'].iloc[-1]
        ema_20 = df['ema_20'].iloc[-1] if 'ema_20' in df else current_price
        ema_50 = df['ema_50'].iloc[-1] if 'ema_50' in df else current_price
        
        score = 0
        reasons = []
        
        # BULLISH SIGNALS
        if trend == 'bullish':
            score += 2
            reasons.append("Bullish trend")
        
        if rsi < RSI_OVERSOLD:
            score += 2
            reasons.append(f"RSI oversold ({rsi:.1f})")
        
        if ema_20 > ema_50:
            score += 1
            reasons.append("EMA 20 > EMA 50")
        
        if breakout == 'bullish_breakout':
            score += 3
            reasons.append("Bullish breakout detected")
        
        if volume_spike:
            score += 1
            reasons.append("Volume spike")
        
        # Check if near bullish order block
        for ob in bullish_obs[-3:]:
            if abs(current_price - ob['top']) / current_price < 0.01:
                score += 2
                reasons.append("Near bullish order block")
                break
        
        # BEARISH SIGNALS
        bearish_score = 0
        bearish_reasons = []
        
        if trend == 'bearish':
            bearish_score += 2
            bearish_reasons.append("Bearish trend")
        
        if rsi > RSI_OVERBOUGHT:
            bearish_score += 2
            bearish_reasons.append(f"RSI overbought ({rsi:.1f})")
        
        if ema_20 < ema_50:
            bearish_score += 1
            bearish_reasons.append("EMA 20 < EMA 50")
        
        if breakout == 'bearish_breakout':
            bearish_score += 3
            bearish_reasons.append("Bearish breakout detected")
        
        for ob in bearish_obs[-3:]:
            if abs(current_price - ob['bottom']) / current_price < 0.01:
                bearish_score += 2
                bearish_reasons.append("Near bearish order block")
                break
        
        # MACD for additional confidence
        macd, signal_line = tech.calculate_macd()
        if macd.iloc[-1] > signal_line.iloc[-1]:
            score += 2
            reasons.append("MACD bullish")
        else:
            bearish_score += 2
            bearish_reasons.append("MACD bearish")
        
        # Generate final signal
        if score >= 5 and score > bearish_score:
            return {
                'signal': 'BUY',
                'score': score,
                'confidence': min(score / 10, 1.0),
                'reasons': reasons
            }
        elif bearish_score >= 5 and bearish_score > score:
            return {
                'signal': 'SELL',
                'score': bearish_score,
                'confidence': min(bearish_score / 10, 1.0),
                'reasons': bearish_reasons
            }
        else:
            return {
                'signal': 'HOLD',
                'score': max(score, bearish_score),
                'confidence': 0,
                'reasons': ['Not enough confluence']
            }
    
    def calculate_position_size(self, capital, risk_percent):
        return capital * risk_percent