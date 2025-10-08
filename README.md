# Trading Crypto Bot

A professional-grade algorithmic trading system for cryptocurrency markets implementing technical analysis, market structure analysis, and order block detection. Built with Python and designed for institutional-level trading on Binance Testnet.

## Overview

This trading engine executes systematic strategies across multiple cryptocurrency pairs with real-time market data processing, sophisticated signal generation, and comprehensive risk management. The system operates with a $10,000 simulated portfolio and provides real-time monitoring through a responsive web interface.

## Architecture

```
trading_crypto_bot/
├── config/
│   ├── settings.py           # Trading configuration and parameters
│   └── risk_config.py        # Risk management settings
├── core/
│   ├── exchange.py           # Exchange connectivity layer (CCXT)
│   ├── data_manager.py       # Real-time data processing pipeline
│   └── portfolio_manager.py  # Portfolio and position management
├── strategy/
│   ├── signals.py           # Multi-factor signal generation engine
│   ├── technical_analysis.py # EMA, RSI, ATR indicators
│   └── market_structure.py   # Order block and structure analysis
├── risk/
│   ├── position_sizing.py    # Kelly-based position sizing
│   └── risk_engine.py        # Real-time risk monitoring
├── monitoring/
│   ├── dashboard.py          # Performance analytics
│   └── alert_system.py       # Trade and risk alerts
├── tests/
│   ├── unit/                # Unit test suite
│   └── integration/         # Integration tests
├── main.py                  # Primary execution engine
├── monitor.html             # Real-time monitoring dashboard
├── requirements.txt         # Python dependencies
└── .env.example             # Environment template
```

## Key Features

### Advanced Analytics
- **Multi-timeframe Technical Analysis**: EMA crossovers, RSI divergence, ATR volatility
- **Market Structure Analysis**: Support/resistance, order block detection, breakouts
- **Multi-factor Signal Generation**: Weighted confidence scoring across technical and structural factors

### Institutional-Grade Risk Management
- **Portfolio-level Risk Controls**: 2% maximum risk per trade, correlation-adjusted position sizing
- **Dynamic Position Sizing**: Kelly Criterion-based sizing with drawdown protection
- **Real-time Risk Monitoring**: Margin utilization, concentration limits, volatility-adjusted stops

### Enterprise Infrastructure
- **Fault-tolerant Data Pipeline**: Real-time market data with reconnection logic
- **Modular Strategy Framework**: Pluggable strategy components with backtesting compatibility
- **Comprehensive Logging**: Structured logging with performance metrics and audit trails

## Installation & Setup

### Prerequisites
- Python 3.8+ with virtual environment support
- Git version control
- Binance Testnet account for API access

### Environment Setup

```bash
# Clone repository
git clone https://github.com/Z3NGHACK/trading_crypto_bot.git
cd trading_crypto_bot

# Create and activate virtual environment
python -m venv trading_bot_env
source trading_bot_env/bin/activate  # Linux/Mac
# trading_bot_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Binance Testnet API credentials
```

### Configuration

Update `config/settings.py` with your trading parameters:

```python
# Trading Parameters
TRADING_PAIRS = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ADA/USDT', 'BNB/USDT',
    'XRP/USDT', 'DOGE/USDT', 'LINK/USDT', 'DOT/USDT', 'UNI/USDT'
]

# Risk Parameters
INITIAL_CAPITAL = 10000
MAX_POSITION_RISK = 0.02  # 2% per trade
MAX_OPEN_TRADES = 3
LEVERAGE = 10

# Strategy Parameters
SIGNAL_CONFIDENCE_THRESHOLD = 0.5
TIMEFRAME = '15m'
ANALYSIS_INTERVAL = 60  # seconds
```

## Operation

### Starting the Trading Engine

```bash
# Start main trading system
python main.py

# In separate terminal - start monitoring dashboard
python -m http.server 8000
```

```
# Deactivate current environment
deactivate

# Delete the problematic environment
rm -rf trading_bot_env

# Create fresh environment
python -m venv trading_bot_env

# Activate (PowerShell)
.\trading_bot_env\Scripts\Activate.ps1

# Install only essential packages
pip install pandas ccxt python-dotenv
```

### Monitoring & Analytics

Access the real-time dashboard at `http://localhost:8000/monitor.html`

**Dashboard Features:**
- Real-time signal display with confidence scores
- Portfolio performance metrics and P&L tracking
- Position sizing and risk exposure monitoring
- Trade execution logs and performance analytics

## Trading Logic

### Signal Generation Framework

The system employs a multi-factor approach:

1. **Technical Indicators**
   - EMA Crossovers (12/26 period)
   - RSI Momentum (oversold/overbought conditions)
   - ATR-based volatility adjustments

2. **Market Structure Analysis**
   - Order block identification and validation
   - Support/resistance level testing
   - Breakout/breakdown confirmation

3. **Confidence Scoring**
   - Weighted composite score (0.0-1.0)
   - Minimum threshold: 0.5 for trade execution
   - Dynamic adjustment based on market regime

### Risk Management Protocol

- **Position Sizing**: Kelly-optimal sizing with 2% maximum portfolio risk
- **Stop-Loss**: ATR-based dynamic stops (2x ATR from entry)
- **Take-Profit**: Risk-reward ratio 1:2 minimum
- **Portfolio Constraints**: Maximum 3 concurrent positions, correlation limits

## Performance Monitoring

### Key Metrics Tracked
- **Win Rate**: Percentage of profitable trades
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Peak-to-trough decline
- **Portfolio Volatility**: Standard deviation of returns
- **Risk-Adjusted Performance**: Return per unit of risk

### Log Analysis
```bash
# Monitor system performance
tail -f logs/market_analysis.log

# Check for errors
grep "ERROR" logs/market_analysis.log

# Performance analytics
python monitoring/dashboard.py --performance-report
```

## Troubleshooting Guide

### Common Issues & Solutions

**No Trade Execution**
```python
# Check open trade limit
MAX_OPEN_TRADES = 5  # Increase if needed

# Verify signal confidence threshold
SIGNAL_CONFIDENCE_THRESHOLD = 0.4  # Lower for more signals
```

**Data Quality Issues**
```bash
# Validate exchange connectivity
python -c "from core.exchange import ExchangeConnector; print(ExchangeConnector().test_connection())"

# Check available trading pairs
python -c "from core.exchange import ExchangeConnector; print(ExchangeConnector().get_available_pairs())"
```

**Dashboard Display Issues**
```bash
# Clear and reset cache
rm -f data/cache.txt
touch data/cache.txt

# Verify data format
head -n 5 data/cache.txt
# Expected: TIMESTAMP|SYMBOL|SIGNAL|PRICE|CONFIDENCE|MARKET_SIZE
```

### Performance Optimization

**For Enhanced Throughput**
```python
# Reduce analysis interval for more frequent signals
ANALYSIS_INTERVAL = 30  # 30 seconds

# Increase parallel processing
MAX_WORKERS = 4  # For concurrent pair analysis
```

## Backtesting & Validation

The system architecture supports pluggable backtesting:

```python
# Run historical validation
python tests/integration/backtest_engine.py \
    --start-date 2024-01-01 \
    --end-date 2024-06-01 \
    --capital 10000
```

## Production Deployment

### Security Considerations
- API keys stored in environment variables only
- Regular key rotation procedures
- SSL/TLS encryption for all exchange communications
- Secure logging without sensitive data exposure

### Monitoring & Alerting
- Real-time performance dashboards
- SMS/email alerts for system exceptions
- Automated health checks and recovery procedures
- Daily performance reporting

## Disclaimer

This trading system is designed for educational and testing purposes on Binance Testnet. 

**Important Notes:**
- Historical performance does not guarantee future results
- Cryptocurrency trading involves substantial risk
- Always test strategies thoroughly before deploying capital
- Maintain appropriate risk management in live trading

## Support & Contribution

### Issue Reporting
1. Check existing issues in GitHub repository
2. Provide detailed system logs and configuration
3. Include reproduction steps for bugs

### Development Contributions
1. Fork repository and create feature branch
2. Implement changes with comprehensive tests
3. Submit pull request with performance validation

## License

MIT License - See LICENSE file for complete terms.

---

**System Requirements**: Python 3.8+, 4GB RAM, Stable Internet Connection  
**Recommended**: Multi-core processor, SSD storage, Low-latency network connection  
**Performance**: ~60% historical accuracy (backtested), Real-time execution < 2s latency

## Core Development Team
Lead Developer: Chea Senghak zeng@tradingbot.com

Core Developer: Chan Suvannet chansuvannet999@gmail.com