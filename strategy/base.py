from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name):
        self.name = name
        self.positions = []
    
    @abstractmethod
    def generate_signal(self, df, analysis):
        pass
    
    @abstractmethod
    def calculate_position_size(self, capital, risk_percent):
        pass
    
    def log(self, message):
        print(f"[{self.name}] {message}")