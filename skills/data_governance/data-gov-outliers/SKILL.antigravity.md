---
name: data-gov-outliers
description: 基於中位數絕對偏差 (MAD) 的魯棒異常值檢測技能。專為非正態、尖峰厚尾的金融數據設計。
trigger: when_needed
language: zh-TW
adapted_from: skills/data-gov-outliers/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# ROBUST-OUTLIER-DETECTION 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/data-gov-outliers
> **語言**: 繁體中文

## 概述

基於中位數絕對偏差 (MAD) 的魯棒異常值檢測技能。專為非正態、尖峰厚尾（Fat Tails）的金融數據設計。**嚴禁**在這些場景使用標準差（Z-score）進行異常值判定，因為極端值會污染均值和方差。

---

## 使用情境

此技能適用於以下情況：
- 必須處理金融時間序列數據清洗時
- 數據具有厚尾特徵或懷疑有異常值污染時
- 需要執行魯棒統計分析前

---

## 數學原理

計算修正後的 Z 分數（Modified Z-score, $M_i$）：

1. **計算中位數**：
   $$\tilde{X} = \text{median}(X)$$

2. **計算 MAD (Median Absolute Deviation)**：
   $$\text{MAD} = \text{median}(|X_i - \tilde{X}|)$$

3. **計算 $M_i$**：
   （$0.6745$ 為正態一致性常數，用於將 MAD 轉換為與標準差 σ 等價的尺度）
   $$M_i = \frac{0.6745 \times (X_i - \tilde{X})}{\text{MAD}}$$

### 判定閾值
當 $|M_i| > 3.5$ 時，標記為異常值。

---

## 處理策略指南

檢測到異常後，根據下游任務選擇策略：

| 下游任務 | 策略 | 說明 |
| :--- | :--- | :--- |
| **機器學習 / 神經網絡** | **蓋帽法 (Winsorization)** | 將異常值替換為 $3.5\sigma$ 對應的邊界值。 |
| **樹模型 (XGBoost / LightGBM)** | **特徵標記** | 僅增加一個 `is_outlier` 布林特徵，保留原始值。 |
| **信號處理 / 傳統統計** | **補值 (Imputation)** | 將異常值視為 NaN，並呼叫 `brownian-bridge-interpolation` 技能進行修復。 |

---

## Python 實作範本

```python
import numpy as np
import pandas as pd

def detect_outliers_mad(data, threshold=3.5):
    """
    使用 MAD 方法檢測異常值。
    data: numpy array 或 pandas series
    """
    if isinstance(data, pd.Series):
        data = data.values
        
    median = np.median(data)
    diff = np.abs(data - median)
    mad = np.median(diff)

    if mad == 0:
        # 如果 MAD 為 0（例如大部分數據相同），則退化處理
        return np.zeros(len(data), dtype=bool)

    modified_z_score = 0.6745 * diff / mad

    return modified_z_score > threshold

def winsorize_series(data, threshold=3.5):
    """
    執行蓋帽處理 (Winsorization)
    """
    if isinstance(data, pd.Series):
        values = data.values
    else:
        values = data
        
    median = np.median(values)
    diff = np.abs(values - median)
    mad = np.median(diff)
    
    limit = (threshold * mad) / 0.6745
    
    return np.clip(values, median - limit, median + limit)
```

## 驗證產出要求

- 產出異常值分佈圖（Scatter Plot），用紅色標記被識別出的異常點。
- 在圖中標註使用的 MAD 閾值。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 與 `skills/_base/architecture.md` 架構模式一致
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

可搭配以下技能使用：
- `data-gov-stationarity` - 平穩性分析 (通常在異常值處理後執行)
- `brownian-bridge-interpolation` - 數據插值修復
