---
name: quant-data-cleaning-pipeline
description: 金融時間序列數據清洗的標準流程，整合 MAD 檢測與布朗橋插值
---

# 金融數據清洗管道 (Data Cleaning Pipeline)

## 適用場景
當處理金融 OHLCV 數據時，需要同時處理異常值和缺失值，且必須保持時間序列的統計特性。

## 核心原則

> ⚠️ **禁止** 使用 `ffill().bfill()` 或 `interpolate(method='linear')` 處理金融數據。
> 這會人為降低波動率，導致 VaR 低估和風險模型失效。

## 標準流程

```
1. 異常值檢測 (MAD)
   └─→ 計算 Modified Z-Score = 0.6745 * |X - median| / MAD
   └─→ 閾值 > 3.5 標記為異常

2. 異常值處理
   └─→ 標記為 NaN（而非直接刪除或替換）

3. 缺失值填補 (Brownian Bridge)
   └─→ 計算局部波動率 σ（前 20 期標準差）
   └─→ P(t) = Drift + N(0, σ² * t(1-t))
   └─→ 必須支持 random_state 確保可重現性
```

## Python 範本

```python
from cleaning import detect_outliers_mad, fill_missing_values

def clean_financial_data(df):
    # Step 1: 在收益率上檢測異常（非價格水平）
    returns = df['Close'].pct_change().fillna(0)
    outlier_mask = detect_outliers_mad(returns.values, threshold=3.5)
    
    # Step 2: 標記為 NaN
    df.loc[outlier_mask, ['Open', 'High', 'Low', 'Close']] = np.nan
    
    # Step 3: 布朗橋填補
    df = fill_missing_values(df, method='brownian')
    
    return df
```

## 進化來源
- **Phase 0**: 發現 `DataLoader` 使用 `ffill/bfill` 掩蓋數據缺口
- **Phase 1**: 實作 MAD 替代固定閾值
- **Auditor 審計**: 確認此流程有效保持局部波動率結構
