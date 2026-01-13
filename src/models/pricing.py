
from scipy.stats import norm
import numpy as np
import logging

logger = logging.getLogger(__name__)

class OptionPricingEngine:
    """
    基於 Black-Scholes-Merton 模型的歐式期權定價引擎。
    提供價格計算及完整 Greeks 分析。
    """
    
    @staticmethod
    def calculate_bs_greeks(S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'call') -> dict:
        """
        計算 Black-Scholes 價格與希臘值。
        
        Args:
            S: 標的資產價格
            K: 行權價
            T: 剩餘期限 (年)
            r: 無風險利率 (年化連續複利)
            sigma: 波動率 (年化)
            option_type: 'call' or 'put'
            
        Returns:
            dict: 包含 price, delta, gamma, vega, theta, rho
        """
        # 防止除零與負值錯誤
        if T <= 0:
            return {
                'price': max(0, S - K) if option_type == 'call' else max(0, K - S),
                'delta': 0.0, 'gamma': 0.0, 'vega': 0.0, 'theta': 0.0, 'rho': 0.0
            }
            
        T = np.maximum(T, 1e-10)
        sigma = np.maximum(sigma, 1e-10)
        
        d1 = (np.log(S/K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # 輔助變量
        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)
        
        # 計算 Delta & Price
        if option_type == 'call':
            price = S * cdf_d1 - K * np.exp(-r * T) * cdf_d2
            delta = cdf_d1
            rho = K * T * np.exp(-r * T) * cdf_d2
            theta = (- (S * sigma * pdf_d1) / (2 * np.sqrt(T)) 
                     - r * K * np.exp(-r * T) * cdf_d2)
        elif option_type == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = cdf_d1 - 1
            rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
            theta = (- (S * sigma * pdf_d1) / (2 * np.sqrt(T)) 
                     + r * K * np.exp(-r * T) * norm.cdf(-d2))
        else:
            raise ValueError("option_type must be 'call' or 'put'")
    
        # Gamma & Vega 對 Call/Put 相同
        gamma = pdf_d1 / (S * sigma * np.sqrt(T))
        vega = S * pdf_d1 * np.sqrt(T)
        
        # Vega 慣例: 每 1% 波動率變化
        # vega = vega / 100 
        # (這裡保持原始定義，由調用方處理單位)
        
        return {
            'price': float(price),
            'delta': float(delta),
            'gamma': float(gamma),
            'vega': float(vega),
            'theta': float(theta),
            'rho': float(rho)
        }

if __name__ == "__main__":
    # Self-Test
    print("--- SELF-TEST: pricing.py ---")
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    
    call_metrics = OptionPricingEngine.calculate_bs_greeks(S, K, T, r, sigma, 'call')
    put_metrics = OptionPricingEngine.calculate_bs_greeks(S, K, T, r, sigma, 'put')
    
    print(f"Call Price: {call_metrics['price']:.4f} (Expected ~10.45)")
    print(f"Put Price: {put_metrics['price']:.4f} (Expected ~5.57)")
    print(f"Put-Call Parity Check: {call_metrics['price'] - put_metrics['price']:.4f} vs {S - K * np.exp(-r*T):.4f}")
    
    if abs((call_metrics['price'] - put_metrics['price']) - (S - K * np.exp(-r*T))) < 1e-4:
        print("[TEST] SUCCESS: Put-Call Parity holds.")
    else:
        print("[TEST] FAILURE: Put-Call Parity violation.")
