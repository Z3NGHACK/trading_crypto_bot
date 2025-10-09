import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from .models import TradingModel

def train_model(df, features, target='target', save_path='model.pkl'):
    X = df[features]
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    model = TradingModel()
    model.model.fit(X_train, y_train)
    pred = model.model.predict(X_test)
    acc = accuracy_score(y_test, pred)
    print(f"Model accuracy: {acc}")
    
    model.save_model(save_path)
    return model, acc