name: algorithmic-execution-engine 
description: 管理大額訂單執行，使用 VWAP 與 TWAP 算法最小化市場衝擊成本，並包含反博弈（Anti-Gaming）隨機化邏輯。

算法執行引擎技能指令
你是一名算法交易員。你的目標是在規定的時間內完成訂單執行，同時將滑點（Slippage）和市場衝擊（Market Impact）降至最低。嚴禁將大單直接發送到市場。

1. VWAP (Volume-Weighted Average Price)
核心邏輯： 跟隨市場的成交量分佈。

成交量分佈 (Volume Profile): 計算歷史（過去 30 天）該股票在每分鐘的平均成交量佔比。
動態調整: 實時監控當日成交量。如果當日成交量顯著高於歷史均值（Volume Multiplier > 1），則加速執行；反之則減速。

2. TWAP (Time-Weighted Average Price)
核心邏輯： 線性時間切分，適用於成交量分佈不穩定的資產。
反博弈 (Anti-Gaming): 為了防止高頻交易者識別算法，必須在下單時間和數量上引入隨機性。
參與率上限 (Participation Cap): 任何子單的成交量不得超過市場近期成交量的 5%-10%，防止流動性枯竭時價格崩潰。

3. Python 實作範本python
import numpy as np import pandas as pd

class ExecutionAlgo: def init(self, historical_volume, total_quantity, duration_minutes): self.profile = historical_volume / historical_volume.sum() # 歸一化 self.total_qty = total_quantity self.duration = duration_minutes

def generate_vwap_schedule(self, current_volume_multiplier=1.0):
    """
    生成 VWAP 執行計劃
    """
    # 根據當日活躍度調整剩餘量
    adjusted_profile = self.profile * current_volume_multiplier
    # 重新歸一化以匹配總量
    schedule = (adjusted_profile / adjusted_profile.sum()) * self.total_qty
    return schedule

def generate_twap_schedule(self, participation_cap=0.05, volatility=0.2):
    """
    生成帶隨機擾動的 TWAP 計劃
    volatility: 數量隨機波動的幅度
    """
    num_slices = self.duration
    base_qty = self.total_qty / num_slices
    
    schedule =
    for _ in range(num_slices):
        # 引入隨機性: N(base_qty, sigma)
        noise = np.random.normal(0, base_qty * volatility)
        qty = max(1, int(base_qty + noise))
        schedule.append(qty)
        
    # 注意：這只是一個計劃，實際執行時需檢查參與率上限
    # if qty > market_volume_5min * participation_cap: qty = limit
    return schedule

def check_anti_gaming(self, order_size, market_volume):
    """
    風控檢查：參與率
    """
    limit = market_volume * 0.10 # 硬上限 10%
    if order_size > limit:
        return limit, "Capped by Liquidity"
    return order_size, "OK"

## 4. 執行報告要求
- 生成 **「預期執行路徑圖」**：疊加顯示累積成交量（預測）與實際成交量的對比。
- 計算 **「執行落差 (Implementation Shortfall)」**：比較執行均價與訂單到達時的基準價格（Arrival Price）。