---
name: trad-fi-pricing
description: 基於 Black-Scholes-Merton 封閉解計算歐式期權價格及全套希臘值（Greeks）。適用於恆定波動率假設。
trigger: when_needed
language: zh-TW
adapted_from: skills/傳統金融/trad-fi-pricing/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# BLACK-SCHOLES-PRICING-ENGINE 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/trad-fi-pricing
> **語言**: 繁體中文

## 概述

使用經典 Black-Scholes-Merton (BSM) 模型為歐式期權 (European Options) 定價。此引擎不僅輸出理論價格，還提供完整的希臘值 (Greeks) 風險敏感度指標，是衍生品交易與風險管理的基石。

---

## 使用情境

此技能適用於以下情況：
- 歐式期權定價（早於到期日不可行權）
- 波動率微笑不顯著，或僅需理論參考價時（假設恆定波動率）
- 需要計算 Delta 進行動態對沖 (Delta Hedging) 時

---

## 數學原理

### 1. 核心公式 ($d_1, d_2$)
$$d_1 = \frac{\ln(S/K) + (r + 0.5\sigma^2)T}{\sigma\sqrt{T}}$$
$$d_2 = d_1 - \sigma\sqrt{T}$$

### 2. 希臘值 (Greeks) 解析解
| Greek | 定義 | 公式特徵 |
| :--- | :--- | :--- |
| **Delta ($\Delta$)** | $\partial V / \partial S$ | Call: $N(d_1)$; Put: $N(d_1) - 1$ |
| **Gamma ($\Gamma$)** | $\partial^2 V / \partial S^2$ | $\frac{N'(d_1)}{S\sigma\sqrt{T}}$ (Call/Put 相同) |
| **Vega ($\nu$)** | $\partial V / \partial \sigma$ | $S N'(d_1) \sqrt{T}$ (Call/Put 相同) |
| **Theta ($\Theta$)** | $\partial V / \partial t$ | 通常為負值，隨時間流逝價值衰減 |
| **Rho ($\rho$)** | $\partial V / \partial r$ | 對無風險利率的敏感度 |

---

## Python 實作範本

此實作支援 NumPy 向量化輸入，可同時計算大量期權價格。

```python
from scipy.stats import norm
import numpy as np

def bs_greeks(S, K, T, r, sigma, option_type='call'):
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
    # 防止除零錯誤
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
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = cdf_d1 - 1
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2)
        theta = (- (S * sigma * pdf_d1) / (2 * np.sqrt(T)) 
                 + r * K * np.exp(-r * T) * norm.cdf(-d2))

    # Gamma & Vega 對 Call/Put 相同
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T)
    
    # Vega 通常以 "每 1% 波動率變化" 報價，這裡保持原始定義 (每 100% 變化)
    # 如需調整為常見慣例，使用 vega / 100
    
    return {
        'price': price,
        'delta': delta,
        'gamma': gamma,
        'vega': vega,
        'theta': theta,
        'rho': rho
    }
```

## 驗證產出要求

- **Greeks 3D 曲面圖** (可選)：繪製 Delta 或 Gamma 隨標的價格 (S) 與 剩餘期限 (T) 變化的曲面圖，以直觀理解非線性風險。
- **單調性檢查**：驗證 Call Price 是否隨 S 遞增，隨 K 遞減。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
