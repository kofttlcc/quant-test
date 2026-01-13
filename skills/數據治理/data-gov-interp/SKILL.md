name: brownian-bridge-interpolation 
description: 應用布朗橋隨機過程對金融時間序列的缺失值進行插值。用於保持數據的局部波動率結構，防止線性插值導致的方差塌陷。

布朗橋插值技能指令
你是一名隨機微積分專家。當修復 OHLC 價格序列的缺失值時，禁止使用線性插值（除非缺口 < 2 個週期），因為這會人為降低波動率，導致 VaR 低估 。

1. 算法邏輯
對於已知端點 $P_{start}$ (時間 $t_0$) 和 $P_{end}$ (時間 $T$) 的缺口，插值 $P_t$ 由以下公式生成:
$$P_t = \underbrace{P_{start} + (P_{end}-P_{start})\frac{t-t_0}{T-t_0}}_{\text{線性漂移}} + \underbrace{\mathcal{N}\left(0, \sigma^2 \frac{(t-t_0)(T-t)}{T-t_0}\right)}_{\text{隨機擾動}}$$
波動率 $\sigma$： 必須使用缺口前後最近 20 個數據點的滾動標準差估計，不可使用全局波動率。

2. 執行步驟
- 識別數據中的連續 NaN 區間。
- 計算局部波動率 $\sigma_{local}$。
- 生成布朗橋路徑填充缺口。
- 種子控制： 必須允許傳入 random_state 以確保回測可重現性。

3. Python 實作範本
python
import numpy as np

def brownian_bridge(start_val, end_val, n_steps, sigma): dt = 1.0 / (n_steps + 1) t = np.linspace(dt, 1.0 - dt, n_steps)

# 線性部分
drift = start_val + (end_val - start_val) * t

# 隨機部分 (橋的方差結構)
bridge_var = (t * (1 - t))
noise = np.random.normal(0, sigma * np.sqrt(bridge_var))

return drift + noise