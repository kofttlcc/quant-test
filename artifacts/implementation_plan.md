# 實施計畫：系統交付與文檔完善 (Phase 5)

## 目標 (Goal)
完成 Phase 1-4 的迭代後，系統核心能力已顯著提升。本階段旨在**更新文檔**以反映最新功能 (AI, StatArb, Data Gov)，並**清理項目結構**，確保代碼庫整潔可維護。

## 需要用戶審查 (User Review Required)
> [!NOTE]
> 將把 `src/` 目錄下的臨時驗證腳本 (`verify_*.py`) 移動到 `tests/verification/`。這是一個文件結構變更。

## 擬議變更 (Proposed Changes)

### Documentation

#### [MODIFY] [README.md](file:///Users/jerrylee/coding/README.md)
- **變更**:
    - 更新 "Feature Highlights" (新增 Purged CV, Black-Scholes, Impact Cost, etc.)。
    - 更新系統架構描述。

#### [NEW] [USAGE.md](file:///Users/jerrylee/coding/USAGE.md)
- **內容**:
    - **Backtesting**: 解讀 Total Commission, Half-Life 參數。
    - **AI Training**: 如何訓練新模型並解讀 Feature Importance。
    - **Troubleshooting**: 常見問題排查。

### Maintenance

#### [MOVE] Verification Scripts
- **源文件**: `src/verify_phase3.py`, `src/verify_ui_integration.py`
- **目標**: `tests/verification/`
- **目的**: 保持源代碼目錄專注於業務邏輯。

## 驗證計畫 (Verification Plan)

### 手動驗證
1. **文檔檢查**: 渲染 `README.md` 和 `USAGE.md`，確認格式正確且鏈接有效。
2. **腳本運行**: 在新目錄下運行驗證腳本，確保路徑引用正確。
    - `python -m tests.verification.verify_ui_integration`
