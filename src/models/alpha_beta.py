
import statsmodels.api as sm
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class AlphaBetaAnalyzer:
    """
    執行 CAPM 回歸分析，分解資產收益為 Alpha (超額) 和 Beta (系統性)。
    """
    
    @staticmethod
    def calculate_capm(asset_ret: pd.Series, market_ret: pd.Series, rf: float = 0.0) -> dict:
        """
        計算 CAPM Beta 與 Alpha。
        
        Args:
            asset_ret (pd.Series): 資產收益率序列
            market_ret (pd.Series): 市場收益率序列
            rf (float): 無風險利率 (日頻，默認 0.0)
            
        Returns:
            dict: 包含 alpha, beta, p_values, r_squared 的字典
        """
        if len(asset_ret) < 20 or len(market_ret) < 20:
            logger.warning("Insufficient data for CAPM analysis (<20 samples).")
            return {}

        # 1. 數據對齊
        df = pd.concat([asset_ret, market_ret], axis=1).dropna()
        df.columns = ['asset', 'market']
        
        if df.empty:
            return {}
        
        # 2. 計算超額收益
        # 這裡假設 rf 是常數 scalar，如果需要支持 Series rf，可擴展
        y = df['asset'] - rf
        x = df['market'] - rf
        
        # 3. 添加常數項 (Alpha)
        X = sm.add_constant(x)
        
        # 4. 擬合模型
        try:
            model = sm.OLS(y, X).fit()
            
            return {
                'alpha': float(model.params['const']),
                'beta': float(model.params['market']),
                'alpha_pvalue': float(model.pvalues['const']),
                'beta_pvalue': float(model.pvalues['market']),
                'r_squared': float(model.rsquared),
                'n_obs': int(model.nobs)
            }
        except Exception as e:
            logger.error(f"CAPM Regression failed: {e}")
            return {}

if __name__ == "__main__":
    print("--- SELF-TEST: alpha_beta.py ---")
    np.random.seed(42)
    # Market: Normal returns
    mkt = pd.Series(np.random.normal(0.0005, 0.01, 100), name='market')
    # Asset: Beta=1.5, Alpha=0.0002
    asset = 1.5 * mkt + 0.0002 + np.random.normal(0, 0.005, 100)
    asset.name = 'asset'
    
    res = AlphaBetaAnalyzer.calculate_capm(asset, mkt, rf=0.0)
    print("Results:", res)
    
    if 1.3 < res['beta'] < 1.7:
        print(f"[TEST] SUCCESS: Beta {res['beta']:.2f} within range.")
    else:
        print("[TEST] FAILURE: Beta estimation incorrect.")
