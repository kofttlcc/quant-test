# 單模型雙腦自動化方案 (Single Model Dual Brain Automation)

## 1. 核心變更
將原定的「雙模型」架構簡化為 **單模型 (Gemini 3 Pro)**，但保留 **雙腦 (Dual Brain)** 的邏輯隔離。
*   **物理層**: 統一使用 `gemini-cli` 調用 `gemini-3-pro` 模型。
*   **邏輯層**: 通過 `gemini-cli` 的 **Context (Session)** 功能來隔離兩個角色：
    *   Context A: `builder_session` (負責執行 `/vibe-build`)
    *   Context B: `auditor_session` (負責執行 `/vibe-audit`)

## 2. 目錄結構
所有相關配置與腳本將存放在 `single_model_dual_brain/` 目錄下：
```
single_model_dual_brain/
├── design.md              // 本設計文檔
├── auto_loop_driver.py    // 自動化驅動腳本 (Python)
├── gemini_settings.json   // 建議的 gemini-cli 配置 (參考)
└── usage_guide.md         // 使用說明
```

## 3. 自動化流程 (The Loop)

### 初始化
*   腳本啟動，檢查 `artifacts/` 目錄。
*   設定初始狀態：`Current Role: Builder`。

### 階段 A: Builder (Gemini 3 Pro)
1.  **指令**: 調用 `gemini -p "/vibe-build" --context builder_session --output-format json`。
2.  **行為**:
    *   讀取 Auditor 的反饋 (如有)。
    *   執行規劃與代碼生成的思考。
    *   **產出**: `artifacts/handoff_notes.md`。
3.  **監控**: 驅動腳本輪詢文件系統，一旦發現 `handoff_notes.md` 更新，立即鎖定 Builder，切換至 Auditor。

### 階段 B: Auditor (Gemini 3 Pro)
1.  **指令**: 調用 `gemini -p "/vibe-audit" --context auditor_session --output-format json`。
2.  **行為**:
    *   讀取 Builder 的 Handoff。
    *   執行審計邏輯 (讀取代碼、檢查規範)。
    *   **產出**: `artifacts/audit_approval_*.md` (通過) 或 `artifacts/auditor_handoff.md` (拒絕)。
3.  **監控**: 驅動腳本輪詢文件系統，發現產出後，切換回 Builder。

## 4. 關鍵配置
*   **Model Name**: `gemini-3-pro` (需確認用戶環境的實際 Model ID，腳本中將設為變量方便修改)。
*   **MCP**: 兩個 Context 共享 `~/.gemini/settings.json` 中的 MCP 工具，確保能讀寫同一個文件系統。

## 5. 優勢
*   **成本效益**: 單一模型訂閱。
*   **上下文隔離**: 通過 CLI 的 Context 機制，避免了 Builder 和 Auditor 的短期記憶混淆，真正實現「左手畫圓，右手畫方」的互搏效果。
