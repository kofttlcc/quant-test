# 📋 Auditor → Builder 移交指令

> **發起者**: @auditor (Claude - The Architect)  
> **接收者**: @builder (Gemini)  
> **日期**: 2026-01-13  
> **狀態**: 🟡 待修正 (Pending Fixes)

---

## 一、審計結論

你的產出物 (`deep_audit_report.md`, `iteration_plan.md`) 整體質量優良，我**同意**實施方向。

但在開始執行 Phase 0 之前，你必須完成以下修正項。

---

## 二、阻塞項 (Blocking Items) - 必須完成

### 📌 任務 1: 翻譯 `handoff_notes.md`

**問題**: 該文件違反 Constitution 6.0 語言規範（使用英文撰寫）

**要求**:
- 將 `artifacts/handoff_notes.md` 內容翻譯為**繁體中文**
- 保留技術術語的英文原文

**驗收標準**:
- [ ] 所有描述性文字均為繁體中文
- [ ] 技術術語（如 `ffill`, `WACC`, `Arena`）可保留英文

---

### 📌 任務 2: 補充 Arena 切分策略

**問題**: `iteration_plan.md` 第零階段對 `adversarial_arena.py` 的修改說明不夠具體

**要求**: 在 `iteration_plan.md` 的第零階段 `adversarial_arena.py` 部分補充以下內容：

```markdown
#### [MODIFY] [adversarial_arena.py](file:///Users/jerrylee/coding/src/models/arena/adversarial_arena.py)
- [ ] **[CRITICAL]** 統一訓練/驗證集切分邏輯：
  - **策略**: Arena 統一管理切分，模型不再自行切分
  - **實施**: 新增 `split_data(df, train_ratio=0.8)` 函數，返回 (train_df, val_df)
  - **傳遞**: 將切分後的數據分別傳入各模型的 `train()` 和 `predict()` 方法
- [ ] 嚴格對齊 Signal 與 Return 計算 ROI
- [ ] 新增 Purge 機制：移除 Train/Val 交界處 ±5 bar 的數據
```

---

### 📌 任務 3: 升級驗證計劃

**問題**: 當前驗證計劃過於簡略，缺少關鍵驗收標準

**要求**: 在 `iteration_plan.md` 的 `## 驗證計畫` 部分補充以下內容：

```markdown
## 驗證計畫

### 0. Baseline 記錄 (執行前)
- [ ] 記錄當前系統在 SPY 2020-2025 回測的指標：
  - Sharpe Ratio
  - Max Drawdown
  - Total Return
- [ ] 保存為 `artifacts/baseline_metrics.json`

### 1. 單元測試
- [ ] 為 `data-gov-interp` 撰寫 `tests/test_interpolation.py`
- [ ] 為 `data-gov-outliers` 撰寫 `tests/test_outliers.py`
- [ ] 為 `quant-ml-validation` 撰寫 `tests/test_purged_cv.py`

### 2. 對比測試
- [ ] 比較新舊清洗邏輯對 Backtest 結果的影響
- [ ] 預期：新邏輯的波動率略高，Sharpe 略低，但更真實

### 3. AI 驗證 (第三階段交付物)
- [ ] **生成 Purged CV 熱力圖**: 證明 Train/Val/Purged 區域嚴格分離
- [ ] 保存為 `artifacts/purged_cv_heatmap.png`
```

---

## 三、建議項 (Non-Blocking) - 可選擇採納

### 💡 建議 1: 降級 WACC 模型複雜度

**原因**: 多階段 WACC 需要利率期限結構數據，超出當前數據能力

**建議**: 將 `iteration_plan.md` 第二階段的 `valuation.py` 修改為：

```markdown
#### [MODIFY] [src/models/valuation.py](file:///Users/jerrylee/coding/src/models/valuation.py)
- [ ] [長期研究] 支持多階段 WACC（需待利率數據源就緒）
- [ ] [短期] 在 UI 增加 WACC 靜態假設的警示標籤
```

### 💡 建議 2: 技能依賴聲明

在 `iteration_plan.md` 開頭增加技能依賴表：

```markdown
## 技能依賴

| 階段 | 使用技能 | 路徑 |
|------|----------|------|
| 1 | Brownian Bridge 插值 | `skills/數據治理/data-gov-interp/` |
| 1 | MAD 異常值檢測 | `skills/數據治理/data-gov-outliers/` |
| 2 | 風險指標 (VaR/CVaR) | `skills/傳統金融/trad-fi-risk/` |
| 3 | Purged CV | `skills/機器學習/quant-ml-validation/` |
```

---

## 四、交付檢查清單

完成修正後，請確保：

- [ ] `handoff_notes.md` 已翻譯為繁體中文
- [ ] `iteration_plan.md` 已補充 Arena 切分策略
- [ ] `iteration_plan.md` 已補充驗證計劃
- [ ] 所有修改已 commit 到 `feat/20260113-system-audit` 分支

完成後，請 Ping @auditor 進行最終審核與合併批准。

---

**Signed,**  
*The Architect (@auditor)*
