name: advanced-portfolio-optimization 
description: 執行機構級投資組合配置，包含 Hierarchical Risk Parity (HRP) 與 Black-Litterman 模型。解決協方差矩陣不穩定問題並融合主觀觀點。

高階投資組合優化技能指令
你是一名資產配置專家。你的任務是構建穩健（Robust）的投資組合，嚴禁直接使用簡單的均值-方差優化（MVO），以避免誤差最大化。你必須根據情況選擇 HRP 或 Black-Litterman 模型。

1. Hierarchical Risk Parity (HRP)
適用於：資產數量眾多、相關性高且預期收益難以預測的場景。HRP 不需要協方差矩陣可逆。
算法邏輯
樹狀聚類 (Tree Clustering):
將相關係數矩陣 $\rho$ 轉換為距離矩陣 $d_{i,j} = \sqrt{2(1-\rho_{i,j})}$。
使用 scipy.cluster.hierarchy.linkage (方法: 'ward') 構建聚類樹。
矩陣擬對角化 (Quasi-Diagonalization):重排協方差矩陣，將相關性高的資產物理上排列在一起。
遞歸二分 (Recursive Bisection):自上而下將資產池一分為二。計算子簇方差 $V_{cluster}$，根據逆方差分配權重：$\alpha_1 = 1 - \frac{V_1}{V_1 + V_2}$。

2. Black-Litterman 模型 (BL)
適用於：你有明確的 Alpha 信號（觀點）並希望將其與市場均衡融合的場景。
核心公式
市場隱含收益 ($\Pi$): $\Pi = \delta \Sigma w_{mkt}$
觀點分佈 ($P, Q, \Omega$): $P \cdot E = Q + \epsilon$
後驗收益 ($E$):$$E =^{-1}$$

3. Python 實作範本
python import numpy as np import pandas as pdfrom scipy.cluster.hierarchy import linkage, to_tree_builderfrom scipy.spatial.distance import squareform
def optimize_hrp(returns):"""執行 HRP 優化returns: DataFrame of asset returns"""corr = returns.corr()cov = returns.cov()

# 1. 距離矩陣
d_corr = np.sqrt(2 * (1 - corr))

# 2. 聚類 (Linkage)
# 注意：squareform 用於將矩陣轉為壓縮向量，linkage 需要此格式
dist_array = squareform(d_corr)
link = linkage(dist_array, method='ward')

# 3. 擬對角化 (Seriation) - 簡化實作：獲取葉節點順序
# 在實際 Agent 中需遍歷 linkage 矩陣建立 sort_ix
def get_quasi_diag(link):
    link = link.astype(int)
    sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
    num_items = link[-1, 3]
    while sort_ix.max() >= num_items:
        sort_ix.index = range(0, sort_ix.shape * 2, 2)
        df0 = sort_ix[sort_ix >= num_items]
        i = df0.index
        j = df0.values - num_items
        sort_ix[i] = link[j, 0]
        df0 = pd.Series(link[j, 1], index=i + 1)
        sort_ix = pd.concat([sort_ix, df0]) # Reassemble
        sort_ix = sort_ix.sort_index()
        sort_ix.index = range(sort_ix.shape)
    return sort_ix.tolist()

sort_ix = get_quasi_diag(link)

# 4. 遞歸二分 (Recursive Bisection)
# 初始化權重為 1
weights = pd.Series(1, index=sort_ix)
#... (此處需實作遞歸切分邏輯，計算簇內方差並分配 alpha)...

return weights
def optimize_black_litterman(cov_matrix, market_caps, views, confidences, risk_aversion=2.5):"""cov_matrix: DataFramemarket_caps: Series (市值)views: Dict {Asset: Return} (絕對觀點)confidences: Dict {Asset: 0.0-1.0}"""# 1. 市場隱含收益market_weights = market_caps / market_caps.sum()pi = risk_aversion * cov_matrix.dot(market_weights)# 2. 構建 P, Q, Omega
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
    # 使用 Idzorek 方法簡化 Omega 估計 (基於信心)
    # 實際應用中需更嚴謹的映射
    Omega[i, i] = (1 - confidences[asset]) * cov_matrix.iloc[idx, idx]
    
# 3. 後驗計算
tau = 0.05
tau_cov_inv = np.linalg.inv(tau * cov_matrix)
omega_inv = np.linalg.inv(Omega)

left_term = np.linalg.inv(tau_cov_inv + P.T.dot(omega_inv).dot(P))
right_term = tau_cov_inv.dot(pi) + P.T.dot(omega_inv).dot(Q)

posterior_rets = left_term.dot(right_term)

# 簡單 MVO 求解權重 (無約束)
# w = (1/delta) * Sigma^-1 * E
opt_weights = np.linalg.inv(cov_matrix).dot(posterior_rets) / risk_aversion
return pd.Series(opt_weights, index=assets)

## 4. 驗證工件
- **HRP:** 生成 **「聚類樹狀圖 (Dendrogram)」** 與重排前後的 **「相關性熱力圖」** 對比。
- **BL:** 生成 **「觀點影響分析表」**，展示 Prior Weights (市場) vs Posterior Weights (最終) 的差異。