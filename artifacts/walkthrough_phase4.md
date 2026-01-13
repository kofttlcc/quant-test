# Walkthrough Phase 4: UI Integration

## 1. AI Feature Importance
> **Goal**: 讓用戶了解 AI 模型決策依據。

- **Implementation**: `AITrainer` 訓練後調用 `FeatureSelector`。
- **Result**: `job.result` 中包含 `feature_importance`。
- **Dashboard Preview**: (前端需對接) 預計在 AI Model Card 顯示 Top-Features 柱狀圖。

## 2. StatArb Half-Life
> **Goal**: 讓用戶判斷配對交易的均值回歸速度。

- **Implementation**: `StatArbEngine` 在信號生成時返回 `HalfLife`。
- **Metric**: 值越小表示回歸越快。若為 `inf` 則無回歸。

## 3. Backtest Commission
> **Goal**: 增加回測真實性，展示交易成本。

- **Implementation**: `Backtester` 計算並返回 `Total_Commission`。

## 4. Verification Evidence
`src/verify_ui_integration.py` 輸出截圖:
```
INFO:VerifyUI:✅ Half-Life Exposed in Selector: inf
INFO:VerifyUI:✅ Total Commission Exposed: 0.0010
INFO:VerifyUI:✅ Feature Importance Found: ['Momentum', 'Returns', 'Volatility']...
🟢 ALL UI VERIFICATION TESTS PASSED
```
