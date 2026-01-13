---
name: trad-fi-risk
description: 計算參數化/歷史模擬法 VaR、CVaR 以及下行風險調整後的 Sortino Ratio。
trigger: when_needed
language: zh-TW
adapted_from: skills/傳統金融/trad-fi-risk/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# ADVANCED-RISK-METRICS 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/trad-fi-risk
> **語言**: 繁體中文

## 概述

提供高階投資組合風險度量工具，超越傳統標準差 (Volatility)，重點關注左尾風險 (Left Tail Risk) 與下行偏差。包含風險價值 (VaR)、條件風險價值 (CVaR/Expected Shortfall) 及 Sortino Ratio。

---

## 使用情境

此技能適用於以下情況：
- 金融監管報告 (FRTB 規範推薦使用 CVaR 而非 VaR)
- 評估極端市場條件下的潛在損失
- 區分「好的波動」(上漲) 與「壞的波動」(下跌) 進行績效評估

---

## 核心指標定義

### 1. Value at Risk (VaR)
在給定置信水平 $\alpha$ (如 95%) 下，特定時間段內的最大預期損失。
- **歷史模擬法 (Historical VaR)**: 計算歷史收益率分佈的第 $1-\alpha$ 百分位數。不依賴正態分佈假設，能捕捉厚尾特徵。

### 2. Conditional VaR (CVaR / Expected Shortfall)
損失超過 VaR 閾值時的平均預期損失。
- **優勢**：滿足次可加性 (Sub-additivity)，是共順風險度量 (Coherent Risk Measure)。能反映尾部損失的嚴重程度。

### 3. Sortino Ratio
Sharpe Ratio 的改進版，僅將下行偏差 ($\sigma_d$) 視為風險，不懲罰上行波動。
$$\text{Sortino} = \frac{\bar{R} - R_f}{\sigma_d}$$
其中下行偏差 $\sigma_d = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (\min(0, R_i - \text{Target}))^2}$

---

## Python 實作範本

```python
import numpy as np

def calc_risk_metrics(returns, alpha=0.95, rf=0.0):
    """
    計算 VaR, CVaR 與 Sortino Ratio。
    
    Args:
        returns (np.array): 收益率序列 (百分比形式小數)
        alpha (float): 置信水平 (default 0.95)
        rf (float): 無風險利率
        
    Returns:
        dict: 各風險指標
    """
    if len(returns) == 0:
        return {}

    # 1. VaR & CVaR (Historical Method)
    # 取分佈的左尾 (損失是負收益)
    var_level = 1 - alpha
    var = np.percentile(returns, var_level * 100)
    
    # CVaR: 所有小於等於 VaR 的收益率的平均值
    tail_losses = returns[returns <= var]
    cvar = tail_losses.mean() if len(tail_losses) > 0 else var
    
    # 2. Sortino Ratio
    excess_ret = returns - rf
    # 僅考慮負收益部分 (下行風險)
    downside_ret = np.minimum(0, excess_ret)
    downside_dev = np.sqrt(np.mean(downside_ret**2))
    
    # 防止除零
    if downside_dev == 0:
        sortino = np.inf if excess_ret.mean() > 0 else -np.inf
    else:
        sortino = excess_ret.mean() / downside_dev
    
    return {
        'VaR': var,
        'CVaR': cvar,
        'Sortino': sortino,
        'DownsideDev': downside_dev
    }
```

## 驗證產出要求

- **收益分佈直方圖**：繪製收益率分佈直方圖，並用垂直線標記 VaR 與 CVaR 的位置。
    - VaR 線應標註為 "VaR (95%)"。
    - CVaR 線應標註為 "ES (95%)" (Expected Shortfall)。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
