"""
stat_arb/selector.py - 配對篩選器
===================================
功能:
1. 候選池生成 (Candidate Pool Generation)
2. 相關性篩選 (Correlation Screening)
3. 最佳配對選擇 (Best Pairs Selection)

Skill: quant-stat-arb
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Tuple, Dict
from itertools import combinations

try:
    from src.strategies.stat_arb.engine import StatArbEngine
except ImportError:
    from engine import StatArbEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PairsSelector:
    def __init__(self, engine: StatArbEngine = None):
        self.engine = engine if engine else StatArbEngine()
        
    def find_best_pairs(self, price_data: pd.DataFrame, top_n: int = 5) -> List[Dict]:
        """
        從價格數據中尋找最佳配對
        
        Args:
            price_data: DataFrame where columns are Tickers, index is Date
            top_n: 返回前 N 個配對
            
        Returns:
            List of dicts: [{'pair': ('A', 'B'), 'p_value': 0.01, 'beta': 1.2}, ...]
        """
        if price_data.shape[1] < 2:
            logger.warning("Need at least 2 assets to find pairs.")
            return []
            
        # 1. 相關性預篩選 (Correlation Pre-screening)
        # 計算相關係數矩陣
        corr_matrix = price_data.pct_change().corr()
        
        # 獲取所有可能的組合
        tickers = price_data.columns
        candidate_pairs = []
        
        # 只測試相關性高的配對 (> 0.8) 以節省協整測試時間
        corr_threshold = 0.8
        
        for t1, t2 in combinations(tickers, 2):
            if abs(corr_matrix.loc[t1, t2]) > corr_threshold:
                candidate_pairs.append((t1, t2))
                
        logger.info(f"Screened {len(candidate_pairs)} pairs with Correlation > {corr_threshold}")
        
        # 2. 協整測試 (Cointegration Test)
        valid_pairs = []
        
        for t1, t2 in candidate_pairs:
            s1 = price_data[t1]
            s2 = price_data[t2]
            
            try:
                is_coint, p_val, beta = self.engine.test_cointegration(s1, s2)
                
                if is_coint:
                    # 計算 Spread 的均值回歸力度 (Half-life)
                    spread = self.engine.calculate_spread(s1, s2, beta)
                    ou = self.engine.calculate_ou_params(spread)
                    
                    valid_pairs.append({
                        'pair': (t1, t2),
                        'p_value': p_val,
                        'beta': beta,
                        'correlation': corr_matrix.loc[t1, t2],
                        'half_life': ou.get('half_life', np.inf),
                        'ou_sigma': ou.get('sigma', 0)
                    })
            except Exception as e:
                logger.error(f"Error testing pair {t1}-{t2}: {e}")
                
        # 3. 排序與選擇
        # 按 p-value 排序 (越小越好)
        valid_pairs.sort(key=lambda x: x['p_value'])
        
        selected = valid_pairs[:top_n]
        logger.info(f"Found {len(selected)} cointegrated pairs. Returning top {top_n}.")
        
        return selected

if __name__ == "__main__":
    # Self-test
    dates = pd.date_range('2023-01-01', periods=200)
    data = pd.DataFrame(index=dates)
    
    # 構造數據
    base = np.cumsum(np.random.randn(200))
    data['A'] = base + np.random.randn(200)
    data['B'] = base * 1.2 + np.random.randn(200) # Cointegrated with A
    data['C'] = np.cumsum(np.random.randn(200)) # Random walk
    
    selector = PairsSelector()
    best_pairs = selector.find_best_pairs(data)
    
    for p in best_pairs:
        print(f"Pair: {p['pair']}, p={p['p_value']:.4f}, beta={p['beta']:.2f}")
