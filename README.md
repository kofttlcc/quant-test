# AI 量化交易系統 (AI Quantitative Trading System)

本項目是一個基於 Python 的模組化量化交易系統，集成了現代 **Machine Learning (LightGBM, LSTM)** 與經典 **Financial Engineering (StatArb, Pricing)** 能力。

經過 Phase 1-4 的深度迭代，系統已具備工業級的數據治理與風控能力。

## ✨ 核心功能 (Features)

### 1. 數據治理 (Data Governance)
- **Robust Cleaning**: 採用 `MAD` (Median Absolute Deviation) 進行魯棒異常值檢測，摒棄傳統標準差法。
- **Smart Interpolation**: 使用 **Brownian Bridge** 算法修復缺失數據，保留市場波動特性。

### 2. 人工智能 (AI Core)
- **Model Arena**: 支援 LightGBM、MLP、LSTM 等多種模型架構。
- **Purged CV**: 實作 `CombinatorialPurgedKFold`，嚴格防止時間序列數據洩露。
- **Feature Importance**: 自動計算並保存特徵重要性，提升模型可解釋性。

### 3. 金融工程 (Financial Engineering)
- **Statistical Arbitrage**: 基於 OU Process (Ornstein-Uhlenbeck) 的配對交易引擎，實時估計 **Half-Life** (半衰期)。
- **Derivatives Pricing**: 內置 Black-Scholes 期權定價模型與 Greeks 計算。
- **Risk Metrics**: 支援 VaR (Value at Risk), CVaR, Sortino Ratio 等機構級風控指標。

### 4. 回測引擎 (Backtesting)
- **Realistic Simulation**: 考慮雙向佣金 (Commission)、滑點與市場衝擊。
- **Comprehensive Reporting**: 提供詳細的 PnL 歸因分析與可視化圖表。

## 🏗️ 系統架構 (Architecture)

```mermaid
graph TD
    Data[Data Loader] --> Governance[Data Governance]
    Governance --> FeatureEng[Feature Engineering]
    
    FeatureEng --> AI_Arena[AI Arena (ML Models)]
    FeatureEng --> StatArb[StatArb Engine]
    
    AI_Arena --> Signals[Signal Generation]
    StatArb --> Signals
    
    Signals --> Portfolio[Portfolio Optimizer]
    Portfolio --> Execution[Execution / Backtest]
    
    subgraph "Core Modules"
        Governance
        AI_Arena
        StatArb
    end
```

## 🚀 快速開始 (Quick Start)

詳細的使用指南請參考 [USAGE.md](USAGE.md)。

### 前置要求
- Python 3.9+
- Redis (用於緩存與消息隊列)

### 安裝
```bash
git clone <repo_url>
cd coding
pip install -r requirements.txt
```

### 運行測試
```bash
pytest tests/
```
