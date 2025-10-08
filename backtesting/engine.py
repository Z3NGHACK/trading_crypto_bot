import pandas as pd
from strategy.signals import SignalGenerator
from strategy.risk_management import RiskManager
from execution.portfolio import Portfolio

class BacktestEngine:
    def __init__(self, df, initial_capital=10000):
        self.df = df
        self.capital = initial_capital
        self.portfolio = Portfolio(initial_capital)
        self.signal_generator = SignalGenerator()
        self.risk_manager = RiskManager(initial_capital)
    
    def run_backtest(self, symbol, timeframe):
        '''Run backtest on historical data'''
        trades = []
        
        for i in range(50, len(self.df)):
            # Slice data up to current point
            historical_df = self.df.iloc[:i+1]
            
            # Perform analysis
            from analysis.technical import TechnicalAnalyzer
            from analysis.structure import MarketStructure
            from analysis.orderblock import OrderBlockDetector
            from analysis.volume import VolumeAnalyzer
            
            tech = TechnicalAnalyzer(historical_df)
            historical_df['ema_20'] = tech.calculate_ema(20)
            historical_df['ema_50'] = tech.calculate_ema(50)
            historical_df['rsi'] = tech.calculate_rsi()
            historical_df['atr'] = tech.calculate_atr()
            
            structure = MarketStructure(historical_df)
            highs, lows = structure.find_swing_points()
            trend = structure.detect_trend(highs, lows)
            
            ob_detector = OrderBlockDetector(historical_df)
            bullish_obs = ob_detector.detect_bullish_order_blocks()
            bearish_obs = ob_detector.detect_bearish_order_blocks()
            
            volume = VolumeAnalyzer(historical_df)
            volume_spike = volume.detect_volume_spike()
            
            analysis = {
                'trend': trend,
                'bullish_order_blocks': bullish_obs,
                'bearish_order_blocks': bearish_obs,
                'volume_spike': volume_spike
            }
            
            # Generate signal
            signal = self.signal_generator.generate_signal(historical_df, analysis)
            
            if signal['signal'] in ['BUY', 'SELL']:
                current_price = historical_df['close'].iloc[-1]
                direction = 'long' if signal['signal'] == 'BUY' else 'short'
                
                stop_loss = self.risk_manager.calculate_stop_loss(current_price, direction, historical_df['atr'].iloc[-1])
                take_profit = self.risk_manager.calculate_take_profit(current_price, direction)
                
                position_size = self.risk_manager.calculate_position_size(current_price, stop_loss)
                
                trade = {
                    'symbol': symbol,
                    'direction': direction,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'position_size': position_size,
                    'entry_time': historical_df.index[-1],
                    'status': 'open'
                }
                
                self.portfolio.add_position(trade)
                trades.append(trade)
                
                # Check for exits
                for pos in self.portfolio.positions[:]:
                    current_price = historical_df['close'].iloc[-1]
                    if pos['direction'] == 'long':
                        if current_price <= pos['stop_loss'] or current_price >= pos['take_profit']:
                            self.portfolio.close_position(pos, current_price)
                    else:
                        if current_price >= pos['stop_loss'] or current_price <= pos['take_profit']:
                            self.portfolio.close_position(pos, current_price)
        
        return trades, self.portfolio.capital