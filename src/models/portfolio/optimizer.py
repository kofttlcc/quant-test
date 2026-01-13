"""
portfolio/optimizer.py - 高級投資組合優化器
=============================================
功能:
1. 均值方差優化 (Mean-Variance Optimization, MVO)
2. 層次風險平價 (Hierarchical Risk Parity, HRP)

Skill: quant-portfolio-opt
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform
import logging
from typing import Dict, Optional, Tuple, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    """
    通用投資組合優化器基類
    """
    def __init__(self, returns: pd.DataFrame):
        """
        Args:
            returns: 資產收益率 DataFrame (Time Series)
        """
        self.returns = returns
        self.assets = returns.columns.tolist()
        self.n_assets = len(self.assets)
        self.mu = returns.mean()
        self.cov = returns.cov()

class MeanVarianceOptimizer(PortfolioOptimizer):
    """
    均值方差優化 (Modern Portfolio Theory)
    """
    def __init__(self, returns: pd.DataFrame, risk_free_rate: float = 0.02):
        super().__init__(returns)
        self.rf = risk_free_rate

    def optimize(self, objective: str = 'max_sharpe', target_return: float = None) -> pd.Series:
        """
        執行優化
        
        Args:
            objective: 目標函數 ('max_sharpe', 'min_volatility')
            target_return: 目標年化收益率 (用於 min_volatility 約束)
            
        Returns:
            pd.Series: 最佳權重
        """
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # 權重和為 1
        ]
        
        bounds = tuple((0.0, 1.0) for _ in range(self.n_assets))  # No Short Selling
        
        initial_weights = self.n_assets * [1. / self.n_assets,]
        
        if objective == 'max_sharpe':
            # Max Sharpe = Min (-Sharpe)
            result = minimize(self._neg_sharpe_ratio, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
            
        elif objective == 'min_volatility':
            # 如果有目標收益約束
            if target_return is not None:
                # 收益約束: w * mu * 252 >= target
                constraints.append({'type': 'eq', 'fun': lambda x: np.sum(x * self.mu) * 252 - target_return})
            
            result = minimize(self._portfolio_volatility, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
            
        else:
            raise ValueError(f"Unknown objective: {objective}")
            
        if not result.success:
            logger.warning(f"Optimization failed: {result.message}")
            return pd.Series([1./self.n_assets]*self.n_assets, index=self.assets)
            
        return pd.Series(result.x, index=self.assets)

    def _portfolio_volatility(self, weights):
        return np.sqrt(np.dot(weights.T, np.dot(self.cov * 252, weights)))

    def _neg_sharpe_ratio(self, weights):
        p_ret = np.sum(self.returns.mean() * weights) * 252
        p_vol = self._portfolio_volatility(weights)
        return -(p_ret - self.rf) / p_vol

class HierarchicalRiskParity(PortfolioOptimizer):
    """
    層次風險平價 (HRP) - Lopez de Prado
    解決 MVO 對協方差矩陣噪聲敏感的問題
    """
    
    def optimize(self) -> pd.Series:
        # 1. Tree Clustering
        corr = self.returns.corr()
        dist = np.sqrt(0.5 * (1 - corr))
        link = linkage(squareform(dist), method='single')
        
        # 2. Quasi-Diagonalization (Sort Linkage)
        sort_ix = self._get_quasi_diag(link)
        sort_ix = [self.assets[i] for i in sort_ix]
        
        # Reorder Covariance
        df_cov = self.cov.loc[sort_ix, sort_ix]
        
        # 3. Recursive Bisection
        weights = self._get_rec_bipart(df_cov, sort_ix)
        
        return weights.sort_index()

    def _get_quasi_diag(self, link):
        # Sort clustered items by distance
        link = link.astype(int)
        sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
        num_items = link[-1, 3]  # number of original items
        
        while sort_ix.max() >= num_items:
            sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)  # make space
            df0 = sort_ix[sort_ix >= num_items]  # find clusters
            i = df0.index
            j = df0.values - num_items
            sort_ix[i] = link[j, 0]  # item 1
            df0 = pd.Series(link[j, 1], index=i + 1)
            sort_ix = pd.concat([sort_ix, df0])
            sort_ix = sort_ix.sort_index()
            sort_ix.index = range(sort_ix.shape[0])
            
        return sort_ix.tolist()

    def _get_cluster_var(self, cov, c_items):
        # Compute variance per cluster
        cov_slice = cov.loc[c_items, c_items]
        w = self._get_ivp(cov_slice).reshape(-1, 1)
        c_var = np.dot(np.dot(w.T, cov_slice), w)[0, 0]
        return c_var

    def _get_ivp(self, cov):
        # Inverse Variance Portfolio
        ivp = 1. / np.diag(cov)
        ivp /= ivp.sum()
        return ivp

    def _get_rec_bipart(self, cov, sort_ix):
        # Recursive Bisection
        w = pd.Series(1, index=sort_ix)
        c_items = [sort_ix]  # initialize all items in one cluster
        
        while len(c_items) > 0:
            c_items = [i[j:k] for i in c_items for j, k in ((0, len(i) // 2), (len(i) // 2, len(i))) if len(i) > 1]
            
            for i in range(0, len(c_items), 2):
                c0 = c_items[i]
                c1 = c_items[i + 1]
                
                c0_var = self._get_cluster_var(cov, c0)
                c1_var = self._get_cluster_var(cov, c1)
                
                alpha = 1 - c0_var / (c0_var + c1_var)
                
                w[c0] *= alpha
                w[c1] *= 1 - alpha
                
        return w

if __name__ == "__main__":
    # Self-test
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100)
    
    # 3 Assets
    # A & B highly correlated, C uncorrelated
    base = np.random.randn(100)
    df = pd.DataFrame(index=dates)
    df['A'] = base + np.random.normal(0, 0.2, 100) 
    df['B'] = base + np.random.normal(0, 0.2, 100)
    df['C'] = np.random.randn(100) # Uncorrelated
    
    print("--- Correlation Matrix ---")
    print(df.corr())
    
    # MVO Test
    mvo = MeanVarianceOptimizer(df)
    w_mvo = mvo.optimize('max_sharpe')
    print("\n[MVO] Max Sharpe Weights:")
    print(w_mvo)
    
    # HRP Test
    hrp = HierarchicalRiskParity(df)
    w_hrp = hrp.optimize()
    print("\n[HRP] Weights:")
    print(w_hrp)
    
    # HRP 應該給 A+B 較低的總權重 (因為高度相關風險)，給 C 較高權重
