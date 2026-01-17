# Coding Standards (代碼規範)

> **版本**: v3.1  
> **萃取自**: Gemini Quant 代碼庫  
> **最後更新**: 2026-01-11

---

## 1. 命名規範 (Naming Conventions)

### 1.1 Python

| 類型 | 規範 | 示例 |
|------|------|------|
| **模塊/文件** | snake_case | `data_loader.py`, `tree_predictor.py` |
| **類名** | PascalCase | `DataLoader`, `ValuationEngine` |
| **函數/方法** | snake_case | `fetch_data()`, `calculate_dcf()` |
| **常量** | UPPER_SNAKE_CASE | `MAX_CACHE_SIZE`, `TARGET_START_DATE` |
| **私有成員** | 前綴 `_` | `_cache`, `_subscribers` |
| **模塊級單例** | 前綴 `_` | `_proxy = GeminiProxy()` |
| **類型標註布爾** | `HAS_*` 前綴 | `HAS_LIGHTGBM`, `HAS_XGBOOST` |

```python
# ✅ 正確
class DataUpdateService:
    TARGET_START_DATE = "2008-01-01"
    
    def __init__(self):
        self._cache = {}
        
    def update_incremental(self, tickers: List[str]):
        pass

# ❌ 錯誤
class dataUpdateService:  # 應為 PascalCase
    targetStartDate = "2008-01-01"  # 應為 UPPER_SNAKE_CASE
```

### 1.2 JavaScript/React

| 類型 | 規範 | 示例 |
|------|------|------|
| **組件** | PascalCase | `QuantDashboard`, `AISignalWidget` |
| **函數** | camelCase | `loadLiveData()`, `generateAIAnalysis()` |
| **常量** | UPPER_SNAKE_CASE | `API_BASE`, `MOCK_BACKTEST` |
| **CSS 類** | kebab-case | `metric-card`, `ai-insight-bar` |
| **State 變量** | camelCase | `isLoading`, `backtestData` |

```jsx
// ✅ 正確
const API_BASE = '/api/v1';

function QuantDashboard({ onNavigate }) {
    const [isLoading, setIsLoading] = useState(false);
    const [backtestData, setBacktestData] = useState(MOCK_BACKTEST);
    
    const loadLiveData = useCallback(async () => {
        // ...
    }, []);
}
```

---

## 2. 文件頭註釋 (File Header Comments)

### 2.1 Python 模塊

```python
"""
module_name.py - 模塊中文標題
================================
版本: v1.0 (Sprint X)
功能:
1. 功能描述 1
2. 功能描述 2

專家建議 (如適用):
- 技術建議或最佳實踐
"""
```

**實際示例**:
```python
"""
tree_predictor.py - 樹模型預測器
=============================================
版本: v1.0 (專家優化建議 Sprint 2)
功能: LightGBM 替換 MLP，用於趨勢預測

專家建議:
- 樹模型訓練速度極快，適合滾動窗口重訓
- 提供特徵重要性，可解釋性高
- 小樣本表現優於深度學習
"""
```

### 2.2 JavaScript/React 組件

```jsx
/**
 * ComponentName.jsx - 組件中文標題
 * 功能描述
 */
```

---

## 3. 函數/方法文檔 (Function Documentation)

### 3.1 中英雙語註釋風格

本項目採用 **中文為主、英文輔助** 的雙語註釋風格：

```python
def calculate_dcf(self, wacc=0.09, growth_rate=0.08, terminal_growth=0.025):
    """
    現金流折現模型 (Discounted Cash Flow Model)
    
    Args:
        wacc: 加權平均資本成本 (Weighted Average Cost of Capital)
        growth_rate: 增長率
        terminal_growth: 終值增長率
        
    Returns:
        float: DCF 估值結果
    """
    pass
```

### 3.2 單行註釋

行內註釋使用 `#`，放在代碼行尾或上方：

```python
# MEM-003 FIX: CacheManager 單例
_cache_manager_instance = None

def get_cache_manager():
    """獲取共享的 CacheManager 實例"""
    global _cache_manager_instance
    if _cache_manager_instance is None:
        _cache_manager_instance = CacheManager()  # 懶加載
    return _cache_manager_instance
```

### 3.3 Issue/Fix 標記

使用統一的前綴標記修復項：

```python
# CRITICAL-002 FIX: 修正 Look-ahead Bias
# MAJOR-005 FIX: 將 DataFrame 轉為 dict，確保 key 是字符串
# MINOR-004 FIX: 統一日誌配置，避免多個模塊重複調用 basicConfig
# MEM-001 FIX: 緩存配置
```

**標記規範**:
- `CRITICAL-XXX`: 關鍵業務邏輯修復
- `MAJOR-XXX`: 重要功能修復
- `MINOR-XXX`: 小問題修復
- `MEM-XXX`: 內存相關優化

---

## 4. 類型標註 (Type Annotations)

### 4.1 Python 類型標註

```python
from typing import List, Dict, Optional, Callable, Tuple, Any
from dataclasses import dataclass

@dataclass
class UpdateProgress:
    """更新進度"""
    total: int
    completed: int
    current_ticker: str
    status: str
    errors: List[str]
    
    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0

def fetch_data(
    self, 
    tickers: Union[str, List[str]], 
    start_date: str, 
    end_date: Optional[str] = None,
    interval: str = "1d"
) -> Dict[str, pd.DataFrame]:
    """獲取歷史數據"""
    pass
```

### 4.2 Dataclass 優先

配置和結果對象優先使用 `@dataclass`：

```python
@dataclass
class AIConfig:
    """AI 配置"""
    api_url: str = "http://127.0.0.1:8045"
    api_key: str = ""
    model_name: str = "gemini-3-pro-high"
    timeout: int = 60
```

---

## 5. 錯誤處理 (Error Handling)

### 5.1 標準 try-except 模式

```python
def load_model(self, path: str = None) -> bool:
    """加載模型"""
    path = path or self.model_path
    if not os.path.exists(path):
        return False
        
    try:
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.model = data['model']
        self.is_fitted = True
        logger.info(f"Model loaded from {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return False
```

### 5.2 可選依賴的優雅降級

```python
# 嘗試導入可選依賴
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False
    logger.warning("LightGBM not available, using fallback")

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

# 使用時按優先級選擇
if HAS_LIGHTGBM:
    self._fit_lightgbm(X, y, is_classification)
elif HAS_XGBOOST:
    self._fit_xgboost(X, y, is_classification)
else:
    self._fit_sklearn(X, y, is_classification)  # 最終後備
```

### 5.3 API 層錯誤處理

```python
@app.route('/api/v1/valuation/<ticker>', methods=['GET'])
def stock_valuation(ticker):
    """Get Intrinsic Value Analysis"""
    try:
        engine = ValuationEngine(ticker)
        result = engine.assess_value()
        return jsonify(result.__dict__)
    except Exception as e:
        logger.error(f"Valuation error for {ticker}: {e}")
        return jsonify({"error": str(e)}), 500
```

---

## 6. 日誌規範 (Logging Standards)

### 6.1 統一日誌配置

使用 `src/utils/logging_config.py` 而非在每個模塊中調用 `basicConfig`:

```python
# ❌ 錯誤 - 不要在每個模塊中這樣做
import logging
logging.basicConfig(level=logging.INFO)

# ✅ 正確 - 使用統一配置
from src.utils import get_logger
logger = get_logger(__name__)
```

### 6.2 日誌級別使用

```python
logger.debug(f"Cache hit for {ticker}")           # 調試信息
logger.info(f"Model loaded from {path}")          # 正常流程
logger.warning(f"LightGBM not available")         # 警告但可繼續
logger.error(f"Failed to load model: {e}")        # 錯誤
logger.error(f"Critical failure: {e}", exc_info=True)  # 帶堆棧
```

---

## 7. Import 組織 (Import Organization)

```python
# 1. 標準庫
import os
import sys
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

# 2. 第三方庫
import pandas as pd
import numpy as np

# 3. 可選第三方庫 (帶 try-except)
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

# 4. 項目內部模塊
from src.core.analyzers import SharpeAnalyzer
from src.utils import get_logger
```

---

## 8. 常量與配置 (Constants & Configuration)

### 8.1 類級常量

```python
class DataUpdateService:
    """數據更新服務"""
    
    DEFAULT_TICKERS = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
        "META", "TSLA", "BRK-B", "JPM", "V"
    ]
    TARGET_START_DATE = "2008-01-01"
```

### 8.2 環境變量

```python
# 從環境變量讀取敏感信息
API_KEY = os.environ.get('QUANT_API_KEY', '')

# 帶默認值的配置
self.model_path = os.environ.get('TREE_MODEL_PATH', 'temp/ml_models/lgbm_model.pkl')
```

---

## 9. 前端代碼規範 (Frontend Standards)

### 9.1 組件結構

```jsx
// 1. Imports
import React, { useState, useEffect, useCallback } from 'react';
import { LineChart, Line } from 'recharts';
import './ComponentName.css';

// 2. Constants
const API_BASE = '/api/v1';
const MOCK_DATA = { /* ... */ };

// 3. Helper Components
const MetricCard = ({ title, value }) => (
    <div className="metric-card">
        <span>{title}</span>
        <span>{value}</span>
    </div>
);

// 4. Main Component
export default function MainComponent({ prop1, prop2 }) {
    // State
    const [data, setData] = useState(MOCK_DATA);
    const [isLoading, setIsLoading] = useState(false);
    
    // Effects
    useEffect(() => {
        loadData();
    }, []);
    
    // Handlers
    const loadData = useCallback(async () => {
        // ...
    }, []);
    
    // Render
    return (
        <div className="main-container">
            {/* ... */}
        </div>
    );
}
```

### 9.2 CSS 命名

使用 BEM-like 命名：

```css
.metric-card { }
.metric-card .metric-header { }
.metric-card .metric-value { }
.metric-card .metric-value.positive { }
.metric-card .metric-value.negative { }
```

---

## 10. 安全紅線 (Security Invariants)

> **來源**: constitution.md

1. **絕不硬編碼 secrets/API keys**
   ```python
   # ❌ 錯誤
   API_KEY = "sk-xxxxxxxxxxxx"
   
   # ✅ 正確
   API_KEY = os.environ.get('QUANT_API_KEY', '')
   ```

2. **絕不在沒有備份的情況下刪除數據**
   ```python
   # 刪除前必須備份
   def delete_data(self, ticker: str):
       self._backup(ticker)  # 先備份
       # 然後刪除
   ```
