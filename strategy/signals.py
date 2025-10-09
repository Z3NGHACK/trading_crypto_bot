from .base import BaseStrategy
from config.settings import RSI_OVERSOLD, RSI_OVERBOUGHT
from analysis.technical import TechnicalAnalyzer
from analysis.structure import MarketStructure
from analysis.orderblock import OrderBlockDetector
from analysis.volume import VolumeAnalyzer
from analysis.sentiment import SentimentAnalyzer
from analysis.orderflow import OrderFlowAnalyzer
from analysis.correlation import CorrelationAnalyzer
from analysis.fibonacci import FibonacciAnalyzer
from analysis.ml_predictor import MLPredictor

class SignalGenerator(BaseStrategy):
    def __init__(self):
        super().__init__("Multi-Factor Strategy")
    
    def generate_signal(self, df, analysis, tech, exchange, symbol):
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
        
        # New: OBV divergence
        va = VolumeAnalyzer(df)
        obv_div = va.detect_obv_divergence()
        if obv_div == 'bullish_divergence':
            score += 2
            reasons.append("Bullish OBV divergence")
        
        # New: Stochastic and Ichimoku
        k, d = tech.calculate_stochastic()
        if k.iloc[-1] > d.iloc[-1] and k.iloc[-1] < 20:
            score += 2
            reasons.append("Stochastic bullish cross in oversold")
        
        tenkan, kijun, _, _, _ = tech.calculate_ichimoku()
        if current_price > max(tenkan.iloc[-1], kijun.iloc[-1]):
            score += 2
            reasons.append("Above Ichimoku cloud")
        
        # New: Fibonacci reversal
        fib = FibonacciAnalyzer(df)
        levels = fib.get_current_levels(highs, lows)
        fib_rev = fib.predict_reversal(current_price, levels)
        if fib_rev and 'reversal_at_0.618' in fib_rev[0]:
            score += 3
            reasons.append("Golden ratio reversal")
        
        # New: Sentiment (assume news_texts fetched externally)
        sent = SentimentAnalyzer(symbol.split('/')[0])
        news_texts = []  # In real: fetch from API
        sentiment = sent.analyze_news_sentiment(news_texts)
        if sentiment[0] == 'bullish':
            score += 2
            reasons.append("Bullish sentiment")
        
        # New: Order flow
        ofa = OrderFlowAnalyzer(exchange, symbol)
        imbalance = ofa.calculate_imbalance()
        if imbalance == 'bullish_pressure':
            score += 2
            reasons.append("Bullish order flow imbalance")
        
        # New: Correlation (assume other_dfs provided)
        corr_anal = CorrelationAnalyzer(df, {'ETH/USDT': df})  # Example
        corrs = corr_anal.calculate_correlation()
        corr_pred = corr_anal.predict_from_correlation(corrs, 'bullish')  # Assume other_signal
        if corr_pred == 'bullish_correlated':
            score += 1
            reasons.append("Bullish correlation")
        
        # New: ML prediction
        mlp = MLPredictor(df)
        ml_pred = mlp.predict_next()
        if ml_pred[0] == 'bullish':
            score += ml_pred[1] * 3  # Weighted by prob
            reasons.append(f"ML predicts bullish ({ml_pred[1]:.2f})")
        
        # BEARISH SIGNALS (similar updates)
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
        
        if obv_div == 'bearish_divergence':
            bearish_score += 2
            bearish_reasons.append("Bearish OBV divergence")
        
        if k.iloc[-1] < d.iloc[-1] and k.iloc[-1] > 80:
            bearish_score += 2
            bearish_reasons.append("Stochastic bearish cross in overbought")
        
        if current_price < min(tenkan.iloc[-1], kijun.iloc[-1]):
            bearish_score += 2
            bearish_reasons.append("Below Ichimoku cloud")
        
        if fib_rev and 'reversal_at_0.618' in fib_rev[0]:  # Can be bearish too depending on context
            bearish_score += 3
            bearish_reasons.append("Golden ratio reversal (bearish)")
        
        if sentiment[0] == 'bearish':
            bearish_score += 2
            bearish_reasons.append("Bearish sentiment")
        
        if imbalance == 'bearish_pressure':
            bearish_score += 2
            bearish_reasons.append("Bearish order flow imbalance")
        
        if ml_pred[0] == 'bearish':
            bearish_score += ml_pred[1] * 3
            bearish_reasons.append(f"ML predicts bearish ({ml_pred[1]:.2f})")
        
        # New: ML prediction
        ml_pred = analysis.get('ml_pred', ('neutral', 0.5))
        if ml_pred[0] == 'bullish':
            score += ml_pred[1] * 3  # Weighted by prob
            reasons.append(f"ML predicts bullish ({ml_pred[1]:.2f})")
        elif ml_pred[0] == 'bearish':
            bearish_score += ml_pred[1] * 3
            bearish_reasons.append(f"ML predicts bearish ({ml_pred[1]:.2f})")
        else:
            reasons.append("ML prediction neutral")
            
        # MACD for additional confidence
        macd, signal_line = tech.calculate_macd()
        if macd.iloc[-1] > signal_line.iloc[-1]:
            score += 2
            reasons.append("MACD bullish")
        else:
            bearish_score += 2
            bearish_reasons.append("MACD bearish")
        
        # Generate final signal with higher threshold for confluence
        if score >= 7 and score > bearish_score:  # Raised from 5 for better accuracy
            return {
                'signal': 'BUY',
                'score': score,
                'confidence': min(score / 15, 1.0),  # Normalized
                'reasons': reasons
            }
        elif bearish_score >= 7 and bearish_score > score:
            return {
                'signal': 'SELL',
                'score': bearish_score,
                'confidence': min(bearish_score / 15, 1.0),
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