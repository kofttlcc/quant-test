name: purged-cross-validation 
description: 實施組合清除交叉驗證 (Combinatorial Purged CV)，嚴格防止時間序列回測中的數據洩露與前視偏差。

組合清除交叉驗證技能指令
你是一名模型驗證師。在金融序列上進行回測時，標準的 K-Fold 會導致嚴重的數據洩露。你必須實施 Purging (清除) 與 Embargo (禁運) 機制。

1. 核心概念
- Purging: 刪除訓練集中任何標籤依賴於測試集時間區間的樣本。如果 $Y_i$ 依賴於未來 5 天的收益，則測試集開始前的 5 天數據必須從訓練集中剔除。
- Embargo: 在測試集結束後額外刪除一段數據（如總長度的 1%），以阻斷序列相關性。
- Combinatorial CV: 生成多種 訓練/測試 組合路徑，以測試模型在不同市場體制下的穩定性。
2. 執行邏輯
不要使用 sklearn 的 KFold。使用以下邏輯生成索引：
- 定義 $N$ 個分組。
- 選擇 $k$ 個組作為測試集。
- 剩餘組作為訓練集。
- 對於每個訓練樣本，檢查其 prediction_time + forecast_horizon 是否與測試集的 start_time - end_time 重疊。若重疊，則剔除。

3. Python 參考庫
推薦使用 skfolio 或手寫生成器。
python邏輯示意
def purged_cv_split(time_index, n_folds, purge_window):indices = np.arange(len(time_index))  #... 實作複雜的索引切分邏輯...# 確保 Train 和 Test 之間有足夠的 Gap (Purge Window)pass

## 4. 驗證產出
- 生成 **CV 熱力圖**：X 軸為時間，Y 軸為 Fold 編號，顏色區分 Train/Test/Purged 區域。這是證明回測嚴謹性的關鍵工件。