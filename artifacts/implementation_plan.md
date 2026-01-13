# 實施計畫書: Phase 5 審計修復 (Audit Fixes)

## 🎯 目標 (Goal)
修復由 Auditor 在 Phase 5 驗收測試中發現的兩個嚴重阻擋性問題 (Blockers)：
1.  **CORS 跨域錯誤**: 導致前端無法存取後端 API (`/api/v1/macro/overview`)。
2.  **前端端口硬編碼**: 導致模擬交易頁面嘗試連線錯誤的端口 (`5001` 而非 `666`)。

## ⚠️ 用戶審查 (User Review Required)
> [!IMPORTANT]
> 前端端口將被統一修改為連接 `localhost:666` (或透過環境變量)。請確保本地開發環境後端運行在 666 端口 (由 `start.sh` 控制)。

## 📝 變更計畫 (Proposed Changes)

### 1. 後端 API (Backend)
#### [MODIFY] [src/api/main.py](file:///Users/jerrylee/coding/src/api/main.py)
-   引入 `CORSMiddleware`。
-   配置允許的源 (Allow Origins): `http://localhost:8888`, `http://127.0.0.1:8888`。

### 2. 前端應用 (Frontend)
#### [MODIFY] [src/frontend/src/pages/Simulation.jsx](file:///Users/jerrylee/coding/src/frontend/src/pages/Simulation.jsx) (及其他相關文件)
-   搜索並替換所有硬編碼的 `http://localhost:5001`。
-   替換為相對路徑 `/api` (如果由 Vite 代理) 或統一的後端 URL 常量。
-   *策略*: 搜索全目錄 `src/frontend/src` 查找 `5001`。

## ✅ 驗證計畫 (Verification Plan)

### 自動化測試
1.  **CORS 測試**: 使用 `curl -I -H "Origin: http://localhost:8888" http://localhost:666/api/v1/macro/overview` 檢查 Headers。

### 手動驗證
1.  運行 `./start.sh` 啟動完整堆棧。
2.  打開 `http://localhost:8888`。
3.  **儀表板檢查**: 確認 Macro Overview 數據加載成功（無 CORS 錯誤）。
4.  **模擬交易檢查**: 進入模擬交易頁面，確認狀態請求指向正確端口且成功。
