import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ChartVisualizer:
    def __init__(self, df):
        self.df = df
    
    def plot_full_analysis(self, highs, lows, order_blocks, signals):
        '''Create comprehensive trading chart'''
        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.6, 0.2, 0.2],
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=('Price & Structure', 'Volume', 'RSI')
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
        
        fig.update_layout(
            title='Trading Bot Analysis',
            xaxis_rangeslider_visible=False,
            height=800
        )
        
        return fig