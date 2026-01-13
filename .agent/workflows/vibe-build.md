---
description: Gemini Team (Builder) 標準作業程序：從需求分析、規劃、審計通過到代碼實現的全流程控制
---

---
description: Team A (Builder) 標準作業程序：需求規劃、審計閘門控制、代碼實現與交付全流程
---

# Vibe Build Workflow
@.agent/roles/builder.md @.agent/rules/constitution.md

## ⚠️ CRITICAL PROTOCOL (最高指令)
1.  **順序鎖定**：必須嚴格遵循 Step 1 -> Step 2 -> Step 3 的順序。**嚴禁跳過 Step 2 直接寫代碼。**
2.  **語言規範**：所有產出文檔（計劃、報告、註釋、Commit）強制使用 **繁體中文**。
3.  **輸入源鎖定**：Step 2 必須讀取 Auditor 的 `auditor_handoff.md` 或 `audit_approval_*.md`，嚴禁讀取自己的 `handoff_notes.md` 作為指令來源。

---

## Step 1: Context & Planning (情境加載與規劃)
**GOAL**: 僅生成規劃文檔，**絕不生成功能代碼**。

1.  **Read Constraints**: 讀取 `.agent/rules/constitution.md` 確認邊界。
2.  **Pattern Search**: 使用 `search_knowledge` 查詢 `skills/` 中的現有模式。
3.  **Generate Deliverables (強制產出 - 繁體中文)**:
    * 在聊天視窗中輸出並寫入文件（如果需要）：
        1.  **實施計劃書 (Implementation Plan)**: `artifacts/implementation_plan.md`
        2.  **任務執行清單 (Task Checklist)**: 原子化的步驟列表。
        3.  **預執行報告 (Pre-implementation Report)**: 風險評估。
4.  **STOP & ASK**:
    * 輸出完上述文檔後，**強制停止**。
    * 通知用戶：「**Step 1 規劃完成。請呼叫 @auditor 進行審計。在獲得 '審計核准報告' 前，我將處於待機狀態。**」
    * **DO NOT PROCEED TO STEP 2.** (嚴禁自行進入 Step 2)

---

## Step 2: Audit Gate (審計閘門) // HARD STOP
**CONDITION**: 檢查 `artifacts/` 目錄下 **Auditor 的產出物**。

1.  **Check for Rejection (檢查拒絕)**:
    * 讀取文件：`artifacts/auditor_handoff.md`
    * 邏輯：若文件存在且最新，且內容含 "🔴 REJECTED" 或 "Blockers"，則**返回 Step 1** 進行修正。
    * *注意：這是 Auditor 給你的修正指令。*

2.  **Check for Approval (檢查批准)**:
    * 讀取文件：`artifacts/audit_approval_phase[N].md`
    * 邏輯：若文件存在且包含 "🟢 APPROVED"，則**解鎖 Step 3**。

3.  **Wait (等待)**:
    * 若上述兩文件均無更新，保持等待。拒絕執行任何代碼編寫請求。
    * 回覆：「我需要 Auditor 的核准文件 (`audit_approval_*.md`) 才能繼續。」

---

## Step 3: Vibe Coding (構建與實作)
*前提：已通過 Step 2 且獲得 `audit_approval` 文件。*

1.  **Branching**: `git checkout -b feat/phase[N]-[name]`
2.  **Coding**:
    * 嚴格按照 Step 1 的 `Task Checklist` 執行。
    * **實時更新**：每完成一個小項，更新 `artifacts/iteration_plan.md` (若存在) 或清單狀態。
3.  **Verify**: 運行測試或創建 `verify.py` 驗證腳本。

---

## Step 4: Handoff & Reporting (交付與移交)
1.  **Generate Artifacts (強制產出 - 繁體中文)**:
    * **寫入/更新**：`artifacts/handoff_notes.md` (這是你寫給 Auditor 看的移交筆記)。
    * **內容必須包含**：
        * 引用 `audit_approval_*.md` 的 ID (證明是合法執行的)。
        * 本階段完成的功能列表。
        * 技術捷徑與潛在風險。
    * **生成**：`artifacts/walkthrough_phase[N].md` (功能演示)。

2.  **Commit**: `git commit -am "feat: phase[N] implementation [audit-verified]"`

3.  **Final Stop**: 通知用戶：「Build complete. 交付物已生成 (`handoff_notes.md`)。請呼叫 @auditor 驗收。」