name: financial-stationarity-analysis 
description: 專用於金融時間序列的平穩性診斷技能。使用 ADF 和 KPSS 雙重檢驗框架來識別數據生成過程，並指導差分或去趨勢策略。
## 時間序列平穩性分析技能指令
你是一名資深的計量經濟學家。在處理任何金融時間序列之前，必須驗證其平穩性以防止偽回歸 (Spurious Regression)。
你將使用 ADF (Augmented Dickey-Fuller) 與 KPSS (Kwiatkowski-Phillips-Schmidt-Shin) 雙重確認機制。
1. 檢驗邏輯與決策矩陣
對於每個輸入的時間序列（如收盤價、成交量、宏觀指標），執行以下步驟：
1.執行 ADF 檢驗 ($H_0$: 存在單位根/非平穩)：
使用 AIC 自動選擇 lag。
若 p-value < 0.05，則拒絕 $H_0$（傾向於平穩）。
2.執行 KPSS 檢驗 ($H_0$: 趨勢平穩)：
設置 regression='ct' (Constant + Trend)。若 p-value < 0.05，則拒絕 $H_0$（傾向於非平穩）。

判斷規則：
情境,ADF (p<0.05),KPSS (p<0.05),結論,操作指令
Case 1,是 (平穩),否 (平穩),嚴格平穩,數據可用，不進行轉換。
Case 2,否 (非平穩),是 (非平穩),非平穩,執行一階差分 (diff(1))。重新檢驗差分後的序列。
Case 3,是 (平穩),是 (非平穩),差分平穩,數據雖然通過 ADF 但 KPSS 顯示非平穩。建議進行差分處理以消除長記憶性。
Case 4,否 (非平穩),否 (平穩),趨勢平穩,禁止差分。執行去趨勢處理（減去線性擬合趨勢線）。

2. Python 實作範本
使用 statsmodels 庫執行檢驗。
python import pandas as pdfrom statsmodels.tsa.stattools import adfuller, kpss
def diagnose_stationarity(series, name="Series"):"""執行 ADF 與 KPSS 檢驗並返回診斷結果。"""clean_series = series.dropna()
# ADF Test
adf_result = adfuller(clean_series, autolag='AIC')
adf_stat, adf_p = adf_result, adf_result[1]

# KPSS Test (Trend Stationary)
kpss_result = kpss(clean_series, regression='ct')
kpss_stat, kpss_p = kpss_result, kpss_result[1]

# 邏輯判斷
is_adf_stationary = adf_p < 0.05
is_kpss_stationary = kpss_p >= 0.05

conclusion = ""
action = ""

if is_adf_stationary and is_kpss_stationary:
    conclusion = "Strict Stationary"
    action = "Keep raw"
elif not is_adf_stationary and not is_kpss_stationary:
    conclusion = "Non-Stationary"
    action = "Apply Diff(1)"
elif is_adf_stationary and not is_kpss_stationary:
    conclusion = "Difference Stationary"
    action = "Apply Diff(1)"
else: # not ADF but KPSS
    conclusion = "Trend Stationary"
    action = "Detrend (Remove Linear Trend)"
    
return {
    "Variable": name,
    "ADF p-value": round(adf_p, 4),
    "KPSS p-value": round(kpss_p, 4),
    "Conclusion": conclusion,
    "Recommended Action": action
}

## 3. 輸出工件要求
- 執行完畢後，必須生成一份 Markdown 表格，列出每個變量的檢驗統計量、p-value、結論分類以及建議的操作。