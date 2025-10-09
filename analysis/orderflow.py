import pandas as pd
import numpy as np

class OrderFlowAnalyzer:
    def __init__(self, exchange, symbol, depth=10):  # Pass exchange from data/exchange.py
        self.exchange = exchange
        self.symbol = symbol
        self.depth = depth
        self.order_book = self.fetch_order_book()
    
    def fetch_order_book(self):
        try:
            ob = self.exchange.fetch_order_book(self.symbol, limit=self.depth)
            bids = pd.DataFrame(ob['bids'], columns=['price', 'size'])
            asks = pd.DataFrame(ob['asks'], columns=['price', 'size'])
            return {'bids': bids, 'asks': asks}
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return None
    
    def calculate_imbalance(self):
        if not self.order_book:
            return 'balanced'
        bid_volume = self.order_book['bids']['size'].sum()
        ask_volume = self.order_book['asks']['size'].sum()
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume)
        if imbalance > 0.2:
            return 'bullish_pressure'
        elif imbalance < -0.2:
            return 'bearish_pressure'
        return 'balanced'
    
    def detect_spoofing(self, historical_obs=None):
        # If historical order books provided, check deltas; else simple check
        if historical_obs is None:
            return False
        # Example: large sudden changes
        delta_bid = abs(historical_obs[-1]['bids']['size'].sum() - historical_obs[-2]['bids']['size'].sum())
        if delta_bid > historical_obs[-1]['bids']['size'].mean() * 2:
            return True  # Possible manipulation
        return False