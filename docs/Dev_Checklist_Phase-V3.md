# Quantum SaaS Platform - Phase V3 開發檢查清單
版本: v3.0 (角色對齊)
生成者: PM (Gemini)
日期: 2026-01-11

> [!IMPORTANT]
> **核心原則**: 基於證據的驗證。無日誌 = 無代碼 (No Logs = No Code)。
> **依賴鏈**: 模組 A (數據) -> 模組 B (宏觀) -> 模組 C (模型) -> 模組 D (回測) -> 模組 E/F (交易)。

---

## Phase 0: 架構標準化 (後端架構師 + PM)
*目標: 將 `src/` 結構與 Global Rules v5.0 對齊。*
- [x] **[ARCH-01] 目錄結構對齊**
  - [x] 建立/確認 `src/data_loader` (目標: 模組 A)
  - [x] 建立/確認 `src/models/arena` (目標: 模組 C)
  - [x] 建立/確認 `src/api` (目標: 集中式 API)
  - [x] *行動*: 若有需要，遷移現有的 `src/data_pipeline`, `src/models/*.py`, `src/backend/api_server.py` 至新結構。

---

## Phase 1: 模組 A - 數據攝取與治理 (數據治理工程師)
*目標: 「基石」。攝取、清理、驗證、儲存。*
*依賴於: Phase 0*
- [x] **[DATA-01] 數據攝取引擎 (`src/data_loader`)**
  - [x] 實作具有穩健重試邏輯的 `yfinance` 獲取器。
  - [ ] 實作本地備份獲取器 (防幻覺規則)。
- [x] **[DATA-02] 數據品質守門員**
  - [x] **丟棄規則**: 丟棄缺失值 > 5% 的資產。
  - [x] **填充規則**: 對缺失值 < 5% 的資產進行插值。
  - [x] **驗證**: 生成「數據形狀與完整性報告」(行數, 缺失, 插值)。
- [x] **[DATA-03] 儲存標準化**
  - [x] 將輸出儲存為 `.parquet` 於 `data/processed/`。
  - [x] *輸出*: 準備好供模組 B/C 使用的有效 Parquet 檔案。

---

## Phase 2: 模組 B - 宏觀情資儀表板 (後端 + 數據工程)
*目標: 「護欄」。市場體制信號。*
*依賴於: Phase 1 (數據可用)*
- [x] **[MACRO-01] 宏觀數據源**
  - [x] 攝取 VIX, 美債 (10Y, 2Y), 聯邦基金利率。
  - [x] 攝取 S&P 500 漲跌騰落線 (Advance/Decline Line)。
- [x] **[MACRO-02] 新聞與情緒**
  - [x] 獲取滾動財經新聞 (若 API 受限則使用模擬)。
  - [x] 實作基本 NLP 情緒評分。
- [x] **[MACRO-03] 風險邏輯實作**
  - [x] 計算 `Macro_Risk_Score` (0-100)。
  - [x] 實作觸發: 分數 > 80 = "Risk Off" (避險模式)。
  - [x] *輸出*: 可供其他模組使用的全域風險信號。

---

## Phase 3: 模組 C - AI 模型引擎 (機器學習工程師)
*目標: 「大腦」。對抗競技場。*
*依賴於: Phase 1 (數據) & Phase 2 (體制感知)*
- [x] **[MLE-01] 模型架構設定 (`src/models/arena`)**
  - [x] 定義模型抽象基類 (Abstract Base Class)。
  - [x] 實作包裝器: XGBoost, LightGBM, LSTM, MLP。
- [x] **[MLE-02] 對抗競技場邏輯**
  - [x] 實作「通用驗證集」強制執行。
  - [x] 實作基於近期表現 (最近 30 天) 的動態權重。
- [x] **[MLE-03] 防過擬合協議**
  - [x] 實作滾動驗證 (Walk-Forward Validation)。
  - [x] *輸出*: 訓練好的模型儲存於 `models/saved/` 並附帶表現日誌。

---

## Phase 4: 系統整合 (後端 + 前端)
*目標: 「脊椎與面孔」。*
*依賴於: Phase 3*
- [x] **[BE-01] API 暴露 (`src/api`)**
  - [x] 端點: `GET /data/status` (模組 A 狀態)
  - [x] 端點: `GET /macro/risk` (模組 B 分數)
  - [x] 端點: `POST /arena/predict` (模組 C 推論)
- [ ] **[FE-01] 儀表板視覺化**
  - [ ] 顯示宏觀風險儀表 (Macro Risk Gauge)。
  - [ ] 顯示模型競技場排行榜 (Model Arena Leaderboard)。
