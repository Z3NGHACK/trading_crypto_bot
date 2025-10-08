import pytest
from analysis.technical import TechnicalAnalyzer
import pandas as pd

def test_ema_calculation():
    df = pd.DataFrame({
        'close': [100, 101, 102, 103, 104]
    })
    analyzer = TechnicalAnalyzer(df)
    ema = analyzer.calculate_ema(3)
    assert len(ema) == len(df)
    assert all(ema >= df['close'].min())
    assert all(ema <= df['close'].max())