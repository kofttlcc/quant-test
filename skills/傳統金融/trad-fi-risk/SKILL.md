name: advanced-risk-metrics 
description: 計算參數化/歷史模擬法 VaR、CVaR 以及下行風險調整後的 Sortino Ratio。

高階風險度量技能指令
你是一名風控經理。請計算投資組合的尾部風險指標，重點關注下行風險。
1. Value at Risk (VaR) 與 CVaR
- 歷史模擬法 (Historical VaR): 計算歷史收益率分佈的第 $1-\alpha$ 百分位數（例如 5%）。
- 條件 VaR (CVaR/Expected Shortfall): 計算所有低於 VaR 閾值的收益率的平均值。這是比 VaR 更保守且數學性質更好的指標。

2. Sortino Ratio
不同於 Sharpe Ratio，Sortino 僅懲罰下行波動。
$$\text{Sortino} = \frac{\bar{R} - R_f}{\sigma_d}$$其中下行偏差 $\sigma_d$ 計算公式：$$\sigma_d = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (\min(0, R_i - \text{Target}))^2}$$

3. Python 實作範本
python import numpy as np
def calc_risk_metrics(returns, alpha=0.95, rf=0.0): # VaR & CVaR (Historical)var_level = 1 - alphavar = np.percentile(returns, var_level * 100)cvar = returns[returns <= var].mean()

# Sortino
excess_ret = returns - rf
downside_ret = np.minimum(0, excess_ret)
downside_dev = np.sqrt(np.mean(downside_ret**2))

sortino = excess_ret.mean() / downside_dev if downside_dev!= 0 else 0

return {'VaR': var, 'CVaR': cvar, 'Sortino': sortino}