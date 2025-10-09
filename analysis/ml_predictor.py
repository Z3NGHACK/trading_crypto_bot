import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os
import logging

class MLPredictor:
    def __init__(self, df, model_path='models/rf_model.pkl'):
        self.df = df
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_fitted = False
        
        # Load pre-trained model if it exists
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                self.is_fitted = True
                logging.info(f"Loaded pre-trained RandomForest model from {self.model_path}")
            except Exception as e:
                logging.error(f"Error loading model from {self.model_path}: {e}")
                self.is_fitted = False
        else:
            logging.info(f"No pre-trained model found at {self.model_path}. Will train new model.")
    
    def prepare_features(self):
        try:
            from analysis.technical import TechnicalAnalyzer
            ta = TechnicalAnalyzer(self.df)
            self.df['ema_50'] = ta.calculate_ema(50)
            self.df['rsi'] = ta.calculate_rsi()
            macd, _ = ta.calculate_macd()
            self.df['macd'] = macd
            self.df['target'] = (self.df['close'].shift(-1) > self.df['close']).astype(int)
            features = ['ema_50', 'rsi', 'macd']
            data = self.df[features + ['target']].dropna()
            return data[features], data['target']  # Returns DataFrame, preserving names
        except Exception as e:
            logging.error(f"Error preparing features: {e}")
            return None, None
    def train_model(self):
        """Train the RandomForest model and save it"""
        X, y = self.prepare_features()
        if X is None or y is None or len(X) < 10:
            logging.warning("Insufficient data for training ML model. Skipping.")
            return False
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            self.is_fitted = True
            pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, pred)
            logging.info(f"ML model trained. Test accuracy: {accuracy:.2f}")
            
            # Save the model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logging.info(f"Saved trained model to {self.model_path}")
            return True
        except Exception as e:
            logging.error(f"Error training ML model: {e}")
            self.is_fitted = False
            return False
    
    def predict_next(self):
        """Predict the next market move"""
        try:
            X, _ = self.prepare_features()
            if X is None or len(X) == 0:
                logging.warning("No valid features for ML prediction. Returning neutral.")
                return 'neutral', 0.5
            
            if not self.is_fitted:
                logging.info("ML model not fitted. Attempting to train.")
                if not self.train_model():
                    logging.warning("Failed to train ML model. Returning neutral.")
                    return 'neutral', 0.5
            
            latest = X.iloc[-1:].values
            prob = self.model.predict_proba(latest)[0][1]  # Prob of up
            if prob > 0.7:
                logging.debug(f"ML predicts bullish with probability {prob:.2f}")
                return 'bullish', prob
            elif prob < 0.3:
                logging.debug(f"ML predicts bearish with probability {1 - prob:.2f}")
                return 'bearish', 1 - prob
            logging.debug(f"ML predicts neutral with probability {prob:.2f}")
            return 'neutral', 0.5
        except Exception as e:
            logging.error(f"Error in ML prediction: {e}")
            return 'neutral', 0.5