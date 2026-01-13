---
name: data-gov-interp
description: 應用布朗橋隨機過程對金融時間序列的缺失值進行插值。用於保持數據的局部波動率結構，防止線性插值導致的方差塌陷。
trigger: when_needed
language: zh-TW
adapted_from: skills/數據治理/data-gov-interp/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# BROWNIAN-BRIDGE-INTERPOLATION 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/data-gov-interp
> **語言**: 繁體中文

## 概述

應用布朗橋隨機過程對金融時間序列的缺失值進行插值。此方法專用於保持數據的局部波動率結構，防止線性插值導致的方差塌陷問題，特別適用於 VaR (Value at Risk) 計算場景。

---

## 使用情境

此技能適用於以下情況：
- 修復 OHLC 價格序列的缺失值時
- 缺口長度大於等於 2 個週期時（缺口 < 2 個週期可考慮線性插值）
- 需要保持原始序列的波動率特徵以進行風險模型回測時

---

## 數學原理

對於已知端點 $P_{start}$ (時間 $t_0$) 和 $P_{end}$ (時間 $T$) 的缺口，插值 $P_t$ 由以下公式生成:

$$P_t = \underbrace{P_{start} + (P_{end}-P_{start})\frac{t-t_0}{T-t_0}}_{\text{線性漂移}} + \underbrace{\mathcal{N}\left(0, \sigma^2 \frac{(t-t_0)(T-t)}{T-t_0}\right)}_{\text{隨機擾動}}$$

**關鍵參數：**
- **波動率 $\sigma$**：必須使用缺口前後最近 20 個數據點的滾動標準差估計，**不可**使用全局波動率，以適應市場的異方差性 (Heteroscedasticity)。

---

## 處理策略指南

1. **識別缺口**：找出數據中的連續 NaN 區間。
2. **局部波動率估計**：計算缺口前後數據的局部波動率 $\sigma_{local}$。
3. **路徑生成**：應用布朗橋公式填充缺口。
4. **可重現性**：必須允許傳入 `random_state` 種子，確保回測結果的一致性。

---

## Python 實作範本

```python
import numpy as np

def brownian_bridge(start_val, end_val, n_steps, sigma, random_state=None):
    """
    生成布朗橋路徑以填充數據缺口。
    
    Args:
        start_val (float): 缺口前的最後一個已知值
        end_val (float): 缺口後的第一個已知值
        n_steps (int): 需要填充的缺失點數量
        sigma (float): 局部波動率 (標準差)
        random_state (int, optional): 隨機數種子
        
    Returns:
        np.array: 插值後的序列片段 (不含端點)
    """
    if random_state is not None:
        np.random.seed(random_state)
        
    dt = 1.0 / (n_steps + 1)
    t = np.linspace(dt, 1.0 - dt, n_steps)
    
    # 線性部分 (Drift)
    drift = start_val + (end_val - start_val) * t
    
    # 隨機部分 (橋的方差結構)
    # Variance = t * (1 - t)
    bridge_var = t * (1 - t)
    noise = np.random.normal(0, sigma * np.sqrt(bridge_var), size=n_steps)
    
    return drift + noise
```

## 驗證產出要求

- **插補對比圖**：繪製原始數據（含缺口）、線性插值結果與布朗橋插值結果的對比圖。
- **波動率分佈**：比較插值前後序列的滾動波動率，驗證布朗橋方法是否有效避免了插值區間的波動率歸零現象。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

- `data-gov-outliers` - 異常值檢測 (建議在插值前先處理異常值)
