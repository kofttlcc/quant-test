name: black-scholes-pricing-engine 
description: 基於 Black-Scholes-Merton 封閉解計算歐式期權價格及全套希臘值（Greeks）。適用於恆定波動率假設。

Black-Scholes 定價技能指令
你是一名衍生品量化專家。請構建定價引擎，計算歐式期權的理論價格及一階、二階敏感度指標。

1. 核心公式
$$d_1 = \frac{\ln(S/K) + (r + 0.5\sigma^2)T}{\sigma\sqrt{T}}$$$$d_2 = d_1 - \sigma\sqrt{T}$$

2. 希臘值 (Greeks) 計算清單
必須提供以下指標的解析解（Analytical Solution）：
- Delta ($\Delta$): $\partial V / \partial S$
- Gamma ($\Gamma$): $\partial^2 V / \partial S^2$ (注意 Gamma 對 Call/Put 是相同的)
- Vega ($\nu$): $\partial V / \partial \sigma$ (注意 Vega 通常以 "每 1% 波動率變化" 報價，需調整單位)
- Theta ($\Theta$): $\partial V / \partial t$ (注意通常為負值)
- Rho ($\rho$): $\partial V / \partial r$

3. Python 實作範本
使用 scipy.stats.norm 進行計算。代碼必須支持 NumPy 陣列輸入，以實現向量化計算。pythonfrom scipy.stats import normimport numpy as np
def bs_greeks(S, K, T, r, sigma, option_type='call'):d1 = (np.log(S/K) + (r + 0.5sigma**2)T) / (sigmanp.sqrt(T))d2 = d1 - sigmanp.sqrt(T)
if option_type == 'call':
    delta = norm.cdf(d1)
else:
    delta = norm.cdf(d1) - 1
    
gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
vega = S * norm.pdf(d1) * np.sqrt(T)

return {'delta': delta, 'gamma': gamma, 'vega': vega}