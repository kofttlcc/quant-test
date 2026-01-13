---
name: algorithmic-execution-engine
description: 管理大額訂單執行，使用 VWAP 與 TWAP 算法最小化市場衝擊成本，並包含反博弈 (Anti-Gaming) 隨機化邏輯。
trigger: when_needed
language: zh-TW
adapted_from: skills/算法執行/quant-execution/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# ALGORITHMIC-EXECUTION-ENGINE 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-execution
> **語言**: 繁體中文

## 概述

模擬並執行機構級的大額訂單算法交易。核心目標是在規定的時間內完成訂單執行，同時將滑點 (Slippage) 和市場衝擊 (Market Impact) 降至最低。此技能包含 VWAP 與 TWAP 兩種核心排程算法，並具備防止被高頻交易識別的反博弈邏輯。

---

## 使用情境

此技能適用於以下情況：
- 執行大於市場流動性 1% 的大額訂單時。
- 需要模擬真實交易環境中的市場衝擊成本回測時。
- 為了隱藏交易意圖，防止訂單被狙擊時。

---

## 數學原理

### 1. VWAP (Volume-Weighted Average Price)
目標是使成交價格接近市場當日的成交量加權平均價。
- **成交量分佈 (Volume Profile)**：使用歷史（如過去 30 天）該資產在每分鐘的平均成交量佔比。
- **動態調整**：實時監控當日成交量。若 $V_{today} > V_{avg}$，則加速執行。

### 2. TWAP (Time-Weighted Average Price)
目標是在時間上均勻執行訂單，適用於成交量分佈不穩定或無法預測的資產。
- **基本邏輯**：$Quantity_{slice} = \frac{TotalQuantity}{TotalTimeSlices}$。

### 3. 反博弈 (Anti-Gaming)
為了防止算法意圖被偵測，必須引入隨機擾動：
$$Qty_t = AvgQty_t + \mathcal{N}(0, \sigma^2)$$

---

## 處理策略指南

1.  **流動性上限檢查**：任何單筆子單 (Child Order) 的成交量不得超過市場近期成交量的 5%-10% (Participation Cap)，以防止流動性枯竭。
2.  **執行排程生成**：
    - 計算歷史成交量分佈曲線。
    - 根據剩餘時間和剩餘數量生成基準排程。
    - 疊加隨機噪音 (Noise) 進行平滑處理。
3.  **風控**：實時監控滑點，若實際執行價格偏離基準價格過大，應暫停執行。

---

## Python 實作範本

```python
import numpy as np
import pandas as pd

class ExecutionAlgo:
    def __init__(self, historical_volume, total_quantity, duration_minutes):
        self.profile = historical_volume / historical_volume.sum() # Normalize
        self.total_qty = total_quantity
        self.duration = duration_minutes
        
    def generate_vwap_schedule(self, current_volume_multiplier=1.0):
        """
        生成 VWAP 執行計劃
        """
        # 根據當日活躍度調整剩餘量並重新歸一化
        adjusted_profile = self.profile * current_volume_multiplier
        schedule = (adjusted_profile / adjusted_profile.sum()) * self.total_qty
        return schedule
        
    def generate_twap_schedule(self, participation_cap=0.05, volatility=0.2):
        """
        生成帶隨機擾動的 TWAP 計劃
        """
        num_slices = self.duration
        base_qty = self.total_qty / num_slices
        
        schedule = []
        for _ in range(num_slices):
            # 引入隨機性: N(base_qty, sigma)
            # volatility 控制隨機波動的幅度
            noise = np.random.normal(0, base_qty * volatility)
            qty = max(1, int(base_qty + noise))
            schedule.append(qty)
            
        return schedule

    def check_anti_gaming(self, order_size, market_volume):
        """
        風控檢查：參與率上限
        """
        limit = market_volume * 0.10 # 硬上限 10%
        if order_size > limit:
            return limit, "Capped by Liquidity"
        return order_size, "OK"
```

## 驗證產出要求

- **預期執行路徑圖**：疊加顯示累積成交量（預測）與實際成交量的對比，驗證執行進度是否符合預期。
- **執行落差報告 (Implementation Shortfall)**：計算執行均價與訂單到達時的基準價格（Arrival Price）之差，以衡量執行績效。

---

## 專案整合

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
