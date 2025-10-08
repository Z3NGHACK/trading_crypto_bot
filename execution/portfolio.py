class Portfolio:
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.positions = []
    
    def add_position(self, trade):
        '''Add a new position to the portfolio'''
        self.positions.append(trade)
        print(f"Added position: {trade['symbol']} {trade['direction']} @ {trade['entry_price']}")
    
    def close_position(self, position, exit_price):
        '''Close an existing position'''
        profit = (exit_price - position['entry_price']) * position['position_size']
        if position['direction'] == 'short':
            profit = (position['entry_price'] - exit_price) * position['position_size']
        self.capital += profit
        self.positions.remove(position)
        print(f"Closed position: {position['symbol']} @ {exit_price}, Profit: {profit:.2f}")
        return profit
    
    def update_portfolio(self, current_prices):
        '''Update portfolio with current prices'''
        total_value = self.capital
        for pos in self.positions:
            current_price = current_prices.get(pos['symbol'], pos['entry_price'])
            unrealized_pnl = (current_price - pos['entry_price']) * pos['position_size']
            if pos['direction'] == 'short':
                unrealized_pnl = (pos['entry_price'] - current_price) * pos['position_size']
            total_value += unrealized_pnl
        return total_value