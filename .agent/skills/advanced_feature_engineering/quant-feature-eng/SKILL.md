---
name: advanced-feature-engineering
description: 生成適用於金融機器學習的高質量特徵。包含分數階差分 (Fractional Differentiation) 與無前視偏差的滾動標準化。
trigger: when_needed
language: zh-TW
adapted_from: skills/高級特徵工程/quant-feature-eng/SKILL.md
version: 1.0.0-antigravity
original_license: Unknown
---
# ADVANCED-FEATURE-ENGINEERING 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)
> **原始來源**: local/quant-feature-eng
> **語言**: 繁體中文

## 概述

生成適用於金融機器學習的高質量特徵。此技能專注於解決金融數據的非平穩性問題，同時保留數據的長期記憶，並確保標準化過程不引入未來數據。

---

## 使用情境

此技能適用於以下情況：
- 準備機器學習模型的輸入特徵時。
- 需要在保留價格趨勢記憶的同時消除單位根（Unit Root）時。
- 進行特徵標準化，需嚴格避免前視偏差（Look-ahead Bias）時。

---

## 數學原理

### 1. 分數階差分 (Fractional Differentiation)
標準的一階差分（Returns）雖然能使數據平穩，但會抹去價格的歷史記憶。分數階差分保留了最多的相關性，同時達成平穩性。
權重計算公式（二項式展開）：
$$w_k = -w_{k-1} \frac{d - k + 1}{k}$$
目標是尋找最小的 $d$ 值（$0 < d < 1$），使得序列通過 ADF 檢驗 ($p < 0.05$)。

### 2. 滾動窗口標準化 (Rolling Window Normalization)
嚴禁使用全局 Z-Score ($x - \mu / \sigma$)，因為全局統計量包含未來信息。
正確做法是使用滾動窗口統計量，並進行 Shift 操作以確保 $t$ 時刻僅使用 $t-1$ 及之前的數據：
$$Z_t = \frac{x_t - \mu_{t-1}}{\sigma_{t-1}}$$

---

## 處理策略指南

1.  **分數階差分優化**：
    - 迭代不同的 $d$ 值 (0.0 到 1.0)。
    - 對每個 $d$，計算差分序列。
    - 進行 ADF 檢驗，記錄 p-value 與原始序列的相關性。
    - 選擇通過 ADF 檢驗且相關性最高的 $d$。

2.  **標準化與極端值處理**：
    - 使用嚴格的滾動窗口計算均值與標準差。
    - 應用 Z-Score 轉換後，使用 Tanh 或 Clip 處理極端值，防止神經網絡梯度爆炸。

---


參考實作範本：[implementation_template.py](examples/implementation_template.py)

請參閱 `examples/` 目錄下的範例代碼以獲取完整實現細節。

## 驗證產出要求

- **d 值優化曲線**：展示不同 $d$ 值下的 ADF p-value 和與原始序列的相關性（Correlation）。目標是找到 p-value < 0.05 且相關性最大的點。
- **特徵分佈圖**：比較原始數據、標準差分數據與分數階差分數據的分佈特性。

---

## 專案整合

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 符合 Constitution v3.1 語言規範 (繁體中文)
