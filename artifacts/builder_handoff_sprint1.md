# Builder 移交文檔：Sprint 1 功能 UI 落地

**日期**: 2026-01-13  
**來源**: @pm → @builder  
**狀態**: 🔴 待執行

---

## 移交背景

PM 功能審計發現 **10/10 項已開發功能在 UI 中無入口**。用戶拒絕驗收，要求整改。

本移交包含 **Sprint 1 (P0 優先級)** 的 5 項功能 UI 落地任務。

---

## 任務清單

### 🔴 Task 1: VaR/CVaR 風險卡片
**優先級**: P0 | **工時**: 2h

**要求**:
- 位置：`QuantDashboard.jsx` 風險指標區
- 顯示：VaR (95%) 和 CVaR (95%)
- 數據：從 `/api/v1/backtest` 的 `metrics` 獲取

**驗收標準**:
- 執行回測後，卡片顯示正確數值
- 無 Console 錯誤

---

### 🔴 Task 2: Sortino Ratio
**優先級**: P0 | **工時**: 1h

**要求**:
- 位置：`QuantDashboard.jsx` 績效摘要區
- 顯示：Sortino Ratio（與 Sharpe Ratio 並列）
- 數據：從 `/api/v1/backtest` 的 `metrics.Sortino_Ratio` 獲取

**驗收標準**:
- 執行回測後，指標正確顯示

---

### 🔴 Task 3: CAPM Alpha/Beta
**優先級**: P0 | **工時**: 3h

**要求**:
1. 後端：新增 `/api/v1/capm/analyze` 端點
2. 前端：在 `ArenaLeaderboard.jsx` 新增 CAPM 分析區

**數據結構**:
```json
{
  "ticker": "AAPL",
  "alpha": 0.0012,
  "beta": 1.15,
  "r_squared": 0.87,
  "p_value": 0.001
}
```

**驗收標準**:
- AI 對戰結果旁顯示 CAPM 指標

---

### 🔴 Task 4: Total Commission
**優先級**: P0 | **工時**: 1h

**要求**:
- 位置：`SimulationDashboard.jsx`
- 顯示：總佣金支出、交易日誌中的佣金列
- 數據：從 `/api/v1/simulation/status` 獲取

**驗收標準**:
- 模擬交易後顯示累計佣金

---

### 🔴 Task 5: Feature Importance
**優先級**: P0 | **工時**: 4h

**要求**:
- 位置：AI 實驗室 → 模型詳情彈窗
- 顯示：Top 10 特徵重要性柱狀圖
- 數據：從訓練結果 `job.result.feature_importance` 獲取

**驗收標準**:
- 點擊模型「查看分析」按鈕顯示特徵圖表

---

## 完成後

1. 更新 `artifacts/handoff_notes.md`
2. 呼叫 `/handoff-to-auditor` 進行 QA 復測
3. 用戶確認驗收

---

## 參考文檔

- [PM 審計報告](file:///Users/jerrylee/coding/artifacts/pm_feature_gap_audit.md)
- [實施計畫](file:///Users/jerrylee/.gemini/antigravity/brain/ecb88d0d-1803-4b1b-98ed-5e0669858cdd/implementation_plan.md)
- [後端 API](file:///Users/jerrylee/coding/src/api/main.py)
