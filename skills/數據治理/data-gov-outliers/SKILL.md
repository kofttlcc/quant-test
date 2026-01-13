name: robust-outlier-detection 
description: 基於中位數絕對偏差 (MAD) 的魯棒異常值檢測技能。專為非正態、尖峰厚尾的金融數據設計，嚴禁用於正態分佈假設場景。

魯棒異常值檢測技能指令
你是一名數據清洗專家。金融數據通常具有厚尾特徵（Fat Tails），嚴禁使用標準差（Z-score） 進行異常值判定，因為極端值會污染均值和方差。
你必須使用基於中位數的 Hampel Filter 或 MAD (Median Absolute Deviation) 方法。

1. 數學原理
計算修正後的 Z 分數（Modified Z-score, $M_i$）：
1.計算中位數：$\tilde{X} = \text{median}(X)$
2.計算 MAD：$\text{MAD} = \text{median}(|X_i - \tilde{X}|)$
3.計算 $M_i$（$0.6745$ 為正態一致性常數）：
$$M_i = \frac{0.6745 \times (X_i - \tilde{X})}{\text{MAD}}$$
判定閾值： 當 $|M_i| > 3.5$ 時，標記為異常值。

2. 處理策略指南
檢測到異常後，根據下游任務選擇策略：
機器學習/神經網絡： 使用 蓋帽法 (Winsorization)，將異常值替換為 $3.5 \sigma$ 對應的邊界值。
樹模型 (XGBoost/LightGBM)： 僅增加一個 is_outlier 布林特徵，保留原始值。
信號處理/傳統統計： 將異常值視為 NaN，並呼叫 brownian-bridge-interpolation 技能進行修復。

3. Python 實作範本
python import numpy as npimport pandas as pddef detect_outliers_mad(data, threshold=3.5):"""使用 MAD 方法檢測異常值。
data: numpy array 或 pandas series"""if isinstance(data, pd.Series):data = data.values
median = np.median(data)
diff = np.abs(data - median)
mad = np.median(diff)

if mad == 0:
    # 如果 MAD 為 0（例如大部分數據相同），則退化處理
    return np.zeros(len(data), dtype=bool)

modified_z_score = 0.6745 * diff / mad

return modified_z_score > threshold
def winsorize_series(data, threshold=3.5):"""執行蓋帽處理"""median = np.median(data)diff = np.abs(data - median)mad = np.median(diff)limit = (threshold * mad) / 0.6745
return np.clip(data, median - limit, median + limit)

## 4. 驗證產出
- 產出異常值分佈圖（Scatter Plot），用紅色標記被識別出的異常點，並在圖中標註使用的 MAD 閾值。