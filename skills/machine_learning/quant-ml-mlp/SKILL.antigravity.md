---
name: quant-ml-mlp
description: 構建專用於金融時間序列預測的 MLP 模型，包含實體嵌入 (Entity Embeddings) 與特徵歸一化層。
trigger: when_needed
language: zh-TW
adapted_from: skills/機器學習/quant-ml-mlp/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# MLP-TIMESERIES-FORECASTING 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-ml-mlp
> **語言**: 繁體中文

## 概述

構建專用於金融時間序列預測的 MLP 架構。為了處理金融數據的高雜訊與異質性，此模型特別集成實體嵌入 (Entity Embeddings) 於類別特徵，並強制執行特徵標準化。

---

## 使用情境

此技能適用於以下情況：
- 需要融合基本面數據（類別型）與價量數據（連續型）進行預測時
- 傳統線性模型無法捕捉非線性市場特徵時
- 需要處理 DayOfWeek, Sector, Exchange 等類別特徵時

---

## 架構設計原則

### 1. 輸入層處理
- **連續特徵 (Continuous)**: 直接輸入，但在送入模型前**必須**進行標準化 (Z-score) 或 歸一化 (MinMax)。
    - *注意*：`Scaler` 的參數只能由訓練集擬合，嚴禁使用測試集數據。
- **類別特徵 (Categorical)**: 嚴禁使用 One-Hot Encoding，因為會導致稀疏性問題。**必須**使用 Embedding 層將其映射為低維稠密向量。

### 2. 網絡結構
- **Dropout**: 在每個 Dense 層後添加 Dropout (0.2-0.5)，以防止過擬合（金融數據信噪比低）。
- **激活函數**: 使用 ReLU 或 Leaky ReLU。
- **輸出層**:
    - 回歸任務：Linear (1 unit).
    - 二分類任務（漲/跌）：Sigmoid (1 unit).

---

## Python 實作範本

```python
from tensorflow.keras.layers import Input, Dense, Embedding, Concatenate, Dropout, Flatten
from tensorflow.keras.models import Model

def build_mlp(n_continuous, cat_info):
    """
    構建混合輸入 MLP 模型。
    
    Args:
        n_continuous (int): 連續特徵的數量
        cat_info (list): 類別特徵資訊列表，每個元素為 tuple (n_categories, embed_dim)
                         例如: [(7, 3)] 代表星期幾有 7 類，嵌入維度為 3
    Returns:
        keras.Model: 編譯前的模型物件
    """
    
    # 1. 連續變量輸入路徑
    input_cont = Input(shape=(n_continuous,), name='continuous_input')
    inputs = [input_cont]
    embeddings = []
    
    # 2. 類別變量輸入路徑 (Entity Embeddings)
    for i, (n_cat, dim) in enumerate(cat_info):
        inp = Input(shape=(1,), name=f'cat_input_{i}')
        emb = Embedding(input_dim=n_cat, output_dim=dim)(inp)
        emb = Flatten()(emb)
        
        inputs.append(inp)
        embeddings.append(emb)
    
    # 3. 特徵拼接
    # 將連續特徵與所有嵌入向量拼接
    if embeddings:
        merged_layer = Concatenate()([input_cont] + embeddings)
    else:
        merged_layer = input_cont
        
    # 4. 全連接層
    x = Dense(64, activation='relu')(merged_layer)
    x = Dropout(0.3)(x)
    x = Dense(32, activation='relu')(x)
    x = Dropout(0.2)(x)
    
    # 5. 輸出層 (假設為回歸任務)
    output = Dense(1, activation='linear', name='output')(x)
    
    model = Model(inputs=inputs, outputs=output)
    return model
```

## 驗證產出要求

- **模型架構圖**：使用 `plot_model` 輸出模型結構圖，確認 Embedding 層與 Concatenate 層連接正確。
- **損失曲線**：繪製 Training Loss 與 Validation Loss 曲線，檢查是否過擬合（Gap 是否過大）。
- **特徵重要性**：若可行，使用 Permutation Importance 分析連續特徵與類別特徵的貢獻度。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

- `quant-ml-validation` - 必須使用 Purged CV 進行驗證，避免過擬合。
