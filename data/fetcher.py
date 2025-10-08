import pandas as pd
import logging
from data.exchange import ExchangeConnector
from config.settings import TRADING_PAIRS

class DataFetcher:
    def __init__(self):
        self.exchange = ExchangeConnector()
        self.logger = logging.getLogger(__name__)
        
        if not self.exchange.markets:
            self.logger.error("❌ No markets loaded during initialization")
        else:
            self.logger.info(f"✓ DataFetcher initialized with {len(self.exchange.markets)} markets")

    def fetch_and_store(self, symbol, timeframe, limit=100):
        """
        Fetch OHLCV data for a symbol and return as DataFrame
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '5m', '15m', '1h')
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            # Validate symbol is in config
            if symbol not in TRADING_PAIRS:
                self.logger.warning(f"Symbol {symbol} not in configured TRADING_PAIRS")
                return pd.DataFrame()
            
            # Check if markets are loaded
            if not self.exchange.markets:
                self.logger.warning("No markets loaded, cannot fetch OHLCV")
                return pd.DataFrame()
            
            # Check if symbol is available on exchange
            if symbol not in self.exchange.markets:
                self.logger.warning(f"Symbol {symbol} not available on exchange")
                available = [s for s in TRADING_PAIRS if s in self.exchange.markets]
                if available:
                    self.logger.info(f"Available symbols from config: {available[:5]}")
                return pd.DataFrame()
            
            # Fetch data from exchange
            self.logger.debug(f"Fetching OHLCV for {symbol} ({timeframe}, limit={limit})")
            data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not data:
                self.logger.warning(f"No OHLCV data returned for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            self.logger.info(f"✓ Fetched {len(df)} candles for {symbol} ({timeframe})")
            self.logger.debug(f"Latest candle: {df.tail(1)[['timestamp', 'close']].to_dict('records')[0]}")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}", exc_info=True)
            return pd.DataFrame()

    def fetch_multiple_pairs(self, symbols, timeframe, limit=100):
        """
        Fetch OHLCV data for multiple symbols
        
        Args:
            symbols: List of trading pairs
            timeframe: Candle timeframe
            limit: Number of candles to fetch
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        results = {}
        for symbol in symbols:
            df = self.fetch_and_store(symbol, timeframe, limit)
            if not df.empty:
                results[symbol] = df
            else:
                self.logger.warning(f"Skipping {symbol} - no data available")
        
        self.logger.info(f"✓ Fetched data for {len(results)}/{len(symbols)} symbols")
        return results

    def get_latest_prices(self, symbols=None):
        """
        Get current prices for symbols
        
        Args:
            symbols: List of symbols (defaults to TRADING_PAIRS)
            
        Returns:
            Dictionary mapping symbols to current prices
        """
        if symbols is None:
            symbols = TRADING_PAIRS
        
        prices = {}
        for symbol in symbols:
            if symbol in self.exchange.markets:
                price = self.exchange.get_current_price(symbol)
                if price:
                    prices[symbol] = price
        
        return prices

    def get_current_price(self, symbol):
        try:
            price = self.exchange.get_current_price(symbol)
            return price
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            return None
    def validate_data(self, df):
        """
        Validate OHLCV DataFrame
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating if data is valid
        """
        if df.empty:
            return False
        
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            self.logger.error(f"Missing required columns. Found: {df.columns.tolist()}")
            return False
        
        # Check for nulls
        if df[required_columns].isnull().any().any():
            self.logger.warning("Data contains null values")
            return False
        
        # Check for valid OHLC relationships
        invalid_ohlc = (df['high'] < df['low']) | (df['high'] < df['open']) | (df['high'] < df['close'])
        if invalid_ohlc.any():
            self.logger.warning("Data contains invalid OHLC relationships")
            return False
        
        return True