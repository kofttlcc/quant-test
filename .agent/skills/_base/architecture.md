# Architecture Patterns (架構模式)

> **版本**: v3.1  
> **萃取自**: Gemini Quant 代碼庫  
> **最後更新**: 2026-01-11

---

## 1. 整體架構 (High-Level Architecture)

本系統採用 **分層式 (Layered) + 事件驅動 (Event-Driven) 混合架構**：

```
┌────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)              │
│     src/frontend/src/components/*.jsx                  │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / REST API
                            ▼
┌────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                    │
│                    src/api/main.py                      │
└───────────────────────────┬────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌───────────────┐   ┌──────────────┐
│   Services   │   │    Models     │   │   Backend    │
│ (ai_proxy,   │   │ (valuation,   │   │ (backtest,   │
│  news,       │   │  arena/,      │   │  paper_trade,│
│  config)     │   │  macro/)      │   │  storage)    │
└──────────────┘   └───────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌────────────────────────────────────────────────────────┐
│                    Data Layer                           │
│     src/data_loader/ (DataLoader, CacheManager,        │
│                       DataUpdateService)               │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                    Core Infrastructure                  │
│     src/core/ (EventBus, Analyzers, DataModels)        │
└────────────────────────────────────────────────────────┘
```

---

## 2. 目錄結構規範 (Directory Structure)

```
src/
├── __init__.py           # 包初始化
├── api/                  # API 層 (Flask endpoints)
│   └── main.py          # 所有 REST endpoints 集中定義
│
├── backend/              # 回測與交易引擎
│   ├── backtest_engine.py
│   ├── paper_trade.py
│   ├── portfolio.py
│   ├── arena.py
│   └── storage.py
│
├── core/                 # 核心基礎設施
│   ├── event_bus.py     # AsyncIO 事件總線
│   ├── events.py        # Event & EventType 定義
│   ├── analyzers.py     # Sharpe, Drawdown 分析器
│   ├── data_models.py   # 共用數據結構
│   └── data_utils.py    # 數據工具函數
│
├── data_loader/          # 數據加載與緩存
│   ├── data_loader.py   # 統一數據加載器 (yfinance)
│   ├── data_update_service.py  # 數據更新服務
│   ├── cache_manager.py # 緩存管理
│   ├── validator.py     # 數據驗證
│   └── providers/       # 數據提供者 (可擴展)
│
├── models/               # 業務模型與算法
│   ├── valuation.py     # 估值引擎 (DCF, Graham)
│   ├── strategy_logic.py
│   ├── arena/           # AI 模型集合
│   │   ├── tree_predictor.py   # LightGBM
│   │   ├── lstm_predictor.py   # LSTM (legacy)
│   │   └── adversarial_arena.py
│   └── macro/           # 宏觀分析
│       ├── macro_features.py
│       └── regime_detector.py
│
├── services/             # 外部服務集成
│   ├── ai_proxy.py      # Gemini API 代理
│   ├── news_service.py  # 新聞抓取
│   ├── config_service.py # 配置持久化
│   └── model_registry.py # 模型版本管理
│
├── utils/                # 工具類
│   ├── __init__.py      # 導出公共工具
│   ├── logging_config.py # 統一日誌配置
│   ├── model_config.py  # 模型路徑配置
│   └── metrics.py       # 性能指標計算
│
└── frontend/             # React 前端
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── index.css
        ├── components/   # UI 組件
        └── services/     # API 客戶端
```

---

## 3. 設計模式 (Design Patterns)

### 3.1 Service Pattern (服務模式)

**應用場景**: 封裝外部 API 調用、複雜業務邏輯

```python
# src/services/ai_proxy.py
class GeminiProxy:
    """服務類: 封裝 Gemini API 調用"""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
    
    def generate(self, prompt: str, system_prompt: str = None) -> dict:
        """統一的對外接口"""
        # 實現細節隱藏
        pass
```

**規則**:
- 服務類應使用 **單例模式** 或提供 `get_*()` 工廠函數
- 服務類不應持有狀態，或僅持有配置級別的狀態

---

### 3.2 Singleton via Module (模塊級單例)

**應用場景**: 共享資源 (如緩存管理器、代理服務)

```python
# src/services/ai_proxy.py

# 模塊級單例
_proxy = GeminiProxy()

def get_ai_proxy() -> GeminiProxy:
    """獲取 AI Proxy 單例"""
    return _proxy
```

**規則**:
- 使用 `_instance` 或 `_*` 命名模塊級私有變量
- 提供 `get_*()` 函數作為公共訪問點

---

### 3.3 Factory Pattern (工廠模式)

**應用場景**: 根據配置動態創建策略、模型

```python
# src/models/arena/tree_predictor.py

def _fit_lightgbm(self, X, y, is_classification):
    # LightGBM 實現
    pass
    
def _fit_xgboost(self, X, y, is_classification):
    # XGBoost 實現 (後備)
    pass
    
def _fit_sklearn(self, X, y, is_classification):
    # sklearn 實現 (最終後備)
    pass
```

**規則**:
- 優先導入 → 後備導入 的漸進降級
- 使用 `HAS_*` 布爾標誌追蹤可用性

---

### 3.4 Event-Driven Architecture (事件驅動架構)

**應用場景**: 解耦組件間通信

```python
# src/core/event_bus.py

class EventBus:
    """AsyncIO-based Event Bus"""
    
    def subscribe(self, event_type: EventType, callback):
        """訂閱事件"""
        pass
    
    async def publish(self, event: Event):
        """發布事件"""
        pass
```

**規則**:
- 事件類型定義在 `src/core/events.py`
- Callback 必須是 `async` 函數

---

### 3.5 Dataclass Pattern (數據類模式)

**應用場景**: 結構化配置、結果對象

```python
# 優先使用 dataclass
from dataclasses import dataclass

@dataclass
class TreeModelConfig:
    n_estimators: int = 100
    max_depth: int = 5
    learning_rate: float = 0.05
    
@dataclass
class ValuationResult:
    ticker: str
    current_price: float
    fair_value: float
    status: str
    data_quality: str = "High"
```

**規則**:
- 配置類使用 `@dataclass` 並提供默認值
- 結果類使用 `@dataclass` 確保類型安全

---

## 4. 模塊依賴規則 (Dependency Rules)

```
                  ┌─────────────────┐
                  │      api/       │
                  └────────┬────────┘
                           │ 可以調用
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐     ┌──────────┐     ┌──────────┐
    │ services │     │  models  │     │ backend  │
    └────┬─────┘     └────┬─────┘     └────┬─────┘
         │                │                │
         └────────────────┼────────────────┘
                          ▼
                   ┌──────────────┐
                   │ data_loader  │
                   └──────┬───────┘
                          ▼
                   ┌──────────────┐
                   │    core      │
                   └──────────────┘
```

**規則**:
- 上層可以調用下層，反之則不行
- `core/` 是基礎層，不應依賴其他 `src/` 模塊
- 跨層通信使用 EventBus 或依賴注入

---

## 5. 前端架構 (Frontend Architecture)

採用 **Component-Based Architecture**：

```
src/frontend/src/
├── App.jsx              # 根組件 (路由控制)
├── components/          # 可複用組件
│   ├── QuantDashboard.jsx    # 主儀表板 (Single-Page)
│   ├── QuantDashboard.css    # 組件樣式
│   ├── AILab.jsx            # AI 實驗室頁面
│   ├── TradingChart.jsx     # 圖表組件
│   └── ModelTrainingModal.jsx # Modal 組件
├── services/
│   └── api.js           # API 客戶端 (集中管理)
└── index.css            # 全局樣式
```

**規則**:
- 每個主要組件都有對應的 `.css` 文件
- API 調用統一通過 `services/api.js`
- 使用 React Hooks (`useState`, `useEffect`, `useCallback`)

---

## 6. Self-Test Pattern (自測試模式)

每個 Python 模塊應包含 `if __name__ == "__main__":` 區塊：

```python
if __name__ == "__main__":
    print("--- SELF-TEST START: module_name.py ---")
    
    # 測試代碼
    result = my_function()
    
    if result > 0:
        print("[TEST] SUCCESS: ...")
    else:
        print("[TEST] FAILURE: ...")
        
    print("--- SELF-TEST END ---")
```

**規則**:
- 輸出格式統一使用 `--- SELF-TEST START/END ---`
- 測試結果使用 `[TEST] SUCCESS/FAILURE:` 前綴
