import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analysis.technical import TechnicalAnalyzer

class ChartVisualizer:
    def __init__(self, df):
        self.df = df
    
    def plot_full_analysis(self, highs, lows, order_blocks, signals):
        '''Create comprehensive trading chart'''
        fig = make_subplots(
            rows=4, cols=1,  # Added row for RSI and MACD
            row_heights=[0.5, 0.2, 0.15, 0.15],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & Structure', 'Volume', 'RSI', 'MACD')
        )
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=self.df.index,
            open=self.df['open'],
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            name='Price'
        ), row=1, col=1)
        
        # Swing highs
        if highs:
            fig.add_trace(go.Scatter(
                x=[h[0] for h in highs],
                y=[h[1] for h in highs],
                mode='markers',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                name='Swing Highs'
            ), row=1, col=1)
        
        # Swing lows
        if lows:
            fig.add_trace(go.Scatter(
                x=[l[0] for l in lows],
                y=[l[1] for l in lows],
                mode='markers',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                name='Swing Lows'
            ), row=1, col=1)
        
        # Order blocks
        for ob in order_blocks:
            fig.add_shape(
                type='rect',
                x0=ob['index'], x1=len(self.df),
                y0=ob['bottom'], y1=ob['top'],
                fillcolor='green' if ob['type'] == 'bullish' else 'red',
                opacity=0.2,
                line=dict(width=0),
                row=1, col=1
            )
        
        # Volume
        colors = ['red' if self.df['close'].iloc[i] < self.df['open'].iloc[i] 
                  else 'green' for i in range(len(self.df))]
        fig.add_trace(go.Bar(
            x=self.df.index,
            y=self.df['volume'],
            marker_color=colors,
            name='Volume'
        ), row=2, col=1)
        
        # New: RSI
        ta = TechnicalAnalyzer(self.df)
        rsi = ta.calculate_rsi()
        fig.add_trace(go.Scatter(x=self.df.index, y=rsi, name='RSI', line=dict(color='purple')), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
        
        # New: MACD
        macd, signal = ta.calculate_macd()
        fig.add_trace(go.Scatter(x=self.df.index, y=macd, name='MACD', line=dict(color='blue')), row=4, col=1)
        fig.add_trace(go.Scatter(x=self.df.index, y=signal, name='Signal', line=dict(color='orange')), row=4, col=1)
        
        fig.update_layout(
            title='Trading Bot Analysis',
            xaxis_rangeslider_visible=False,
            height=1000  # Increased for new subplots
        )
        
        return fig