import ccxt
import logging
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from config.settings import API_KEY, API_SECRET, SANDBOX_MODE, EXCHANGE_ID

class ExchangeConnector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if SANDBOX_MODE:
            self.base_url = 'https://testnet.binance.vision'
            self.logger.info("Running in SANDBOX mode (testnet)")
        else:
            self.base_url = 'https://api.binance.com'
            self.logger.info("Running in PRODUCTION mode")
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.binance_client = ccxt.binance({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'timeout': 30000,
            'enableTestnet': SANDBOX_MODE,
            'urls': {
                'api': f'{self.base_url}/api/v3',
                'public': f'{self.base_url}/api/v3',
                'private': f'{self.base_url}/api/v3',
            },
            'options': {
                'defaultType': 'spot',
                'fetchCurrencies': False,
                'fetchMarkets': ['spot'],
                'adjustForTimeDifference': True,
                'recvWindow': 10000,
            }
        })
        if self._test_connection():
            self.markets = self._load_markets()
        else:
            self.logger.error("Failed to connect to exchange. Using fallback markets.")
            self.markets = self._create_manual_markets()

    def _test_connection(self):
        try:
            response = requests.get(f'{self.base_url}/api/v3/ping', timeout=10)
            if response.status_code == 200:
                mode = "Testnet" if SANDBOX_MODE else "Production"
                self.logger.info(f"✓ Successfully connected to Binance {mode}")
                return True
            else:
                self.logger.error(f"Connection failed with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Cannot reach Binance: {e}")
            return False

    def _load_markets(self):
        try:
            response = requests.get(f'{self.base_url}/api/v3/exchangeInfo', timeout=10)
            if response.status_code == 200:
                data = response.json()
                markets = {}
                for symbol_info in data['symbols']:
                    if symbol_info['status'] == 'TRADING':
                        symbol = f"{symbol_info['baseAsset']}/{symbol_info['quoteAsset']}"
                        markets[symbol] = {
                            'id': symbol_info['symbol'],
                            'symbol': symbol,
                            'base': symbol_info['baseAsset'],
                            'quote': symbol_info['quoteAsset'],
                            'active': True,
                            'type': 'spot',
                            'spot': True,
                            'info': symbol_info
                        }
                self.logger.info(f"✓ Loaded {len(markets)} trading pairs")
                return markets
            else:
                self.logger.warning(f"Failed to load markets: {response.status_code}")
                return self._create_manual_markets()
        except Exception as e:
            self.logger.warning(f"Could not load markets from API: {e}")
            return self._create_manual_markets()

    def _create_manual_markets(self):
        self.logger.info("Using fallback market definitions")
        common_pairs = [
            ('BTC', 'USDT'), ('ETH', 'USDT'), ('BNB', 'USDT'),
            ('SOL', 'USDT'), ('ADA', 'USDT'), ('XRP', 'USDT'),
            ('DOGE', 'USDT'), ('LINK', 'USDT'), ('DOT', 'USDT'),
            ('UNI', 'USDT')
        ]
        markets = {}
        for base, quote in common_pairs:
            symbol = f"{base}/{quote}"
            markets[symbol] = {
                'id': f'{base}{quote}',
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'active': True,
                'type': 'spot',
                'spot': True,
                'info': {'quantityPrecision': 4, 'pricePrecision': 2}
            }
        return markets

    def _create_signature(self, params):
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def fetch_ohlcv(self, symbol, timeframe, limit=100):
        try:
            if symbol not in self.markets:
                self.logger.warning(f"Symbol {symbol} not found in available markets")
                return []
            pair_id = self.markets[symbol]['id']
            params = {'symbol': pair_id, 'interval': timeframe, 'limit': limit}
            url = f'{self.base_url}/api/v3/klines'
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ohlcv = [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]), float(k[5])] for k in data]
                self.logger.debug(f"✓ Fetched {len(ohlcv)} candles for {symbol} ({timeframe})")
                return ohlcv
            else:
                self.logger.error(f"Failed to fetch OHLCV: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return []

    def get_current_price(self, symbol):
        try:
            if symbol not in self.markets:
                self.logger.warning(f"Symbol {symbol} not found in available markets")
                return None
            pair_id = self.markets[symbol]['id']
            url = f'{self.base_url}/api/v3/ticker/price'
            params = {'symbol': pair_id}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                self.logger.debug(f"Current price {symbol}: ${price:,.2f}")
                return price
            else:
                self.logger.error(f"Failed to fetch price: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching price for {symbol}: {e}")
            return None

    def get_account_balance(self):
        try:
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp, 'recvWindow': 10000}
            params['signature'] = self._create_signature(params)
            url = f'{self.base_url}/api/v3/account'
            headers = {'X-MBX-APIKEY': self.api_key}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                balance = {'free': {}, 'used': {}, 'total': {}}
                for b in data['balances']:
                    asset = b['asset']
                    free_amt = float(b['free'])
                    locked_amt = float(b['locked'])
                    total_amt = free_amt + locked_amt
                    if total_amt > 0:
                        balance['free'][asset] = free_amt
                        balance['used'][asset] = locked_amt
                        balance['total'][asset] = total_amt
                self.logger.info(f"✓ Account balance fetched: {len(balance['total'])} assets")
                return balance
            else:
                self.logger.error(f"Failed to fetch balance: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return None

    def get_open_orders(self, symbol):
        try:
            if symbol not in self.markets:
                self.logger.warning(f"Symbol {symbol} not found in available markets")
                return []
            pair_id = self.markets[symbol]['id']
            timestamp = int(time.time() * 1000)
            params = {'symbol': pair_id, 'timestamp': timestamp, 'recvWindow': 10000}
            params['signature'] = self._create_signature(params)
            url = f'{self.base_url}/api/v3/openOrders'
            headers = {'X-MBX-APIKEY': self.api_key}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                orders = response.json()
                self.logger.debug(f"Open orders for {symbol}: {len(orders)}")
                return orders
            else:
                self.logger.error(f"Failed to fetch orders: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching open orders for {symbol}: {e}")
            return []

    def place_order(self, symbol, side, order_type, quantity, price=None):
        try:
            if symbol not in self.markets:
                self.logger.error(f"Symbol {symbol} not found")
                return None
            pair_id = self.markets[symbol]['id']
            timestamp = int(time.time() * 1000)
            params = {
                'symbol': pair_id,
                'side': side.upper(),
                'type': order_type.upper(),
                'quantity': quantity,
                'timestamp': timestamp,
                'recvWindow': 10000
            }
            if price and order_type.upper() == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'
            params['signature'] = self._create_signature(params)
            url = f'{self.base_url}/api/v3/order'
            headers = {'X-MBX-APIKEY': self.api_key}
            response = requests.post(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                order = response.json()
                self.logger.info(f"✓ Order placed: {side} {quantity} {symbol} @ {price if price else 'MARKET'}")
                return order
            else:
                self.logger.error(f"Failed to place order: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return None

    def round_step_size(self, quantity, step_size):
        try:
            from decimal import Decimal, ROUND_DOWN
            return float(Decimal(str(quantity)).quantize(Decimal(str(step_size)), rounding=ROUND_DOWN))
        except Exception as e:
            self.logger.error(f"Error rounding quantity: {e}")
            return quantity