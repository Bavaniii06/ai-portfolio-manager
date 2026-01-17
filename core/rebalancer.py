import pandas as pd
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import StockData
from core.portfolio import PortfolioAnalyzer

class Rebalancer:
    def __init__(self):
        self.target_alloc = 33.33  # Equal weight target
        self.max_alloc = 30.0      # Max per stock
        self.portfolio = PortfolioAnalyzer()
    
    def analyze_allocation(self):
        """Get current portfolio state"""
        summary, total, over, under = self.portfolio.analyze()
        current_alloc = summary['Allocation %']
        return summary, current_alloc
    
    def generate_signals(self, current_alloc):
        """AI Rebalancing recommendations"""
        signals = []
        
        for stock in current_alloc.index:
            alloc = current_alloc[stock]
            
            if alloc > self.max_alloc:
                action = "🔴 REDUCE"
                weight = self.target_alloc
            elif alloc < 20:
                action = "🟢 BUY" 
                weight = self.target_alloc
            else:
                action = "🟡 HOLD"
                weight = alloc
            
            signals.append({
                'Stock': stock,
                'Current %': alloc,
                'Target %': weight,
                'Action': action
            })
        
        return pd.DataFrame(signals)
    
    def execute_report(self):
        """Complete rebalancing report"""
        print("⚖️  AI REBALANCING ENGINE - DAY 4\n")
        summary, current_alloc = self.analyze_allocation()
        signals = self.generate_signals(current_alloc)
        
        print("🎯 CURRENT ALLOCATION:")
        print(summary[['Price', 'Value', 'Allocation %']])
        
        print("\n🔄 REBALANCING SIGNALS:")
        print("=" * 60)
        print(signals.round(2))
        
        # Calculate required trades
        trades = []
        for _, row in signals.iterrows():
            if row['Action'] == '🔴 REDUCE':
                trades.append(f"SELL {row['Stock']}: {row['Current %']:.1f}% → {row['Target %']:.1f}%")
            elif row['Action'] == '🟢 BUY':
                trades.append(f"BUY  {row['Stock']}: {row['Current %']:.1f}% → {row['Target %']:.1f}%")
        
        print(f"\n📋 RECOMMENDED TRADES ({len([t for t in trades if 'BUY' in t or 'SELL' in t])} trades):")
        for trade in trades:
            print(f"  {trade}")

# TEST DAY 4 (CORE MODULE 🔥)
if __name__ == "__main__":
    rebalancer = Rebalancer()
    rebalancer.execute_report()
