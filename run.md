```bash


# Create fresh environment
python -m venv trading_bot_env

# Install dependencies
pip install -r requirements.txt

# Install only essential packages
pip install pandas ccxt python-dotenv

# Deactivate current environment
deactivate

# Create and activate virtual environment
trading_bot_env\Scripts\activate 

# Start main trading system
python main.py

# In separate terminal - start monitoring dashboard
python -m http.server 8000
```