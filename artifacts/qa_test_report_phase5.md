# QA 測試報告：Phase 5 驗收測試

**測試員**: @qa  
**日期**: 2026-01-13  
**測試環境**: `start.sh` 啟動，前端 :8888，後端 :666

---

## 測試結論：❌ **FAIL** - 退回 @builder 修復

---

## 測試結果摘要

| 功能模塊 | 狀態 | 問題描述 |
|----------|------|----------|
| 宏觀風險儀表板 | ❌ FAIL | CORS 跨域阻擋，紅條「宏觀數據載入失敗」 |
| AI 對抗競技場 | ❌ FAIL | CORS 跨域阻擋，點擊「開始對戰」無反應 |
| AI 實驗室 | ✅ PASS | 訓練配置、Model Registry 正常，可成功訓練模型 |
| 模擬交易 | ❌ FAIL | 硬編碼端口 5001，`net::ERR_CONNECTION_REFUSED` |

---

## 發現的錯誤 (Console Errors)

### 1. CORS 跨域阻擋 (Critical)
```
Access to fetch at 'http://127.0.0.1:666/api/v1/macro/overview' 
from origin 'http://localhost:8888' has been blocked by CORS policy
```
**影響範圍**:
- `/api/v1/macro/overview` (宏觀儀表板)
- `/api/v1/arena/adversarial` (AI 對抗競技場)

**根因分析**: 後端 API 未正確設置 CORS Header 允許 `localhost:8888` 跨域請求。

### 2. 端口硬編碼錯誤 (Critical)
```
GET http://localhost:5001/api/v1/simulation/status net::ERR_CONNECTION_REFUSED
```
**影響範圍**: `SimulationDashboard.jsx` (模擬交易頁面)

**根因分析**: 前端組件仍使用舊端口 5001，未統一為 666。

---

## 必須修復項 (Blockers for Merge)

> [!CAUTION]
> 以下問題必須在合併前解決

### 修復項 1：後端 CORS 配置
- **文件**: `src/api/main.py`
- **操作**: 確保 `CORSMiddleware` 允許 `http://localhost:8888` 和 `http://127.0.0.1:8888`

### 修復項 2：前端端口統一
- **文件**: `src/frontend/src/components/SimulationDashboard.jsx` (或類似)
- **操作**: 將所有 `localhost:5001` 替換為 `localhost:666`

---

## 測試截圖

### 儀表板錯誤狀態
![Dashboard Error](file:///Users/jerrylee/.gemini/antigravity/brain/ecb88d0d-1803-4b1b-98ed-5e0669858cdd/.system_generated/click_feedback/click_feedback_1768304351532.png)

### AI 實驗室正常狀態
![AI Lab OK](file:///Users/jerrylee/.gemini/antigravity/brain/ecb88d0d-1803-4b1b-98ed-5e0669858cdd/.system_generated/click_feedback/click_feedback_1768304381873.png)

---

## 測試錄影
![QA Test Recording](file:///Users/jerrylee/.gemini/antigravity/brain/ecb88d0d-1803-4b1b-98ed-5e0669858cdd/qa_full_test_1768304327554.webp)

---

**簽章**: *QA (Auditor)* | 2026-01-13T19:40:00+08:00
