# 使用手冊 (System Usage Manual)

本手冊提供了 AI 量化交易系統的核心功能操作指南與解讀說明。

---

## 1. AI 模型訓練 (AI Model Training)

### 啟動訓練
通過 API 或腳本啟動模型訓練：
```bash
# 示例：訓練 LightGBM 模型
python -m src.models.arena.train --model_type lightgbm --ticker SPY
```

### 結果解讀
訓練完成後，系統會生成模型產物。重點關注：
- **Validation Score**: 使用 Purged CV 計算的交叉驗證分數，比傳統 CV 更能反映真實泛化能力。
- **Feature Importance**: 在模型元數據中查看。
    - 數值越高代表該特徵對預測貢獻越大。
    - *注意*: 若某特徵權重過高，可能存在 Look-ahead Bias，需檢查 `Data Governance` 流程。

---

## 2. 統計套利策略 (Statistical Arbitrage)

### 配置配對
在 `src/strategies/stat_arb/config.py` 中配置交易配對。

### 核心指標：Half-Life (半衰期)
系統使用 **Ornstein-Uhlenbeck (OU)** 過程對價差殘差進行建模。
- **定義**: 價差回歸到均值所需時間的期望值。
- **解讀**:
    - **Half-Life 越短**：均值回歸越快，交易機會越多，持倉風險越低。
    - **Half-Life 越長**：回歸緩慢，可能長期套牢。
    - *建議*: 僅交易 Half-Life < 20 (天) 的配對。

---

## 3. 回測與績效 (Backtesting)

### 運行回測
```bash
python -m src.backend.backtest_engine --strategy stat_arb --start_date 2023-01-01
```

### 關鍵指標詳解
- **Total Commission (總佣金)**:
    - 包含了開倉與平倉的雙向交易成本。
    - 計算公式: `Trade Volume * Rate` (預設 Rate 可在配置中調整)。
- **Sortino Ratio**:
    - 類似 Sharpe Ratio，但僅懲罰下行波動 (Downside Deviation)。
    - 對於追求絕對收益的策略，Sortino 比 Sharpe 更具參考價值。
- **Impact Cost (衝擊成本)**:
    - 模擬大額成交對市場價格的推動作用（目前版本使用固定滑點模型）。

---

## 4. 常見問題 (Troubleshooting)

### Q: 訓練時報錯 `Data Leakage Detected`?
**A**: 檢查您的特徵工程代碼。Purged CV 會嚴格檢測時間重疊。確保 `X` 的時間戳嚴格早於 `y` 的預測目標時間。

### Q: StatArb 找不到協整配對?
**A**: 嘗試放寬 `p-value` 閾值 (默認 0.05) 或增加候選股票池 (Universe)。
