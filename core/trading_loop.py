import time
import logging
from core.bot import TradingBot
from config.settings import TRADING_PAIRS, ANALYSIS_INTERVAL

def start_trading_loop(bot: TradingBot):
    """Main trading loop."""
    bot.running = True
    logging.info("Trading loop started.")
    cycle = 0
    try:
        while bot.running:
            cycle += 1
            logging.info(f"Cycle #{cycle}")
            for symbol in TRADING_PAIRS:
                bot.analyze_and_execute(symbol)
            bot.update_portfolio_values()
            time.sleep(ANALYSIS_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Loop stopped by user.")
    finally:
        logging.info("Trading loop shutdown.")