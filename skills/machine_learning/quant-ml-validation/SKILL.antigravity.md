---
name: quant-ml-validation
description: 實施組合清除交叉驗證 (Combinatorial Purged CV)，嚴格防止時間序列回測中的數據洩露與前視偏差。
trigger: when_needed
language: zh-TW
adapted_from: skills/機器學習/quant-ml-validation/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# PURGED-CROSS-VALIDATION 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-ml-validation
> **語言**: 繁體中文

## 概述

在金融序列上進行回測時，標準的 K-Fold 會導致嚴重的數據洩露。本技能實施 Purging (清除) 與 Embargo (禁運) 機制，確保訓練集與測試集在時間軸上的嚴格隔離，從而準確評估模型的真實泛化能力。

---

## 使用情境

此技能適用於以下情況：
- 訓練任何監督式金融預測模型時
- 標籤 (Label) 具有重疊性質（例如：預測未來 5 天收益，這會導致標籤在時間上相關）
- 需要評估模型在不同市場體制 (Regime) 下的穩定性

---

## 核心概念

### 1. Purging (清除)
刪除訓練集中任何標籤依賴於測試集時間區間的樣本。
- *例子*：若 $Y_i$ 依賴於未來 5 天的收益，則測試集開始前的 5 天數據必須從訓練集中剔除，否則模型會「偷看」到測試集的未來訊息。

### 2. Embargo (禁運)
在測試集結束後額外刪除一段數據（如總長度的 1%）。
- *目的*：阻斷序列的長記憶性 (Long Memory) 或相關性，確保測試集後的訓練樣本不受測試集期間的影響。

### 3. Combinatorial CV (組合交叉驗證)
生成多種 訓練/測試 組合路徑，而非單一的 K-Fold。這有助於測試模型在 "Train on Bull, Test on Bear" 等不同情境下的表現。

---

## 驗證邏輯

**禁止**使用 sklearn 的 `KFold` 或 `TimeSeriesSplit` (若是 Walk-Forward 則可用，但 CPCV 更佳)。

**執行步驟**：
1. 定義 $N$ 個分組。
2. 選擇 $k$ 個組作為測試集。
3. 剩餘組作為訓練集。
4. 對於每個訓練樣本，檢查其 `prediction_time` + `forecast_horizon` 是否與測試集的 `start_time` - `end_time` 重疊。若重疊，則做 Purging 剔除。

---

## Python 參考邏輯

```python
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

def get_purged_cv_folds(time_index, n_folds=5, purge_window=0, embargo_window=0):
    """
    生成 Purged K-Fold 索引。
    這是一個簡化示範，完整實作建議使用 skfolio 或 mlfinlab。
    
    Args:
        time_index (pd.Index): 時間索引
        n_folds (int): 折數
        purge_window (int): 清除窗口大小 (bars)
        embargo_window (int): 禁運窗口大小 (bars)
        
    Yields:
        train_indices, test_indices
    """
    indices = np.arange(len(time_index))
    kf = KFold(n_splits=n_folds, shuffle=False)
    
    for train_idx_raw, test_idx in kf.split(indices):
        
        # 1. 識別測試集邊界
        test_start_idx = test_idx[0]
        test_end_idx = test_idx[-1]
        
        # 2. 應用 Purging: 移除測試集前後緊鄰的樣本
        # Train set before Test set
        train_indices_before = train_idx_raw[train_idx_raw < test_start_idx - purge_window]
        
        # Train set after Test set (需考慮 Embargo)
        train_indices_after = train_idx_raw[train_idx_raw > test_end_idx + embargo_window]
        
        train_indices = np.concatenate([train_indices_before, train_indices_after])
        
        yield train_indices, test_idx

# 使用範例
# cv = get_purged_cv_folds(df.index, n_folds=5, purge_window=5)
```

## 驗證產出要求

- **CV 熱力圖**：生成一張熱力圖，X 軸為時間，Y 軸為 Fold 編號。
    - 顏色區分：Train (藍色), Test (橙色), Purged/Embargo (灰色/空白)。
    - 這張圖是證明回測嚴謹性的**必要工件**，必須隨模型報告提交。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

- `quant-ml-mlp` - 與 MLP 模型搭配使用
