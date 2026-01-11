# V2 開發意向清單 (Development Checklist)

## Phase 1: 基礎設施與後端 (Infrastructure & Backend)

- [ ] **模型註冊表服務 (Model Registry Service)**
    - [ ] 創建 `src/services/model_registry.py`。
    - [ ] 實現 `save_model_version(model, metadata)`。
    - [ ] 實現 `list_models()` 與 `load_model_version(version_id)`。
    - [ ] 確保文件存儲路徑為 `data/model_registry/`。

- [ ] **AI 訓練優化器 (AI Optimizer Enhancements)**
    - [ ] Refactor `src/backend/arena.py` 以支持異步訓練任務。
    - [ ] 實現訓練過程中的狀態回調 (Callback)，將 Loss/Progress 寫入臨時狀態文件或內存變量供 API 查詢。
    - [ ] 增加 API 端點 `/api/ai/train_status` 以獲取實時進度。
    - [ ] 增加 API 端點 `/api/ai/models` (GET/POST/DELETE)。

## Phase 2: 前端開發 (Frontend Development)

- [ ] **AI 實驗室頁面 (AI Lab Page)**
    - [ ] 新增路由 `/ai-lab`。
    - [ ] 實現「新建訓練任務」表單 (選擇模型類型、參數)。
    - [ ] 實現「訓練監控面板」 (Progress Bar + Loss Chart using Recharts)。
    - [ ] 實現「模型列表」表格，展示歷史版本與績效。

- [ ] **儀表板集成 (Dashboard Integration)**
    - [ ] 在 `Dashboard.tsx` 中增加 `AISignalWidget`。
    - [ ] 連接後端 `/api/ai/inference` (需確認或新增此接口) 獲取最新預測。

## Phase 3: 驗證與回歸 (Verification & Regression)

- [ ] **單元測試 (Unit Tests)**
    - [ ] 測試 `ModelRegistry` 的保存與讀取功能。
    - [ ] 測試 `Arena` 訓練流程是否會阻塞主線程。

- [ ] **集成測試 (Integration Tests)**
    - [ ] 完整流程：配置 -> 訓練 -> 保存 -> 在回測中使用該模型。

- [ ] **回歸測試 (Regression Test)**
    - [ ] 運行 `tests/test_legacy_features.py` (需創建或運行現有測試)。
    - [ ] 確保 v1.1 的基礎回測功能不受影響。
    - [ ] 確保 `start.sh` 依然能一鍵啟動系統。
