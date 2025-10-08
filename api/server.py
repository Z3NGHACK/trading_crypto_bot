import sys
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/server.log',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(message)s'))
logging.getLogger('').addHandler(console)

# Set up sys.path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

try:
    from config.settings import (
        TRADING_PAIRS, PRIMARY_TIMEFRAME, LEVERAGE, MAX_OPEN_TRADES, SANDBOX_MODE,
        CONFIDENCE_THRESHOLD, INITIAL_CAPITAL
    )
except ImportError as e:
    logging.error(f"Error importing from config.settings: {e}")
    raise

app = Flask(__name__)
CORS(app)

bot = None
try:
    from core.bot import TradingBot
    bot = TradingBot()
    logging.info("TradingBot initialized successfully")
except Exception as e:
    logging.error(f"Error initializing TradingBot: {e}")

@app.route('/config', methods=['GET'])
def get_config():
    try:
        return jsonify({
            'tradingPairs': TRADING_PAIRS,
            'timeframe': PRIMARY_TIMEFRAME,
            'leverage': LEVERAGE,
            'maxPositions': MAX_OPEN_TRADES,
            'sandboxMode': SANDBOX_MODE,
            'confidenceThreshold': CONFIDENCE_THRESHOLD,
            'initialCapital': INITIAL_CAPITAL
        })
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return jsonify({'error': f'Failed to load config: {str(e)}'}), 500

@app.route('/performance', methods=['GET'])
def get_performance():
    try:
        if bot is None:
            raise Exception("TradingBot not initialized due to connection issues")
        return jsonify(bot.get_performance_metrics())
    except Exception as e:
        logging.error(f"Failed to load performance: {e}")
        return jsonify({
            'error': f'Failed to load performance: {str(e)}',
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'avg_confidence': 0.0
        }), 200

if __name__ == '__main__':
    logging.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)