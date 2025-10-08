import pandas as pd
import os
import logging
from data.fetcher import DataFetcher

class AccuracyAnalyzer:
    def __init__(self):
        self.historical_signals = []
        self.fetcher = DataFetcher()

    def update_from_cache(self, cache_lines):
        """Parse cache.txt for past signals and simulate outcomes."""
        self.historical_signals = []
        for line in cache_lines:
            try:
                parts = line.strip().split('|')
                if len(parts) < 12:
                    continue
                timestamp, symbol, signal, open_price, _, sl, tp, _, conf, _, _, reasons = parts
                if signal not in ['BUY', 'SELL']:
                    continue
                conf = float(conf.replace('Conf=', '').replace('%', '')) / 100
                entry = float(open_price.replace('Open=', ''))
                sl = float(sl.replace('SL=', ''))
                tp = float(tp.replace('TP=', ''))
                sig = {
                    'timestamp': timestamp,
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': conf,
                    'entry_price': entry,
                    'stop_loss': sl,
                    'take_profit': tp,
                    'reasons': reasons
                }
                outcome = self._simulate_outcome(sig)
                sig['outcome'] = outcome
                self.historical_signals.append(sig)
                logging.debug(f"Processed signal: {symbol} {signal} Outcome: {outcome}")
            except Exception as e:
                logging.error(f"Error parsing cache line: {line} - {e}")

    def _simulate_outcome(self, sig):
        """Simulate trade outcome using historical data."""
        df = self.fetcher.load_local_data(sig['symbol'], '15m')
        if df is None or len(df) < 2:
            logging.warning(f"No data for {sig['symbol']} at {sig['timestamp']}")
            return 'unknown'
        entry_time = pd.to_datetime(sig['timestamp'])
        df = df[df.index > entry_time].head(100)
        if len(df) == 0:
            logging.warning(f"No post-entry data for {sig['symbol']} at {sig['timestamp']}")
            return 'unknown'
        for _, row in df.iterrows():
            if sig['signal'] == 'BUY':
                if row['low'] <= sig['stop_loss']:
                    return 'loss'
                if row['high'] >= sig['take_profit']:
                    return 'win'
            elif sig['signal'] == 'SELL':
                if row['high'] >= sig['stop_loss']:
                    return 'loss'
                if row['low'] <= sig['take_profit']:
                    return 'win'
        return 'unknown'

    def get_recent_win_rate(self, confidence_min=0.8, lookback=100):
        """Compute win rate for high-confidence signals."""
        high_conf = [s for s in self.historical_signals[-lookback:] if s['confidence'] >= confidence_min and s['outcome'] != 'unknown']
        if not high_conf:
            return 0.0
        wins = sum(1 for s in high_conf if s['outcome'] == 'win')
        return (wins / len(high_conf)) * 100 if high_conf else 0.0

    def get_historical_performance(self):
        """Compute overall performance metrics from historical signals."""
        total_trades = len([s for s in self.historical_signals if s['outcome'] != 'unknown'])
        wins = sum(1 for s in self.historical_signals if s['outcome'] == 'win')
        losses = sum(1 for s in self.historical_signals if s['outcome'] == 'loss')
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0.0
        avg_confidence = sum(s['confidence'] for s in self.historical_signals) / len(self.historical_signals) if self.historical_signals else 0.0
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'avg_confidence': avg_confidence * 100
        }