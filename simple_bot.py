import time
import logging
import os
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class SimpleTradingBot:
    def __init__(self):
        self.running = False
        logging.info("Simple Trading Bot Initialized")
    
    def run(self):
        self.running = True
        logging.info("🚀 Starting Simple Trading Bot")
        
        count = 0
        try:
            while self.running:
                count += 1
                logging.info(f"Cycle #{count} - Bot is running...")
                time.sleep(5)  # Wait 5 seconds
                
        except KeyboardInterrupt:
            logging.info("🛑 Bot stopped by user")
        except Exception as e:
            logging.error(f"❌ Error: {e}")
        finally:
            logging.info("👋 Bot shutdown complete")

if __name__ == '__main__':
    bot = SimpleTradingBot()
    bot.run()