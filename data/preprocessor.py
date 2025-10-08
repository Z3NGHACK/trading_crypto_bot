import pandas as pd

class DataPreprocessor:
    def __init__(self, df):
        self.df = df.copy()
    
    def clean_data(self):
        '''Clean and prepare data'''
        # Remove duplicates
        self.df = self.df[~self.df.index.duplicated(keep='last')]
        
        # Fill missing values
        self.df = self.df.ffill()
        
        # Ensure numeric types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        return self.df