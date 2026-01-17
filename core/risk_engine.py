import pandas as pd
import numpy as np
import sys
import os

# FIX: Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import StockData

class RiskAnalyzer:
    def __init__(self, prices, returns):
        self.prices = prices
        self.returns = returns
    
    def calculate_metrics(self):
        """Core risk metrics"""
        vol = self.returns.std() * np.sqrt(252) * 100
        sharpe = (self.returns.mean() * 252) / (self.returns.std() * np.sqrt(252))
        
        risk_category = []
        for v in vol:
            if v < 20: cat = "🟢 LOW"
            elif v < 35: cat = "🟡 MEDIUM" 
            else: cat = "🔴 HIGH"
            risk_category.append(cat)
        
        var_95 = [np.percentile(self.returns[stock].dropna(), 5) * 100 
                 for stock in self.returns.columns]
        
        return pd.DataFrame({
            'Volatility (%)': vol.round(2),
            'Sharpe Ratio': sharpe.round(2),
            'VaR 95%': np.array(var_95).round(2),
            'Risk Level': risk_category
        }, index=self.returns.columns)
    
    def portfolio_risk(self):
        return round(self.returns.std(axis=1).mean() * np.sqrt(252) * 100, 2)

# TEST
if __name__ == "__main__":
    print("🔍 RISK ANALYSIS DAY 2\n")
    portfolio = StockData(['RELIANCE.NS', 'TCS.NS', 'AAPL'])
    prices, returns = portfolio.fetch_live()
    
    analyzer = RiskAnalyzer(prices, returns)
    risk_table = analyzer.calculate_metrics()
    port_risk = analyzer.portfolio_risk()
    
    print("📊 STOCK RISK REPORT:")
    print("=" * 50)
    print(risk_table)
    print(f"\n💼 PORTFOLIO RISK: {port_risk}%")
