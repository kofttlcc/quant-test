# Gemini Quant V2 - AI Evolution (AI 進化版)

## 1. 項目背景 (Background)
目前的 v1.1 版本已經建立了穩定的回測與實盤模擬基礎，並引入了初步的 AI 模型（LightGBM/MLP）。然而，當前的 AI 訓練過程是一個「黑盒子」，用戶無法直觀看到訓練進度與性能指標。此外，模型缺乏版本管理，難以比較不同參數的效果。V2 版本的核心目標是將 AI 能力「產品化」與「可視化」。

## 2. 核心目標 (Core Objectives)
1.  **可視化訓練 (Visualized Training)**: 讓用戶在前端實時看到模型訓練的 Loss 曲線與評估指標。
2.  **模型版本控制 (Model Registry)**: 建立模型倉庫，保存不同版本的模型及其參數、回測績效。
3.  **實盤儀表板增強 (Enhanced Dashboard)**: 在模擬交易界面增加 AI 實時預測信號的展示。

## 3. 功能需求 (Functional Requirements)

### 3.1 AI 煉丹爐 (AI Lab)
-   **訓練監控**: 前端展示訓練進度條、實時 Loss / Accuracy 圖表。
-   **參數配置**: 用戶可調整更多超參數（如 Learning Rate, Epochs, Batch Size）。
-   **模型保存**: 訓練完成後，自動保存模型文件與 Metadata (時間、參數、分數) 到 `models/registry`。

### 3.2 模型倉庫 (Model Registry)
-   **列表展示**: 顯示所有歷史訓練模型，支持按性能排序。
-   **一鍵切換**: 用戶可在實盤或回測中選擇特定版本的模型。

### 3.3 實盤信號 (Live Signals)
-   **信號流**: 在 Dashboard 增加「AI 決策流」，顯示 AI 對最新 K 線的預測概率。

## 4. 技術架構變更 (Technical Changes)

### Backend (`src/backend`)
-   **Modify**: `arena.py` - 增加 SocketIO 或輪詢機制推送訓練狀態。
-   **New**: `src/services/model_registry.py` - 管理模型文件的 CRUD。
-   **New**: `src/models/ai_optimizer.py` - 封裝模型訓練邏輯，支持 Callback 回調狀態。

### Frontend (`src/frontend`)
-   **New**: `AILab.tsx` - 訓練與管理界面。
-   **Modify**: `Dashboard.tsx` - 整合 AI 信號組件。

### Data Structure
-   `workspaces/B_Stable_Release/data/model_registry/` (New Directory for model storage)
-   `registry_manifest.json` (Metadata index)

## 5. 風險評估 (Risk Assessment)
-   **兼容性風險**: 新的模型加載機制必須兼容 v1.0 的舊模型文件，或提供遷移腳本。
-   **性能風險**: 訓練過程可能佔用大量 CPU/RAM，需確保不影響 API Server 的響應（考慮異步任務）。
