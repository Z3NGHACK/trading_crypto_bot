import pandas as pd

class CorrelationAnalyzer:
    def __init__(self, main_df, other_dfs={}):  # dict of {asset: df}
        self.main_df = main_df
        self.other_dfs = other_dfs
    
    def calculate_correlation(self, period=30):
        corrs = {}
        for asset, df in self.other_dfs.items():
            aligned_main = self.main_df['close'].tail(period)
            aligned_other = df['close'].tail(period)
            corrs[asset] = aligned_main.corr(aligned_other)
        return corrs
    
    def predict_from_correlation(self, corrs, other_signal):
        # If highly correlated and other asset is bullish, predict same
        for asset, corr in corrs.items():
            if corr > 0.8 and other_signal == 'bullish':
                return 'bullish_correlated'
        return None