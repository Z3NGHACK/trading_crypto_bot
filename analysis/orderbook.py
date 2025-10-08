import ccxt
from config.settings import EXCHANGE_ID

class OrderBookAnalyzer:
    def __init__(self, exchange, current_price):
        self.exchange = exchange
        self.current_price = current_price

    def fetch_order_book(self, symbol, limit=20):
        """Fetch order book snapshot."""
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            return orderbook['bids'], orderbook['asks']  # [[price, amount], ...]
        except Exception as e:
            print(f"Error fetching order book: {e}")
            return [], []

    def get_imbalance(self, symbol):
        """Calculate bid/ask imbalance (positive = bullish)."""
        bids, asks = self.fetch_order_book(symbol)
        if not bids or not asks:
            return 0.0
        bid_volume = sum(amount for price, amount in bids[:10])
        ask_volume = sum(amount for price, amount in asks[:10])
        imbalance = (bid_volume - ask_volume) / (bid_volume + ask_volume + 1e-8)
        return imbalance  # >0.2 = strong buy pressure, <-0.2 = sell pressure