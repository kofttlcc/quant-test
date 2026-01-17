---
name: quant-ml-purged-cv-integration
description: 將 Purged CV 整合到 ML 訓練流程的標準模式
---

# Purged CV 整合模式 (ML Training Integration)

## 適用場景
當在金融時間序列上訓練 ML 模型時，必須使用 Purged CV 而非標準 K-Fold，以防止數據洩露。

## 核心原則

> ⚠️ **禁止** 在金融序列上使用 `sklearn.model_selection.KFold`。
> 標準 K-Fold 會導致訓練集和測試集在時間上重疊，造成過擬合幻覺。

## 標準整合模式


> [!TIP]
> 已提取代碼至：[quant-ml-purged-cv-integration_examples_1.py](examples/quant-ml-purged-cv-integration_examples_1.py)

## 關鍵參數

| 參數 | 說明 | 建議值 |
|------|------|--------|
| `purge_window` | 測試集之前剔除的樣本數 | 標籤前視長度 (如 5 天) |
| `embargo_window` | 測試集之後剔除的樣本數 | 序列相關性半衰期 |
| `n_test_splits` | 測試集組數 | 1-2 (增加路徑多樣性) |

## 進化來源
- **Phase 3**: 實作 `CombinatorialPurgedKFold` 並整合至 MLP
- **Auditor 審計**: 確認 Purge/Embargo 機制正確隔離 Train/Val
