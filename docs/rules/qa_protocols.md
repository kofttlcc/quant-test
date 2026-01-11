# QA 測試標準操作程序 (SOP) - v2.0

## 1. 效率優化 (Efficiency)
- **縮減停留時間**: 瀏覽器自動化步驟中，減少不必要的 `wait` 時間，提升執行效率。
- **快速反饋循環 (Fast Fail)**:
    - 初次測試失敗 -> 立即停止並報告 (Notify PM) -> 等待修復/安排修復。
    - 修復後 -> **必須** 優先運行 **腳本單元測試** (Script Test/Curl) 進行驗證。
    - 腳本驗證通過 -> **才執行** 瀏覽器端對端驗證 (Browser E2E)。
    - **禁止** 在瀏覽器測試環節中反覆嘗試或卡死 (No Looping)。

## 2. 輸入規範 (Input Discipline)
- **清空後輸入**: 操作輸入框 (Input Field) 時，邏輯必須包含：
    1. Focus Element
    2. Clear / Select All + Delete
    3. Type New Value
    - *目的*: 防止出現 `AAPLNVIDIA` 這類字符疊加錯誤。

## 3. 異常監控 (Error Monitoring)
- **關鍵詞掃描**: 測試過程中主動掃描頁面可見區域 (Viewport) 是否包含：
    - "錯誤"
    - "失敗"
    - "error" (Case insensitive)
    - "failed" (Case insensitive)
- **異常報告**: 
    - 一旦發現上述字符，立即截圖並記錄 DOM 區域。
    - 測試結束後，在報告 (Walkthrough/Notify) 中明確列出所有發現的異常。

---
*生效日期: 2026-01-11*
*適用角色: QA Engineer, Agent*
