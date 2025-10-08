class BacktestMetrics:
    def __init__(self, trades, initial_capital, final_capital):
        self.trades = trades
        self.initial_capital = initial_capital
        self.final_capital = final_capital
    
    def calculate_metrics(self):
        '''Calculate key performance metrics'''
        total_trades = len(self.trades)
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'return_pct': 0
            }
        
        wins = sum(1 for trade in self.trades if trade.get('profit', 0) > 0)
        losses = sum(1 for trade in self.trades if trade.get('profit', 0) < 0)
        
        gross_profit = sum(trade.get('profit', 0) for trade in self.trades if trade.get('profit', 0) > 0)
        gross_loss = abs(sum(trade.get('profit', 0) for trade in self.trades if trade.get('profit', 0) < 0))
        
        win_rate = wins / total_trades if total_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        return_pct = ((self.final_capital - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'return_pct': return_pct
        }