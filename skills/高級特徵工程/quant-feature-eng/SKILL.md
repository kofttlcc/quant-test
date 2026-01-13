name: advanced-feature-engineering 
description: 生成適用於金融機器學習的高質量特徵。包含分數階差分 (Fractional Differentiation) 與無前視偏差的滾動標準化。

高級特徵工程技能指令
你是一名 AI 數據科學家。金融數據具有非平穩性，直接輸入 ML 模型會導致失效。你的任務是使用高級變換技術保留數據的記憶（Memory）同時實現平穩性。

1. 分數階差分 (Fractional Differentiation)
標準的一階差分（Returns）會使數據平穩，但會抹去所有的價格歷史記憶。分數階差分（例如 0.4 階）可以在達成平穩性的同時，保留最多的相關性。
算法： 迭代尋找最小的 $d$ 值（0 < d < 1），使得序列通過 ADF 檢驗 (p < 0.05)。

2. 滾動窗口標準化 (Rolling Window Normalization)
嚴禁使用全局 Z-Score ((x - mean) / std)，這會引入未來數據（Look-ahead Bias）。
正確做法： 對於時刻 $t$，僅使用 $t-W$ 到 $t-1$ 的數據計算均值和標準差。
變換： 使用雙曲正切 (Tanh) 或百分位 (Percentile) 將極端值壓縮到固定區間，防止神經網絡梯度爆炸。

3. Python 實作範本
python import numpy as npimport pandas as pdfrom statsmodels.tsa.stattools import adfuller
def get_weights_ffd(d, thres, size):"""生成分數階差分的權重係數 (Fixed Window)"""w = [1.]for k in range(1, size):w_ = -w[-1] / k * (d - k + 1)if abs(w_) < thres: breakw.append(w_)return np.array(w[::-1]).reshape(-1, 1)
def frac_diff_ffd(series, d, thres=1e-5):"""執行分數階差分""" # 1. 處理缺失值series = series.fillna(method='ffill').dropna()x = series.values.reshape(-1, 1)

# 2. 獲取權重
w = get_weights_ffd(d, thres, len(x))
width = len(w) - 1

# 3. 應用卷積 (差分)
output =
for i in range(width, len(x)):
    # Dot product of weights and recent history
    val = np.dot(w.T, x[i-width:i+1])
    output.append(val)
    
return pd.Series(output, index=series.index[width:])

def find_min_d(series):"""尋找使序列平穩的最小 d 值"""out_d = 0.0for d in np.linspace(0, 1, 11):res = frac_diff_ffd(series, d)if len(res) == 0: continuep_val = adfuller(res, maxlag=1, regression='c', autolag=None)1if p_val < 0.05:out_d = dbreakreturn out_d
def rolling_z_score(series, window=60):"""無前視偏差的滾動標準化"""roll = series.rolling(window=window)mean = roll.mean().shift(1)  # Shift 1 to strictly avoid look-aheadstd = roll.std().shift(1)

z_score = (series - mean) / std

# 壓縮極端值 (Optional)
z_score_clipped = z_score.clip(-4, 4)
return z_score_clipped

## 4. 驗證產出
- 輸出 **「d 值優化曲線」**：展示不同 $d$ 值下的 ADF p-value 和與原始序列的相關性（Correlation）。目標是找到 p-value < 0.05 且相關性最大的點。