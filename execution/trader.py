from config.settings import MAX_OPEN_TRADES

class Trader:
    def __init__(self, exchange, risk_manager):
        self.exchange = exchange
        self.risk_manager = risk_manager
        self.open_positions = []
    
    def execute_trade(self, signal, symbol, df):
        if signal['signal'] == 'HOLD':
            return None
        
        if len(self.open_positions) >= MAX_OPEN_TRADES:
            print(f"Cannot execute trade: Max open trades ({MAX_OPEN_TRADES}) reached")
            return None
        
        current_price = df['close'].iloc[-1]
        atr = df['atr'].iloc[-1] if 'atr' in df else None
        
        direction = 'long' if signal['signal'] == 'BUY' else 'short'
        
        # Calculate risk parameters
        stop_loss = self.risk_manager.calculate_stop_loss(current_price, direction, atr)
        take_profit = self.risk_manager.calculate_take_profit(current_price, direction)
        
        # Validate trade
        valid, message = self.risk_manager.validate_trade(
            current_price, stop_loss, take_profit, direction
        )
        
        if not valid:
            print(f"❌ Trade rejected: {message}")
            return None
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(current_price, stop_loss)
        
        # Place order (in sandbox mode, simulate order)
        order = self.exchange.place_order(symbol, 'limit', signal['signal'].lower(), position_size, current_price)
        
        if order:
            trade = {
                'symbol': symbol,
                'direction': direction,
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'position_size': position_size,
                'confidence': signal['confidence'],
                'reasons': signal['reasons'],
                'status': 'open',
                'order_id': order.get('id') if order else None
            }
            
            self.open_positions.append(trade)
            print(f"\n📊 TRADE SIGNAL")
            print(f"Symbol: {symbol}")
            print(f"Direction: {direction.upper()}")
            print(f"Entry: ${current_price:.2f}")
            print(f"Stop Loss: ${stop_loss:.2f}")
            print(f"Take Profit: ${take_profit:.2f}")
            print(f"Position Size: {position_size:.4f}")
            print(f"Reasons: {', '.join(signal['reasons'])}")
            
            return trade
        
        return None
    
    def monitor_positions(self, df):
        '''Monitor open positions and close if SL/TP hit'''
        current_price = df['close'].iloc[-1]
        closed_trades = []
        
        for pos in self.open_positions[:]:
            if pos['direction'] == 'long':
                if current_price <= pos['stop_loss']:
                    profit = (pos['stop_loss'] - pos['entry_price']) * pos['position_size']
                    closed_trades.append(self.close_position(pos, pos['stop_loss'], 'Stop Loss'))
                elif current_price >= pos['take_profit']:
                    profit = (pos['take_profit'] - pos['entry_price']) * pos['position_size']
                    closed_trades.append(self.close_position(pos, pos['take_profit'], 'Take Profit'))
            else:  # short
                if current_price >= pos['stop_loss']:
                    profit = (pos['entry_price'] - pos['stop_loss']) * pos['position_size']
                    closed_trades.append(self.close_position(pos, pos['stop_loss'], 'Stop Loss'))
                elif current_price <= pos['take_profit']:
                    profit = (pos['entry_price'] - pos['take_profit']) * pos['position_size']
                    closed_trades.append(self.close_position(pos, pos['take_profit'], 'Take Profit'))
        
        return closed_trades
    
    def close_position(self, position, exit_price, reason):
        '''Close a position'''
        profit = (exit_price - position['entry_price']) * position['position_size']
        if position['direction'] == 'short':
            profit = (position['entry_price'] - exit_price) * position['position_size']
        
        self.open_positions.remove(position)
        print(f"Closed position: {position['symbol']} @ {exit_price:.2f}, Reason: {reason}, Profit: {profit:.2f}")
        
        return {
            'symbol': position['symbol'],
            'profit': profit,
            'exit_price': exit_price,
            'reason': reason
        }