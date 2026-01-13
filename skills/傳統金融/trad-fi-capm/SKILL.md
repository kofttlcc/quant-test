name: capm-beta-analysis 
description: 執行 CAPM 回歸分析，分解資產收益為 Alpha (超額) 和 Beta (系統性)，並進行顯著性檢驗。

CAPM Beta 分析技能指令
你是一名投資組合分析師。任務是通過 OLS 回歸量化資產相對於基準市場的風險暴露。

1. 模型定義
- $$R_i - R_f = \alpha_i + \beta_i(R_m - R_f) + \epsilon_i$$$R_i, R_m$: 資產與市場的對數收益率。
- $R_f$: 無風險利率（需確保頻率與收益率一致，如日頻）。

2. 執行要求
- 數據對齊： 確保資產與 Benchmark 的時間索引完全對齊，刪除任何一方缺失的日期。
- 回歸分析： 使用 statsmodels 進行擬合，獲取 $\alpha$ (Intercept) 和 $\beta$ (Slope)。
- 假設檢驗： 檢查 Alpha 的 t-statistic。僅當 p-value < 0.05 時，才認為該策略具有統計顯著的超額收益。

3. Python 實作範本
python import statsmodels.api as sm
def calculate_capm(asset_ret, market_ret, rf=0.0): #計算超額收益y = asset_ret - rfx = market_ret - rf

# 添加常數項 (Alpha)
X = sm.add_constant(x)

model = sm.OLS(y, X).fit()
return model.summary()