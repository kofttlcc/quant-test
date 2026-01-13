"""
models/arena/feature_selector.py - 特徵重要性分析器
===================================================
功能:
1. 計算 Permutation Importance (與模型無關)
2. 篩選 Top-K 特徵

Skill: quant-feature-eng
"""

import pandas as pd
import numpy as np
import logging
from sklearn.inspection import permutation_importance
from typing import List, Tuple, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureSelector:
    """
    特徵選擇器
    使用 Permutation Importance 評估特徵對模型預測能力的貢獻
    """
    
    def __init__(self, model: Any, n_repeats: int = 5, random_state: int = 42):
        """
        Args:
            model: 已訓練的 sklearn 兼容模型 (需有 predict 或 score 方法)
            n_repeats: 排列次數
            random_state: 隨機種子
        """
        self.model = model
        self.n_repeats = n_repeats
        self.random_state = random_state
        self.importance_df = pd.DataFrame()

    def compute_importance(self, X: pd.DataFrame, y: pd.Series, scoring: str = 'neg_mean_squared_error') -> pd.DataFrame:
        """
        計算特徵重要性
        
        Args:
            X: 特徵矩陣 (Validation Set)
            y: 標籤
            scoring: 評分指標 (e.g., 'r2', 'neg_mean_squared_error', 'accuracy')
            
        Returns:
            DataFrame: Index=Feature, Columns=[Importance, Std]
        """
        logger.info(f"Computing Permutation Importance (repeats={self.n_repeats})...")
        
        # 執行 Permutation Importance
        result = permutation_importance(
            self.model, X, y,
            n_repeats=self.n_repeats,
            random_state=self.random_state,
            scoring=scoring,
            n_jobs=-1  # 平行計算
        )
        
        # 整理結果
        perm_sorted_idx = result.importances_mean.argsort()
        
        importances = pd.DataFrame(
            result.importances[perm_sorted_idx].T,
            columns=X.columns[perm_sorted_idx]
        )
        
        # 轉置為 Feature 為 Index
        summary = pd.DataFrame({
            'Importance': result.importances_mean,
            'Std': result.importances_std
        }, index=X.columns).sort_values(by='Importance', ascending=False)
        
        self.importance_df = summary
        logger.info("Feature Importance Computation Completed.")
        return summary

    def select_top_k(self, k: int = 10) -> List[str]:
        """
        獲取 Top-K 重要特徵
        """
        if self.importance_df.empty:
            logger.warning("Importance not computed yet. Call compute_importance first.")
            return []
            
        top_k = self.importance_df.head(k).index.tolist()
        logger.info(f"Selected Top-{k} features: {top_k}")
        return top_k

if __name__ == "__main__":
    # Self-test
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.datasets import make_regression
    
    # Generate dummy data
    X, y = make_regression(n_samples=200, n_features=10, n_informative=3, noise=0.1, random_state=42)
    feature_names = [f"feat_{i}" for i in range(10)]
    X_df = pd.DataFrame(X, columns=feature_names)
    
    # Train dummy model
    model = RandomForestRegressor(random_state=42)
    model.fit(X_df, y)
    
    # Select features
    selector = FeatureSelector(model)
    imp = selector.compute_importance(X_df, y, scoring='r2')
    
    print("\nFeature Importance Head:")
    print(imp.head())
    
    top_3 = selector.select_top_k(3)
    # Informative features should be in top 3
