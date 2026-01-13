# 實施計畫：優化神器 UI 集成 (Phase 4)

## 目標 (Goal)
將 Phase 1-3 已經實施的後端優化成果 (Feature Importance, StatArb Improvements, Backtest Fixes) 正式接入 Frontend UI，並通過 API 暴露關鍵指標，完成 "AI 工廠化" 與 "屍檢修復" 的最後一哩路。

## 需要用戶審查 (User Review Required)
> [!IMPORTANT]
> 此階段將修改 `AITrainer` 的訓練流程，增加 `FeatureSelector` 的計算步驟，可能會稍微延長訓練時間 (約 +5~10秒)。

## 擬議變更 (Proposed Changes)

### Backend (Python)

#### [MODIFY] [ai_optimizer.py](file:///Users/jerrylee/coding/src/models/arena/ai_optimizer.py)
- **變更**: 在 `_run_training` 流程結束前，初始化 `FeatureSelector` 並計算特徵重要性。
- **存儲**: 將 Top-K 特徵及權重保存至 `job.result` 和模型註冊表 (Model Registry) 的 metadata 中。

#### [MODIFY] [engine.py](file:///Users/jerrylee/coding/src/strategies/stat_arb/engine.py)
- **變更**: 修改 `generate_signals` 以返回包含 OU Process 參數 (Half-Life, Theta, Sigma) 的字典，而不僅僅是打印日誌。
- **目的**: 讓前端能顯示當前配對的均值回歸力度。

#### [MODIFY] [selector.py](file:///Users/jerrylee/coding/src/strategies/stat_arb/selector.py)
- **變更**: 在篩選最佳配對時，顯式調用 `calculate_ou_params` 並將 `half_life` 加入返回的配對信息中。

#### [MODIFY] [backtest_engine.py](file:///Users/jerrylee/coding/src/backend/backtest_engine.py)
- **變更**: 在 `metrics` 字典中新增 `Total_Commission` (總佣金) 字段。
- **目的**: 讓用戶直觀看到交易成本對策略的影響。

#### [MODIFY] [main.py](file:///Users/jerrylee/coding/src/api/main.py)
- **變更**: 更新 `/api/ai/models/{model_id}` 或相關端點，確保返回 `feature_importance` 數據。
- **變更**: 更新 `/api/backtest/run` 端點，確保返回 StatArb 的 `half_life` 等額外指標。

### Frontend (React)
*(由 @frontend 角色負責，此處僅列出對接點)*
- **AI Model Details**: 新增 "Feature Importance" 柱狀圖。
- **StatArb Strategy**: 在策略詳情頁顯示 "Estimated Half-Life"。
- **Trade Log**: 在回測報告中顯示 "Total Commission"。

---

## 驗證計畫 (Verification Plan)

### 自動化驗證 (Automated Verification)
- **腳本**: 創建 `verify_ui_integration.py`
    1. **Test AI Training**: 模擬一次 AI 訓練，檢查返回的 Result 是否包含 `feature_importance`。
    2. **Test StatArb**: 運行 StatArb 策略，檢查返回的 Metrics 是否包含 `half_life`。
    3. **Test Backtest**: 運行一次回測，檢查 Metrics 是否包含 `Total_Commission` > 0。

### 手動驗證 (Manual Verification)
- 啟動 Frontend，進入 "AI Model Center" 查看新訓練模型的特徵重要性圖表。
- 運行 StatArb 策略回測，確認 UI 顯示半衰期數據。
