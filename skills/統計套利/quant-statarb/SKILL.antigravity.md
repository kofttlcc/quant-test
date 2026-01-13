---
name: statistical-arbitrage-engine
description: 識別均值回歸交易機會。使用 Engle-Granger 協整檢驗與 Ornstein-Uhlenbeck (OU) 過程參數估計。
trigger: when_needed
language: zh-TW
adapted_from: skills/統計套利/quant-statarb/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# STATISTICAL-ARBITRAGE-ENGINE 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-statarb
> **語言**: 繁體中文

## 概述

識別價格走勢長期綁定但在短期出現背離的資產對（Pairs）。通過協整檢驗確認均值回歸屬性，並使用 Ornstein-Uhlenbeck (OU) 過程對價差（Spread）進行建模，以精確捕捉套利機會。

---

## 使用情境

此技能適用於以下情況：
- 開發配對交易（Pairs Trading）策略時。
- 需要驗證兩個相關資產是否具有長期穩定的線性關係（協整性）時。
- 計算價差的均值回歸速度與半衰期，以制定進出場規則時。

---

## 數學原理

### 1. 協整檢驗 (Cointegration Test)
使用 Engle-Granger 兩步法：
1.  **OLS 回歸**：對資產 A 和 B 的價格序列進行回歸 $P_A = \beta P_B + \alpha + \epsilon$。
2.  **ADF 檢驗**：對殘差 $\epsilon_t$ 進行單位根檢驗。若 ADF 拒絕原假設 ($p < 0.05$)，則殘差平穩，資產協整。$\beta$ 為對沖比率。

### 2. Ornstein-Uhlenbeck (OU) 過程
將價差建模為隨機微分方程：
$$dX_t = \theta(\mu - X_t)dt + \sigma dW_t$$
- **均值回歸速度 ($\theta$)**：衡量價差回歸均值的快慢。
- **半衰期 (Half-Life)**：$HL = \frac{\ln(2)}{\theta}$。這是價差回歸到均值一半距離所需的預期時間。

---

## 處理策略指南

1.  **資產篩選**：首先利用相關性進行初步篩選，再進行嚴格的協整檢驗。
2.  **參數估計**：將 OU 過程離散化為 AR(1) 模型進行參數估計：
    $$x_t - x_{t-1} = \lambda x_{t-1} + \alpha + \epsilon$$
    其中 $\theta = -\lambda$。
3.  **交易規則制定**：僅當半衰期在可交易範圍內（如 1 天 < HL < 30 天）才視為有效機會。過短意味著交易成本過高，過長意味著資金佔用過久。

---

## Python 實作範本

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller

def check_cointegration(asset_a, asset_b):
    """
    執行 Engle-Granger 檢驗
    
    Returns:
        dict: 包含協整狀態、P值、對沖比率與價差序列
    """
    # 步驟 1: OLS 回歸
    X = sm.add_constant(asset_b)
    # 確保數據對齊且無 NaN
    common_idx = asset_a.index.intersection(asset_b.index)
    
    y = asset_a.loc[common_idx]
    x = X.loc[common_idx]
    
    model = sm.OLS(y, x).fit()
    hedge_ratio = model.params.iloc[1]
    spread = y - hedge_ratio * x.iloc[:, 1] - model.params.iloc[0]
    
    # 步驟 2: 殘差 ADF 檢驗
    adf_res = adfuller(spread)
    p_value = adf_res[1]
    
    is_coint = p_value < 0.05
    return {
        "is_cointegrated": is_coint,
        "p_value": p_value,
        "hedge_ratio": hedge_ratio,
        "spread_series": spread
    }

def calculate_ou_params(spread):
    """
    估計 OU 過程參數與半衰期
    離散模型: x(t) - x(t-1) = lambda * x(t-1) + alpha + epsilon
    theta = -lambda
    """
    spread_lag = spread.shift(1)
    spread_diff = spread.diff()
    
    # 去除 NaN
    df = pd.concat([spread_diff, spread_lag], axis=1).dropna()
    df.columns = ['diff', 'lag']
    
    X = sm.add_constant(df['lag'])
    model = sm.OLS(df['diff'], X).fit()
    
    lambda_param = model.params['lag']
    theta = -lambda_param
    
    # 如果 theta <= 0，表示均值發散，非均值回歸過程
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
```

## 驗證產出要求

- **價差 Z-Score 走勢圖**：將價差標準化後繪圖，並標註入場閾值（如 +/- 2 std）與出場閾值（如 0 std）。
- **半衰期報告**：計算並報告策略的半衰期。若半衰期在合理範圍外，應發出警告。
- **協整穩定性**：(進階) 使用滾動窗口檢驗協整關係的穩定性。

---

## 專案整合

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
