---
name: trad-fi-capm
description: 執行 CAPM 回歸分析，分解資產收益為 Alpha (超額) 和 Beta (系統性)，並進行顯著性檢驗。
trigger: when_needed
language: zh-TW
adapted_from: skills/傳統金融/trad-fi-capm/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# CAPM-BETA-ANALYSIS 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/trad-fi-capm
> **語言**: 繁體中文

## 概述

資本資產定價模型 (CAPM) 分析技能，旨在通過 OLS 回歸量化單一資產或投資組合相對於基準市場的風險暴露 (Beta) 及超額收益能力 (Alpha)。

---

## 使用情境

此技能適用於以下情況：
- 評估基金經理的選股能力 (尋找顯著的正 Alpha)
- 計算投資組合的系統性風險暴露 (Beta)
- 進行多因子模型分析的基礎步驟

---

## 數學原理

模型定義如下：

$$R_i - R_f = \alpha_i + \beta_i(R_m - R_f) + \epsilon_i$$

其中：
- $R_i$: 資產收益率
- $R_m$: 市場基準收益率 (如 SPY, TAIEX)
- $R_f$: 無風險利率
- $\beta_i$: 系統性風險係數 (斜率)
- $\alpha_i$: 詹森指數 (截距)，代表超額收益能力

---

## 執行邏輯

1. **數據對齊**：確保資產與 Benchmark 的時間索引完全對齊，刪除任何一方缺失的日期 (Inner Join)。
2. **無風險利率處理**：將年化無風險利率轉換為與數據頻率一致（如日頻）。
3. **回歸分析**：使用 OLS (普通最小二乘法) 進行擬合。
4. **假設檢驗**：檢查 Alpha 的 t-statistic。僅當 p-value < 0.05 時，我們才有 95% 的信心拒絕原假設 ($\alpha=0$)，即認為該策略具有統計顯著的超額收益。

---

## Python 實作範本

```python
import statsmodels.api as sm
import pandas as pd

def calculate_capm(asset_ret, market_ret, rf=0.0):
    """
    計算 CAPM Beta 與 Alpha。
    
    Args:
        asset_ret (pd.Series): 資產收益率序列
        market_ret (pd.Series): 市場收益率序列
        rf (float or pd.Series): 無風險利率 (日頻)
        
    Returns:
        dict: 包含 alpha, beta, p_values, r_squared 的字典
    """
    # 1. 數據對齊
    df = pd.concat([asset_ret, market_ret], axis=1).dropna()
    df.columns = ['asset', 'market']
    
    # 2. 計算超額收益
    if isinstance(rf, pd.Series):
        rf = rf.reindex(df.index).ffill()
    
    y = df['asset'] - rf
    x = df['market'] - rf
    
    # 3. 添加常數項 (Alpha)
    X = sm.add_constant(x)
    
    # 4. 擬合模型
    model = sm.OLS(y, X).fit()
    
    return {
        'alpha': model.params['const'],
        'beta': model.params.iloc[1],
        'alpha_pvalue': model.pvalues['const'],
        'beta_pvalue': model.pvalues.iloc[1],
        'r_squared': model.rsquared,
        'summary': model.summary()
    }
```

## 驗證產出要求

- **回歸散點圖**：繪製 X 軸為市場超額收益，Y 軸為資產超額收益的散點圖，並疊加回歸直線。
- **統計報告**：必須輸出包含 t-stats 和 p-values 的完整回歸摘要表。

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
