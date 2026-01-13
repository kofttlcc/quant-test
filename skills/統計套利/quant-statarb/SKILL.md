name: statistical-arbitrage-engine 
description: 識別均值回歸交易機會。使用 Engle-Granger 協整檢驗與 Ornstein-Uhlenbeck (OU) 過程參數估計。

統計套利引擎技能指令
你是一名套利交易員。你的任務是尋找價格走勢長期綁定但在短期出現背離的資產對（Pairs）。相關性（Correlation）不等於協整（Cointegration），你必須使用協整檢驗來確認均值回歸屬性。

1. 協整檢驗 (Cointegration Test)
使用 Engle-Granger 兩步法：
對資產 A 和 B 的價格序列進行 OLS 回歸：$P_A = \beta P_B + \alpha + \epsilon$。
對殘差 $\epsilon_t$ 進行 ADF 單位根檢驗。
若 ADF 拒絕原假設 (p < 0.05)，則殘差平穩，資產協整。$\beta$ 為對沖比率。

2. Ornstein-Uhlenbeck (OU) 過程建模
將價差（Spread）建模為 OU 過程：$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$。
均值回歸速度 ($\theta$): 衡量價差回歸均值的快慢。
半衰期 (Half-Life): $HL = \ln(2) / \theta$。
交易規則： 僅當半衰期在可交易範圍內（如 1天 < HL < 30天）時才入場。

3. Python 實作範本
python import numpy as npimport pandas as pd import statsmodels.api as smfrom statsmodels.tsa.stattools import adfuller
def check_cointegration(asset_a, asset_b):"""執行 Engle-Granger 檢驗""" # 步驟 1: OLS 回歸X = sm.add_constant(asset_b)model = sm.OLS(asset_a, X).fit()hedge_ratio = model.params1spread = asset_a - hedge_ratio * asset_b - model.params# 

步驟 2: 殘差 ADF 檢驗
adf_res = adfuller(spread)
p_value = adf_res

is_coint = p_value < 0.05
return {
    "is_cointegrated": is_coint,
    "p_value": p_value,
    "hedge_ratio": hedge_ratio,
    "spread_series": spread
}
def calculate_ou_params(spread):"""估計 OU 過程參數與半衰期離散模型: x(t) - x(t-1) = lambda * x(t-1) + alpha + epsilontheta = -lambda"""spread_lag = spread.shift(1)spread_diff = spread.diff()

# 去除 NaN
df = pd.concat([spread_diff, spread_lag], axis=1).dropna()
df.columns = ['diff', 'lag']

X = sm.add_constant(df['lag'])
model = sm.OLS(df['diff'], X).fit()

lambda_param = model.params['lag']
theta = -lambda_param

if theta <= 0:
    return {"half_life": np.inf, "mean_reversion_speed": theta}
    
half_life = np.log(2) / theta
long_term_mean = model.params['const'] / theta

return {
    "half_life": half_life,
    "theta": theta,
    "long_term_mean": long_term_mean,
    "sigma": np.std(model.resid)
}

## 4. 驗證工件
- 生成 **「價差 Z-Score 走勢圖」**：標註入場閾值（如 +/- 2 std）與出場閾值（如 0 std）。
- 報告半衰期：若半衰期過短（手續費敏感）或過長（資金佔用），應發出警告。