
"""
arena.py - Multi-Strategy Battle Arena (Phase 7.2 Enhanced)
==================================================
AI vs 傳統策略對抗平台
功能:
1. 獨立競技平台展示排名
2. 返回冠軍策略供回測使用
"""

import pandas as pd
import numpy as np

# Ensure project root is in path for local execution
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.backend.backtest_engine import Backtester
from src.models.strategy_logic import MomentumStrategy

# 嘗試導入其他策略
try:
    from src.models.strategy_enhancements import RSIReversionStrategy
    HAS_RSI = True
except ImportError:
    HAS_RSI = False

try:
    from src.models.arena.lstm_predictor import MLPPredictor
    HAS_MLP = True
except ImportError:
    HAS_MLP = False

try:
    from src.models.arena.tree_predictor import LightGBMPredictor
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False


class StrategyArena:
    """
    策略競技場 - AI vs 傳統策略對抗
    
    設計意圖:
    1. 展示場景: 獨立平台展示 AI 策略與傳統策略的最終排名
    2. 策略選擇: 提供競技場獲勝的 AI 策略供用戶使用
    """
    
    def __init__(self):
        self.backtester = Backtester()
        self.champion = None  # 當前冠軍策略
        self.last_results = []
        
        # 策略分類: AI vs 傳統
        self.strategies = {
            # === 傳統策略 (Traditional) ===
            "動能策略 (基準)": {
                "strategy": MomentumStrategy(window=20),
                "type": "Traditional",
                "description": "經典動能策略，跟隨趨勢"
            },
            "動能策略 (快速)": {
                "strategy": MomentumStrategy(window=10),
                "type": "Traditional",
                "description": "快速動能，適合短線"
            },
            "動能策略 (慢速)": {
                "strategy": MomentumStrategy(window=50),
                "type": "Traditional",
                "description": "慢速動能，減少噪音"
            },
        }
        
        # 動態添加 RSI 策略
        if HAS_RSI:
            self.strategies["RSI 均值回歸"] = {
                "strategy": RSIReversionStrategy(rsi_period=14),
                "type": "Traditional",
                "description": "均值回歸，超賣買入超買賣出"
            }
            
        # === AI 策略 ===
        if HAS_MLP:
            self.strategies["AI：神經網絡 (MLP)"] = {
                "strategy": MLPPredictor(),
                "type": "AI",
                "description": "多層感知機，學習非線性模式"
            }
            
        if HAS_LGBM:
            self.strategies["AI：梯度提升樹 (LightGBM)"] = {
                "strategy": LightGBMPredictor(),
                "type": "AI",
                "description": "梯度提升樹，特徵可解釋"
            }
        
    def run_battle(self, df: pd.DataFrame):
        """
        運行所有策略對決，返回排名表
        """
        results = []
        
        for name, config in self.strategies.items():
            strategy = config["strategy"]
            strategy_type = config["type"]
            description = config["description"]
            
            try:
                # Run Backtest
                bt_res = self.backtester.run_backtest(df.copy(), strategy)
                
                # Extract key metrics
                metrics = bt_res['metrics']
                
                results.append({
                    "Strategy": name,
                    "Type": strategy_type,  # AI 或 Traditional
                    "Description": description,
                    "Total Return": metrics['Total_Return'],
                    "Sharpe": metrics['Sharpe_Ratio'],
                    "Max DD": metrics['Max_Drawdown']
                })
            except Exception as e:
                print(f"Strategy {name} failed: {e}")
                
        # Sort by Sharpe Ratio
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df.sort_values(by="Sharpe", ascending=False, inplace=True)
            results_df["Rank"] = range(1, len(results_df) + 1)
            
            # 記錄冠軍
            self.champion = results_df.iloc[0].to_dict()
            self.last_results = results_df.to_dict(orient='records')
            
        return results_df.to_dict(orient='records')
    
    def get_champion(self) -> dict:
        """
        返回當前冠軍策略
        
        用於策略選擇功能：用戶可選擇使用競技場獲勝的策略
        """
        if self.champion:
            return {
                "name": self.champion.get("Strategy"),
                "type": self.champion.get("Type"),
                "sharpe": self.champion.get("Sharpe"),
                "return": self.champion.get("Total Return"),
                "description": self.champion.get("Description", "")
            }
        return None
    
    def get_ai_vs_traditional_summary(self) -> dict:
        """
        返回 AI vs 傳統策略的對比摘要
        """
        if not self.last_results:
            return {}
            
        ai_results = [r for r in self.last_results if r.get("Type") == "AI"]
        trad_results = [r for r in self.last_results if r.get("Type") == "Traditional"]
        
        ai_avg_sharpe = np.mean([r["Sharpe"] for r in ai_results]) if ai_results else 0
        trad_avg_sharpe = np.mean([r["Sharpe"] for r in trad_results]) if trad_results else 0
        
        ai_best = max(ai_results, key=lambda x: x["Sharpe"]) if ai_results else None
        trad_best = max(trad_results, key=lambda x: x["Sharpe"]) if trad_results else None
        
        return {
            "ai_count": len(ai_results),
            "traditional_count": len(trad_results),
            "ai_avg_sharpe": round(ai_avg_sharpe, 2),
            "traditional_avg_sharpe": round(trad_avg_sharpe, 2),
            "ai_winner": ai_best["Strategy"] if ai_best else None,
            "traditional_winner": trad_best["Strategy"] if trad_best else None,
            "overall_winner": "AI" if ai_avg_sharpe > trad_avg_sharpe else "Traditional"
        }

if __name__ == "__main__":
    # Self-Test
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
    
    from src.data_loader.downloader import fetch_data
    df = fetch_data("AAPL", start_date="2023-01-01")
    arena = StrategyArena()
    res = arena.run_battle(df)
    print("Arena Results:")
    for r in res:
        print(f"  {r['Rank']}. [{r['Type']}] {r['Strategy']}: Sharpe={r['Sharpe']:.2f}")
    
    print("\nChampion:", arena.get_champion())
    print("AI vs Traditional:", arena.get_ai_vs_traditional_summary())

