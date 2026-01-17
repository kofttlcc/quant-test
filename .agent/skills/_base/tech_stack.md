# Tech Stack Specifics (技術棧詳解)

> **版本**: v3.1  
> **萃取自**: Gemini Quant 代碼庫  
> **最後更新**: 2026-01-11

---

## 1. 技術棧總覽 (Tech Stack Overview)

### 1.1 後端 (Backend)

| 類別 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **Web 框架** | Flask | - | REST API 服務 |
| **數據處理** | Pandas | - | DataFrame 操作 |
| **數值計算** | NumPy | - | 矩陣運算 |
| **ML 框架** | LightGBM | - | 樹模型預測 (優先) |
| | XGBoost | - | 樹模型 (後備) |
| | scikit-learn | - | 通用 ML (最終後備) |
| **數據源** | yfinance | - | 美股/加密貨幣數據 |
| **AI 服務** | Google Gemini | 3 Pro | AI 分析生成 |
| **序列化** | pickle | - | 模型持久化 |
| **異步** | asyncio | - | Event Bus |

### 1.2 前端 (Frontend)

| 類別 | 技術 | 版本 | 用途 |
|------|------|------|------|
| **框架** | React | 19.2.0 | UI 框架 |
| **構建工具** | Vite | 7.2.4 | 開發/打包 |
| **圖表** | Recharts | 3.6.0 | 數據可視化 |
| | lightweight-charts | 5.1.0 | K 線圖 |
| **圖標** | lucide-react | 0.562.0 | 圖標庫 |
| **Lint** | ESLint | 9.39.1 | 代碼質量 |

---

## 2. 核心庫初始化代碼 (Core Library Initialization)

### 2.1 Flask API 服務

```python
# src/api/main.py

from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# CORS 設置
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# API Key 驗證 (生產環境必須)
API_KEY = os.environ.get('QUANT_API_KEY', '')

def check_api_key():
    """API Key 驗證"""
    if os.environ.get('FLASK_ENV') == 'production' and not API_KEY:
        raise RuntimeError("Production mode requires QUANT_API_KEY")

# 路由定義
@app.route('/api/v1/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# 啟動
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
```

---

### 2.2 yfinance 數據加載

```python
# src/data_loader/data_loader.py

import yfinance as yf
import pandas as pd
import time
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """統一數據加載器"""
    
    MAX_CACHE_SIZE = 50  # 緩存限制
    CACHE_TTL = 3600     # 1 小時過期
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.cache = {}
        self._cache_timestamps = {}
        
    def fetch_data(
        self, 
        tickers: Union[str, List[str]], 
        start_date: str, 
        end_date: Optional[str] = None,
        interval: str = "1d"
    ) -> Dict[str, pd.DataFrame]:
        """獲取歷史數據"""
        if isinstance(tickers, str):
            tickers = [tickers]
            
        ticker_str = " ".join(tickers)
        
        for attempt in range(self.max_retries):
            try:
                data = yf.download(
                    tickers, 
                    start=start_date, 
                    end=end_date, 
                    interval=interval,
                    group_by='ticker', 
                    auto_adjust=False,
                    progress=False
                )
                
                if data.empty:
                    logger.warning("下載數據為空")
                    return {}
                    
                # 處理結果...
                return self._process_data(data, tickers)
                
            except Exception as e:
                logger.error(f"下載失敗 (嘗試 {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
```

---

### 2.3 LightGBM 模型訓練

```python
# src/models/arena/tree_predictor.py

import numpy as np
import logging
from typing import List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# 可選依賴導入模式
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

from sklearn.ensemble import GradientBoostingClassifier

@dataclass
class TreeModelConfig:
    """樹模型配置"""
    n_estimators: int = 100
    max_depth: int = 5
    learning_rate: float = 0.05
    min_child_samples: int = 20
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    reg_alpha: float = 0.1   # L1 正則化
    reg_lambda: float = 0.1  # L2 正則化
    verbose: int = -1


class LightGBMPredictor:
    """LightGBM 趨勢預測器"""
    
    def __init__(self, config: TreeModelConfig = None):
        self.config = config or TreeModelConfig()
        self.model = None
        self.feature_names: List[str] = []
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str] = None):
        """訓練模型"""
        self.feature_names = feature_names or [f"f{i}" for i in range(X.shape[1])]
        
        unique_y = np.unique(y)
        is_classification = len(unique_y) <= 10
        
        if HAS_LIGHTGBM:
            self._fit_lightgbm(X, y, is_classification)
        elif HAS_XGBOOST:
            self._fit_xgboost(X, y, is_classification)
        else:
            self._fit_sklearn(X, y, is_classification)
            
        self.is_fitted = True
        
    def _fit_lightgbm(self, X, y, is_classification):
        """LightGBM 訓練"""
        params = {
            'objective': 'binary' if is_classification else 'regression',
            'metric': 'binary_logloss' if is_classification else 'mse',
            'boosting_type': 'gbdt',
            'num_leaves': 2 ** self.config.max_depth - 1,
            'max_depth': self.config.max_depth,
            'learning_rate': self.config.learning_rate,
            'min_child_samples': self.config.min_child_samples,
            'subsample': self.config.subsample,
            'colsample_bytree': self.config.colsample_bytree,
            'reg_alpha': self.config.reg_alpha,
            'reg_lambda': self.config.reg_lambda,
            'verbose': self.config.verbose,
            'seed': 42
        }
        
        train_data = lgb.Dataset(X, label=y, feature_name=self.feature_names)
        self.model = lgb.train(params, train_data, num_boost_round=self.config.n_estimators)
```

---

### 2.4 Gemini API 代理

```python
# src/services/ai_proxy.py

import os
import logging
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """AI 配置"""
    api_url: str = "http://127.0.0.1:8045"
    api_key: str = ""
    model_name: str = "gemini-3-pro-high"
    timeout: int = 60


class GeminiProxy:
    """Gemini AI 代理服務 (直接 HTTP 版本)"""
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        
    def _load_config_from_env(self):
        """從環境變量加載配置"""
        self.config.api_url = os.environ.get('GEMINI_API_URL', self.config.api_url)
        self.config.api_key = os.environ.get('GEMINI_API_KEY', '')
        self.config.model_name = os.environ.get('GEMINI_MODEL', self.config.model_name)
        
    def generate(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        調用 Gemini API 生成內容 (直接 HTTP)
        
        重要: 使用 proxies={'http': None, 'https': None} 繞過系統代理
        """
        try:
            # 構建請求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.config.api_key}"
            }
            
            payload = {
                "model": self.config.model_name,
                "contents": [{"role": "user", "parts": [{"text": prompt}]}]
            }
            
            if system_prompt:
                payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
            
            # 直接請求，繞過系統代理
            response = requests.post(
                f"{self.config.api_url}/v1beta/models/{self.config.model_name}:generateContent",
                json=payload,
                headers=headers,
                timeout=self.config.timeout,
                proxies={'http': None, 'https': None}  # 關鍵: 繞過代理
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {"success": True, "content": content}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"success": False, "error": str(e)}


# 模塊級單例
_proxy = GeminiProxy()

def get_ai_proxy() -> GeminiProxy:
    """獲取 AI Proxy 單例"""
    return _proxy
```

---

### 2.5 AsyncIO Event Bus

```python
# src/core/event_bus.py

import asyncio
import logging
from typing import Dict, List, Callable, Awaitable
from .events import Event, EventType

logger = logging.getLogger(__name__)

class EventBus:
    """AsyncIO-based Event Bus"""
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], Awaitable[None]]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
    def subscribe(self, event_type: EventType, callback: Callable[[Event], Awaitable[None]]):
        """訂閱事件 (Callback 必須是 async 函數)"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        
    async def publish(self, event: Event):
        """發布事件"""
        await self._queue.put(event)
        
    async def start(self):
        """啟動事件處理循環"""
        self._running = True
        logger.info("Event Bus Started.")
        
        while self._running:
            try:
                event = await self._queue.get()
                if event.type in self._subscribers:
                    for callback in self._subscribers[event.type]:
                        try:
                            await callback(event)
                        except Exception as e:
                            logger.error(f"Error in subscriber: {e}", exc_info=True)
                self._queue.task_done()
            except asyncio.CancelledError:
                break
                
    def stop(self):
        """停止事件循環"""
        self._running = False
```

---

### 2.6 React + Vite 前端

**package.json**:
```json
{
  "name": "frontend",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "recharts": "^3.6.0",
    "lightweight-charts": "^5.1.0",
    "lucide-react": "^0.562.0"
  },
  "devDependencies": {
    "vite": "^7.2.4",
    "@vitejs/plugin-react": "^5.1.1",
    "eslint": "^9.39.1"
  }
}
```

**vite.config.js**:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    }
  }
})
```

**API 客戶端 (services/api.js)**:
```javascript
const API_BASE = '/api/v1';

export const API = {
    async runBacktest(ticker, strategy = 'momentum', modelVersion = null) {
        const params = new URLSearchParams({ ticker, strategy });
        if (modelVersion) params.append('model_version', modelVersion);
        
        const res = await fetch(`${API_BASE}/backtest?${params}`);
        return res.json();
    },
    
    async getValuation(ticker) {
        const res = await fetch(`${API_BASE}/valuation/${ticker}`);
        return res.json();
    },
    
    async getMacroOverview() {
        const res = await fetch(`${API_BASE}/macro/overview`);
        return res.json();
    },
    
    async generateAI(contextType, data) {
        const res = await fetch(`${API_BASE}/ai/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ context_type: contextType, data })
        });
        return res.json();
    },
    
    async configureAI(url, key, model) {
        const res = await fetch(`${API_BASE}/ai/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_url: url, api_key: key, model_name: model })
        });
        return res.json();
    },
    
    async listModels(modelType) {
        const res = await fetch(`${API_BASE}/models?type=${modelType}`);
        return res.json();
    }
};
```

---

## 3. 啟動腳本 (Start Scripts)

### 3.1 開發模式 (start.sh)

```bash
#!/bin/bash

# 啟動後端
cd /path/to/project
source venv/bin/activate
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# 後台啟動 Flask
python -m src.api.main &
BACKEND_PID=$!
echo $BACKEND_PID > backend_pid.txt

# 啟動前端
cd src/frontend
npm run dev
```

### 3.2 生產模式

```bash
#!/bin/bash

export FLASK_ENV=production
export QUANT_API_KEY="your-secure-key"
export GEMINI_API_KEY="your-gemini-key"

# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 'src.api.main:app'
```

---

## 4. 數據目錄結構 (Data Directory)

```
data/
├── price/           # 價格數據 (JSON)
│   ├── AAPL.json
│   ├── MSFT.json
│   └── ...
├── financials/      # 財務數據 (JSON)
│   ├── AAPL_financials.json
│   └── ...
├── models/          # 訓練好的模型
│   ├── lgbm_model.pkl
│   └── ...
└── cache/           # 臨時緩存
```

---

## 5. 環境變量 (Environment Variables)

| 變量 | 用途 | 默認值 |
|------|------|--------|
| `FLASK_ENV` | Flask 環境 | `development` |
| `QUANT_API_KEY` | API 認證密鑰 | (必須設置) |
| `GEMINI_API_URL` | Gemini API 地址 | `http://127.0.0.1:8045` |
| `GEMINI_API_KEY` | Gemini API 密鑰 | - |
| `GEMINI_MODEL` | Gemini 模型名稱 | `gemini-3-pro-high` |
| `LOG_LEVEL` | 日誌級別 | `INFO` |
| `LOG_FILE` | 日誌文件路徑 | - |
| `TREE_MODEL_PATH` | 樹模型保存路徑 | `temp/ml_models/lgbm_model.pkl` |

---

## 6. 常見問題與解決方案 (Common Issues)

### 6.1 yfinance 限流

**問題**: 大量請求時被 Yahoo Finance 限流

**解決方案**:
```python
# 帶速率限制的更新
def _update_with_rate_limit(self, tickers, delay=1.0):
    for ticker in tickers:
        self._download_single(ticker)
        time.sleep(delay)  # 請求間隔
```

### 6.2 LightGBM 不可用

**問題**: 某些環境無法安裝 LightGBM

**解決方案**: 使用優雅降級
```python
if HAS_LIGHTGBM:
    # 使用 LightGBM
elif HAS_XGBOOST:
    # 使用 XGBoost
else:
    # 使用 sklearn GradientBoosting
```

### 6.3 系統代理干擾 API 調用

**問題**: 本地代理 (如 VPN) 干擾 Gemini API 調用

**解決方案**:
```python
response = requests.post(
    url,
    json=payload,
    proxies={'http': None, 'https': None}  # 繞過代理
)
```

### 6.4 緩存內存溢出

**問題**: DataLoader 緩存無限增長

**解決方案**: 實現有界緩存 (MEM-001 FIX)
```python
MAX_CACHE_SIZE = 50
CACHE_TTL = 3600

def _evict_expired_cache(self):
    # 清理過期和超量緩存
    pass
```
