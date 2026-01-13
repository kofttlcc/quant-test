# 系統迭代優化計畫 (System Iteration Plan)

## 審計摘要
由 @dataeng, @quant, @mle 聯合執行的代碼審計已完成。我們發現現有系統在數據處理嚴謹性、金融模型深度和機器學習驗證方法上存在顯著差距。本計畫旨在引入已適配的 Antigravity 技能 (`skills/`) 來解決這些問題。

## 發現的問題 (Findings)

### 1. 數據治理 (@dataeng)
- **問題 A (嚴重)**: `src/data_loader/cleaning.py` 使用 `interpolate(method='linear')` 修復壞帳。這會人為降低波動率，導致下游風險模型失效。
    - *解決方案*: 替換為 `data-gov-interp` (布朗橋插值)。
- **問題 B (中等)**: 異常值檢測依賴簡單的 `threshold_pct` (20%)，無法適應不同波動率的市場環境。
    - *解決方案*: 替換為 `data-gov-outliers` (MAD 魯棒檢測)。

### 2. 傳統金融 (@quant)
- **問題 C (中等)**: `backtest_engine.py` 缺乏高階風險度量 (VaR, CVaR)，僅依賴 Sharpe/Drawdown，無法滿足機構級風控要求。
    - *解決方案*: 集成 `trad-fi-risk` 技能。
- **問題 D (缺失)**: 系統目前缺乏衍生品定價引擎與 Beta 分析模組。
    - *解決方案*: 新增 `trad-fi-pricing` (Black-Scholes) 與 `trad-fi-capm` 模組。

### 3. 機器學習 (@mle)
- **問題 E (嚴重)**: ML 模型 (`lstm_predictor.py`, `tree_predictor.py`) 訓練時缺乏嚴謹的交叉驗證 (僅做簡單切分)，存在過擬合風險。
    - *解決方案*: 引入 `quant-ml-validation` (Purged CV)。
- **問題 F (優化)**: MLP 模型未利用 Entity Embeddings 處理潛在的類別特徵 (如 Sector, DayOfWeek)。
    - *解決方案*: 根據 `quant-ml-mlp` 重構模型架構。

---

## 迭代路線圖 (Roadmap)

### 第零階段：緊急漏洞修復 (Emergency Fixes)
> **負責人**: 全員
> **目標**: 修復深層審計中發現的危急代碼漏洞。

#### [MODIFY] [src/data_loader/data_loader.py](file:///Users/jerrylee/coding/src/data_loader/data_loader.py)
- [ ] **[CRITICAL]** 移除 `ffill().bfill()` 暴力填充，接入 `data-gov-interp` 處理缺失值。
- [ ] 增加並發鎖機制。

#### [MODIFY] [src/models/arena/adversarial_arena.py](file:///Users/jerrylee/coding/src/models/arena/adversarial_arena.py)
- [ ] **[CRITICAL]** 統一訓練/驗證集切分邏輯，消除數據洩露。
- [ ] 嚴格對齊 Signal 與 Return 計算 ROI。

#### [MODIFY] [src/models/strategy_logic.py](file:///Users/jerrylee/coding/src/models/strategy_logic.py)
- [ ] 移除 `Position` 的 `ffill`，正確處理非交易日狀態。

### 第一階段：數據底層重構 (Data Foundation)
> **負責人**: @dataeng
> **目標**: 確保所有進入模型的數據均經過魯棒清洗與正確插值。

#### [MODIFY] [src/data_loader/cleaning.py](file:///Users/jerrylee/coding/src/data_loader/cleaning.py)
- [x] 移除 `handle_outliers` 中的線性插值邏輯。
- [x] 實作 `data-gov-outliers` (MAD) 替換固定閾值過濾。
- [x] 實作 `data-gov-interp` (Brownian Bridge) 用於填補 `NaN`。

### 第二階段：核心金融引擎 (Financial Core)
> **負責人**: @quant
> **目標**: 補齊基礎金融分析能力。

#### [NEW] [src/models/pricing.py](file:///Users/jerrylee/coding/src/models/pricing.py)
- [x] 實作 `trad-fi-pricing` (Black-Scholes & Greeks)。

#### [NEW] [src/models/alpha_beta.py](file:///Users/jerrylee/coding/src/models/alpha_beta.py)
- [x] 實作 `trad-fi-capm` 用於計算資產相對於 Benchmark 的 Beta/Alpha。

#### [MODIFY] [src/backend/backtest_engine.py](file:///Users/jerrylee/coding/src/backend/backtest_engine.py)
- [x] 在 `run_backtest` 的 Metrics 計算中集成 `trad-fi-risk` (VaR, CVaR, Sortino)。

### 第三階段：AI 模型升級 (AI Upgrade)
> **負責人**: @mle
> **目標**: 提升模型的預測能力與泛化穩健性。

#### [NEW] [src/models/validation.py](file:///Users/jerrylee/coding/src/models/validation.py)
- [ ] 實作 `quant-ml-validation` (Combinatorial Purged CV) 類。

#### [MODIFY] [src/models/arena/lstm_predictor.py](file:///Users/jerrylee/coding/src/models/arena/lstm_predictor.py)
- [ ] 重構 `MLPTrendModel`，引入 `quant-ml-mlp` 的 Embedding 層架構。
- [ ] 在 `train` 方法中接入 `validation.py` 的 CV 流程。

## 驗證計畫
1. **單元測試**: 為每個新模組編寫 `tests/`。
2. **對比測試**: 比較新舊清洗邏輯對 Backtest 結果的影響（預期新邏輯的波動率會略高，Sharpe 略低，但更真實）。
