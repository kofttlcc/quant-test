"""
bayesian_valuation.py - 貝葉斯估值模組
=========================================
版本: v1.0 (Phase 2 Sprint 1)
功能: 使用正態-正態共軛先驗更新估值參數

移植自: old-system/prob_engine.py
"""

import numpy as np
from scipy import stats
from typing import Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BayesianEstimate:
    """貝葉斯估計結果"""
    posterior_mean: float
    posterior_std: float
    prior_mean: float
    prior_std: float
    confidence_interval: Tuple[float, float]  # 95% CI


class BayesianValuator:
    """
    貝葉斯估值器
    使用正態-正態共軛先驗 (Normal-Normal Conjugate Prior) 更新估值參數
    """
    
    def update_parameter(
        self,
        prior_mean: float,
        prior_std: float,
        data_mean: float,
        data_std: float,
        n_samples: int = 10
    ) -> BayesianEstimate:
        """
        更新單個參數 (如 Growth Rate)
        
        Parameters:
        -----------
        prior_mean: 先驗均值 (行業基準)
        prior_std: 先驗標準差 (不確定性)
        data_mean: 觀測數據均值 (分析師預期/情緒調整後數值)
        data_std: 觀測數據噪聲 (分析師分歧度)
        n_samples: 觀測數據的樣本量權重 (權重越大，後驗越偏向數據)
        
        Returns:
        --------
        BayesianEstimate 包含後驗均值、標準差和置信區間
        """
        # 貝葉斯更新公式 (Normal-Normal)
        # Precision = 1 / Variance
        
        tau_0 = 1 / (prior_std ** 2)  # Prior precision
        tau_data = n_samples / (data_std ** 2)  # Data precision (Total)
        
        tau_post = tau_0 + tau_data
        
        # Posterior Mean = weighted average of prior mean and data mean
        post_mean = (tau_0 * prior_mean + tau_data * data_mean) / tau_post
        
        # Posterior Variance = 1 / Posterior Precision
        post_var = 1 / tau_post
        post_std = np.sqrt(post_var)
        
        # 95% 置信區間
        ci_lower = post_mean - 1.96 * post_std
        ci_upper = post_mean + 1.96 * post_std
        
        return BayesianEstimate(
            posterior_mean=post_mean,
            posterior_std=post_std,
            prior_mean=prior_mean,
            prior_std=prior_std,
            confidence_interval=(ci_lower, ci_upper)
        )
    
    def update_growth_rate(
        self,
        industry_growth: float,
        industry_uncertainty: float,
        analyst_estimate: float,
        analyst_dispersion: float,
        n_analysts: int = 5
    ) -> BayesianEstimate:
        """
        更新增長率估計
        
        Args:
            industry_growth: 行業平均增長率 (先驗)
            industry_uncertainty: 行業增長率不確定性
            analyst_estimate: 分析師平均預期
            analyst_dispersion: 分析師預期分歧度
            n_analysts: 分析師數量
            
        Returns:
            BayesianEstimate
        """
        return self.update_parameter(
            prior_mean=industry_growth,
            prior_std=industry_uncertainty,
            data_mean=analyst_estimate,
            data_std=analyst_dispersion,
            n_samples=n_analysts
        )
    
    def update_wacc(
        self,
        sector_wacc: float,
        sector_wacc_std: float,
        company_beta: float,
        risk_free_rate: float = 0.04
    ) -> BayesianEstimate:
        """
        更新 WACC 估計
        
        Args:
            sector_wacc: 行業平均 WACC
            sector_wacc_std: 行業 WACC 標準差
            company_beta: 公司 Beta
            risk_free_rate: 無風險利率
            
        Returns:
            BayesianEstimate
        """
        # 使用 CAPM 估算公司特定 WACC
        market_premium = 0.05  # 市場風險溢價
        company_wacc = risk_free_rate + company_beta * market_premium
        company_wacc_std = 0.01 * company_beta  # Beta 越高，不確定性越大
        
        return self.update_parameter(
            prior_mean=sector_wacc,
            prior_std=sector_wacc_std,
            data_mean=company_wacc,
            data_std=company_wacc_std,
            n_samples=3
        )
    
    def get_valuation_distribution(
        self,
        base_val: float,
        uncertainty_std: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """生成估值分佈 (用於繪圖)"""
        x = np.linspace(base_val - 4 * uncertainty_std, base_val + 4 * uncertainty_std, 100)
        y = stats.norm.pdf(x, base_val, uncertainty_std)
        return x, y


if __name__ == "__main__":
    print("--- SELF-TEST: bayesian_valuation.py ---")
    
    bv = BayesianValuator()
    
    # 測試增長率更新
    print("\n[TEST] Growth Rate Update")
    result = bv.update_growth_rate(
        industry_growth=0.08,      # 行業 8%
        industry_uncertainty=0.02, # 不確定性 2%
        analyst_estimate=0.12,     # 分析師預期 12%
        analyst_dispersion=0.01,   # 分析師分歧低
        n_analysts=5
    )
    print(f"Prior: {result.prior_mean:.1%} ± {result.prior_std:.1%}")
    print(f"Posterior: {result.posterior_mean:.1%} ± {result.posterior_std:.1%}")
    print(f"95% CI: [{result.confidence_interval[0]:.1%}, {result.confidence_interval[1]:.1%}]")
    
    # 測試 WACC 更新
    print("\n[TEST] WACC Update")
    wacc_result = bv.update_wacc(
        sector_wacc=0.09,
        sector_wacc_std=0.02,
        company_beta=1.2
    )
    print(f"Posterior WACC: {wacc_result.posterior_mean:.1%} ± {wacc_result.posterior_std:.1%}")
    
    print("\n--- SELF-TEST COMPLETE ---")
