# 💀 深層系統屍檢報告 (Deep System Autopsy Report)

## 概要
本報告針對系統核心模組進行了無死角代碼審計，暴露了隱藏的架構缺陷、算法漏洞與數據風險。

---

## 1. 數據架構與治理 (@dataeng)
> **狀態**: 危急 (Critical)
> **關鍵詞**: 併發競爭、髒數據掩蓋、緩存風險

### 1.1 數據加載器 (`src/data_loader/data_loader.py`)
- **[CRITICAL] 數據掩蓋**: 使用 `df.ffill().bfill()` 無差別填充所有缺失值。這會將停牌、數據丟失等異常狀態掩蓋成正常交易數據，導致回測產生「可交易」的幻覺。
- **[RISK] 內存洩露**: `_evict_expired_cache` 僅在調用 `fetch_data` 時觸發。若服務長期運行且空閒，過期對象將永久佔用內存。
- **[RISK] 併發競爭**: `self.cache` 為非並發安全 Dict。若 API 層並發請求同一 Ticker，可能導致寫入衝突。

### 1.2 緩存管理器 (`src/data_loader/cache_manager.py`)
- **[CRITICAL] 文件鎖缺失**: 多進程環境下（如 AI 訓練任務後台並行），同時寫入同一個 `.parquet` 文件會導致文件損壞 (Corruption)。
- **[HIGH] 序列化效率**: 每次 save 都做 `to_datetime` 和 index set，對於高頻讀寫是極大的性能開銷。

---

## 2. 金融核心引擎 (@quant)
> **狀態**: 高風險 (High Risk)
> **關鍵詞**: 靜態假設、邏輯漏洞、組合失效

### 2.1 估值模型 (`src/models/valuation.py`)
- **[HIGH] WACC 恆定假設**: DCF 模型假設未來 5 年 WACC 保持不變且等於當前 WACC。在加息/降息週期中，這會導致估值嚴重失真 (1% WACC變動可導致估值波動 15-20%)。
- **[HIGH] 硬編碼增長率**: `est_growth` 在缺少分析師數據時回退到 `sector` 基準，或 `0.05`。這忽略了個股特異性 (Idiosyncratic Risk)。
- **[MEDIUM] 算術錯誤風險**: `spread = wacc - terminal_growth` 未充分考慮負值情況，僅做簡單 clamp，可能導致負估值被強行轉正。

### 2.2 投資組合管理 (`src/backend/portfolio.py`)
- **[HIGH] 信號加權失效**: `combined_position += pos * weight`。不同策略的 Position 規模未歸一化。若策略 A 輸出 [0, 1]，策略 B 輸出 [-100, 100]，權重 50/50 將導致 B 完全主導 A。
- **[MEDIUM] 狀態管理**: Portfolio 不管理資金 (Cash)，只管理信號。無法實現基於凱利公式 (Kelly Criterion) 或波動率的動態倉位管理。

### 2.3 策略邏輯 (`src/models/strategy_logic.py`)
- **[CRITICAL] 幽靈持倉**: `Position` 使用 `ffill` 填充。若發生長假或停牌，系統會認為「一直持有」，忽略期間的資金佔用成本與跳空風險。

---

## 3. 人工智能實驗室 (@mle)
> **狀態**: 邏輯謬誤 (Logical Fallacy)
> **關鍵詞**: 數據洩露、優化器造假、驗證錯配

### 3.1 對抗競技場 (`src/models/arena/adversarial_arena.py`)
- **[CRITICAL] 驗證集錯配 (Overlap Leakage)**: 
    - 模型內部將數據切分為 80:20 (0-80% Train, 80-100% Test)。
    - Arena 驗證窗口固定為 60 bar。
    - 若數據長度較短 (如 200 bar, 20%=40)，Arena 驗證的 60 bar 中有 20 bar 實際上落在模型的**訓練集** (Train) 區域 (被模型強制置為 0 或更糟，參與了訓練)。
    - 後果：Arena 看到的業績被低估 (因訓練區信號為 0) 或虛高 (若模型未置 0 則為訓練集回測)。
- **[HIGH] 前視偏差 (Look-ahead)**: `strat_ret = s * r` 計算 ROI 時，未明確確保 `Signal[t]` 僅利用了 t 及之前的數據。若 Predictor 使用了 `shift(-1)` 標籤訓練，則此處評估成立；若 Predictor 預測的是 t+1 方向但標記在 t，則邏輯正確。需要嚴格的對齊測試。

### 3.2 AI 優化器 (`src/models/arena/ai_optimizer.py`)
- **[MEDIUM] 虛假優化**: 名為 Optimizer，實為 Runner。沒有實現貝葉斯優化 (Bayesian Optimization) 或網格搜索。僅執行單次任務。

---

## 建議行動方案 (Action Plan)

1. **立即修復 (Fix Now)**:
    - 替換 `DataLoader` 的 `ffill/bfill` 為 `data-gov-interp`。
    - 為 `CacheManager` 增加文件鎖 (FileLock)。
    - 修正 `Arena` 的驗證集切分邏輯，強制與模型內部 Split 一致。

2. **核心重構 (Refactor)**:
    - 重寫 `Portfolio`，引入波動率歸一化 (Volatility Scaling)。
    - 升級 `Valuation` DCF 模型，支持多階段 WACC。

3. **長期升級 (Upgrade)**:
    - 實現真正的 AI 超參數優化 (Optuna integration)。
