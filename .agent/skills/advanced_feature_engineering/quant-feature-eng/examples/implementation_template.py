import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

def get_weights_ffd(d, thres, size):
    """
    生成分數階差分的權重係數 (Fixed Window)
    """
    w = [1.]
    for k in range(1, size):
        w_ = -w[-1] / k * (d - k + 1)
        if abs(w_) < thres: break
        w.append(w_)
    return np.array(w[::-1]).reshape(-1, 1)

def frac_diff_ffd(series, d, thres=1e-5):
    """
    執行分數階差分
    
    Args:
        series (pd.Series): 價格序列
        d (float): 差分階數
        thres (float): 權重截斷閾值
    """
    # 1. 處理缺失值
    series = series.ffill().dropna()
    x = series.values.reshape(-1, 1)
    
    # 2. 獲取權重
    w = get_weights_ffd(d, thres, len(x))
    width = len(w) - 1
    
    # 3. 應用卷積 (差分)
    output = []
    for i in range(width, len(x)):
        # Dot product of weights and recent history
        val = np.dot(w.T, x[i-width:i+1])
        output.append(val[0][0])
        
    return pd.Series(output, index=series.index[width:])

def find_min_d(series):
    """
    尋找使序列平穩的最小 d 值
    """
    out_d = 0.0
    for d in np.linspace(0, 1, 11):
        try:
            res = frac_diff_ffd(series, d)
            if len(res) == 0: continue
            # maxlag=1, regression='c', autolag=None for speed/stability
            p_val = adfuller(res, maxlag=1, regression='c', autolag=None)[1]
            if p_val < 0.05:
                out_d = d
                break
        except Exception:
            continue
    return out_d

def rolling_z_score(series, window=60):
    """
    無前視偏差的滾動標準化
    """
    roll = series.rolling(window=window)
    # Shift 1 to strictly avoid look-ahead
    mean = roll.mean().shift(1)
    std = roll.std().shift(1)
    
    z_score = (series - mean) / std
    
    # 壓縮極端值
    z_score_clipped = z_score.clip(-4, 4)
    return z_score_clipped
