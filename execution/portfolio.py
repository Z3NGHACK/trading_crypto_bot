class Portfolio:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.positions = []
        self.closed_positions = []
    
    def add_position(self, position):
        self.positions.append(position)
    
    def get_open_positions_count(self):
        return len(self.positions)
    
    def update_portfolio(self, current_prices):
        """Update portfolio value based on current prices"""
        total_value = self.initial_capital
        
        for position in self.positions:
            symbol = position['symbol']
            if symbol in current_prices:
                current_price = current_prices[symbol]
                if position['direction'] == 'BUY':
                    pnl = (current_price - position['entry_price']) * position['position_size']
                else:  # SELL
                    pnl = (position['entry_price'] - current_price) * position['position_size']
                total_value += pnl
        
        return total_value
    
    def close_position(self, symbol, exit_price):
        """Close a position"""
        for i, position in enumerate(self.positions):
            if position['symbol'] == symbol:
                closed_position = position.copy()
                closed_position['exit_price'] = exit_price
                closed_position['exit_time'] = '2025-10-08 18:00:00'  # Placeholder
                self.closed_positions.append(closed_position)
                self.positions.pop(i)
                return True
        return False