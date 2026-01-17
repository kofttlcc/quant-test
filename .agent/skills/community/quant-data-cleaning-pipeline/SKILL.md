---
name: quant-data-cleaning-pipeline
description: 金融時間序列數據清洗的標準流程，整合 MAD 檢測與布朗橋插值
---

# 金融數據清洗管道 (Data Cleaning Pipeline)

## 適用場景
當處理金融 OHLCV 數據時，需要同時處理異常值和缺失值，且必須保持時間序列的統計特性。

## 核心原則

> ⚠️ **禁止** 使用 `ffill().bfill()` 或 `interpolate(method='linear')` 處理金融數據。
> 這會人為降低波動率，導致 VaR 低估和風險模型失效。

## 標準流程


> [!TIP]
> 已提取代碼至：[quant-data-cleaning-pipeline_examples_1.txt](examples/quant-data-cleaning-pipeline_examples_1.txt)

## Python 範本


> [!TIP]
> 已提取代碼至：[quant-data-cleaning-pipeline_examples_2.py](examples/quant-data-cleaning-pipeline_examples_2.py)

## 進化來源
- **Phase 0**: 發現 `DataLoader` 使用 `ffill/bfill` 掩蓋數據缺口
- **Phase 1**: 實作 MAD 替代固定閾值
- **Auditor 審計**: 確認此流程有效保持局部波動率結構
