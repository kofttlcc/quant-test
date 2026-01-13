---
name: advanced-portfolio-optimization
description: 執行機構級投資組合配置，包含 Hierarchical Risk Parity (HRP) 與 Black-Litterman 模型。
trigger: when_needed
language: zh-TW
adapted_from: skills/高級投資組合優化/quant-portfolio-opt/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# ADVANCED-PORTFOLIO-OPTIMIZATION 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-portfolio-opt
> **語言**: 繁體中文

## 概述

構建穩健 (Robust) 的投資組合，解決傳統均值-方差優化 (MVO) 的誤差最大化問題。此技能包含 Hierarchical Risk Parity (HRP) 機器學習資產配置法與 Black-Litterman 貝葉斯觀點融合模型。

---

## 使用情境

此技能適用於以下情況：
- **HRP**: 資產數量眾多、相關性高且協方差矩陣可能不可逆，或者預期收益極難預測時。
- **Black-Litterman**: 投資者擁有明確的主觀觀點 (Alpha Signal)，並希望將其與市場均衡觀點有機結合時。

---

## 數學原理

### 1. Hierarchical Risk Parity (HRP)
利用圖論與聚類算法解決相關性結構問題，不依賴協方差矩陣的逆矩陣。
- **樹狀聚類 (Tree Clustering)**：將相關係數轉化為距離度量 $d_{i,j} = \sqrt{2(1-\rho_{i,j})}$，進行層次聚類。
- **遞歸二分 (Recursive Bisection)**：自上而下將資產池切分，根據子簇的逆方差分配權重：
  $$\alpha_1 = 1 - \frac{V_1}{V_1 + V_2}$$

### 2. Black-Litterman 模型 (BL)
$$E[R] = [(\tau \Sigma)^{-1} + P^T \Omega^{-1} P]^{-1} [(\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q]$$
- $\Pi$: 市場隱含均衡收益 (Market Implied Returns)。
- $Q$: 投資者對資產收益的主觀觀點向量 (Views)。
- $\Omega$: 觀點的不確定性矩陣 (Confidence)。

---

## 處理策略指南

1.  **HRP 實作**：
    - 必須首先進行矩陣擬對角化 (Quasi-Diagonalization)，將相關性高的資產物理上排列在一起，這也是 HRP 的核心創新點。
2.  **BL 實作**：
    - 觀點信心矩陣 $\Omega$ 的設定是關鍵。建議使用 Idzorek 方法，將 0-1 的直觀信心分數映射為方差。
    - 得到的後驗收益 (Posterior Returns) 應作為輸入代入 MVO 優化器求解最終權重。

---

## Python 實作範本

```python
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform

def optimize_hrp(returns):
    """
    執行 HRP 優化
    """
    corr = returns.corr()
    cov = returns.cov()
    
    # 1. 距離矩陣
    d_corr = np.sqrt(2 * (1 - corr))
    dist_array = squareform(d_corr)
    # 2. 聚類
    link = linkage(dist_array, method='ward')
    
    # 3. 擬對角化 (Quasi-Diagonalization)
    # (此處省略複雜的 Seriation 代碼，實作時需確保矩陣重排)
    # sort_ix = get_quasi_diag(...)
    
    # 4. 遞歸二分分配權重
    # ...
    # return weights

def optimize_black_litterman(cov_matrix, market_caps, views, confidences, risk_aversion=2.5):
    """
    執行 Black-Litterman 優化
    
    Args:
        cov_matrix: 資產協方差矩陣
        market_caps: 資產市值 (用於計算市場均衡權重)
        views: 觀點字典 {Asset: Expected_Return}
        confidences: 信心字典 {Asset: 0.0-1.0}
    """
    # 1. 市場隱含收益 (Prior)
    market_weights = market_caps / market_caps.sum()
    pi = risk_aversion * cov_matrix.dot(market_weights)
    
    # 2. 構建 P (Asset Mapping), Q (Views), Omega (Uncertainty)
    assets = cov_matrix.columns
    k = len(views)
    n = len(assets)
    P = np.zeros((k, n))
    Q = np.zeros(k)
    Omega = np.zeros((k, k))
    
    for i, (asset, view_ret) in enumerate(views.items()):
        idx = assets.get_loc(asset)
        P[i, idx] = 1
        Q[i] = view_ret
        # 簡易映射: 信心越高，方差(Omega)越小
        Omega[i, i] = (1 - confidences[asset]) * cov_matrix.iloc[idx, idx]
        
    # 3. 後驗計算 (Posterior)
    tau = 0.05
    tau_cov_inv = np.linalg.inv(tau * cov_matrix)
    omega_inv = np.linalg.inv(Omega)
    
    # BL Master Formula for Expected Returns
    left_term = np.linalg.inv(tau_cov_inv + P.T.dot(omega_inv).dot(P))
    right_term = tau_cov_inv.dot(pi) + P.T.dot(omega_inv).dot(Q)
    posterior_rets = left_term.dot(right_term)
    
    # 4. 最終權重 (Unconstrained MVO based on Posterior)
    opt_weights = np.linalg.inv(cov_matrix).dot(posterior_rets) / risk_aversion
    return pd.Series(opt_weights, index=assets)
```

## 驗證產出要求

- **HRP**: 生成 **「聚類樹狀圖 (Dendrogram)」** 與重排前後的 **「相關性熱力圖」** 對比，證明算法成功將相關資產分組。
- **BL**: 生成 **「觀點影響分析表」**，直觀展示 Prior Weights (純市場觀點) vs Posterior Weights (融合觀點後) 的差異。

---

## 專案整合

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
