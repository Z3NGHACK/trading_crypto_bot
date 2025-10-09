from sklearn.ensemble import RandomForestClassifier
import joblib  # For saving/loading models

class TradingModel:
    def __init__(self, model_path=None):
        if model_path:
            self.model = joblib.load(model_path)
        else:
            self.model = RandomForestClassifier(n_estimators=100)
    
    def save_model(self, path):
        joblib.dump(self.model, path)
    
    def predict(self, features):
        return self.model.predict(features)
    
    def predict_proba(self, features):
        return self.model.predict_proba(features)