from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class MLTrainer:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.features = ['rsi', 'ema_20', 'ema_50', 'imbalance', 'volume_spike']

    def train(self, signals):
        """Train model on historical signals."""
        X = []
        y = []
        for sig in signals:
            X.append([sig.get(f, 0) for f in self.features])
            y.append(1 if sig['outcome'] == 'win' else 0)
        if X and y:
            self.model.fit(X, y)