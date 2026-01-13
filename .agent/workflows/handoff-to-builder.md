---
description: Builder 接收 Auditor 審計反饋並執行下一階段
---

---
description: Builder 接收 Auditor 審計反饋並執行下一階段的強制協議
---

# Builder 接棒協議 (Handoff Protocol)

請以 @builder 身份執行此協議。

## ⚠️ CRITICAL INPUT CHECK (輸入強制驗證)
**在你執行任何代碼或規劃之前，必須先執行此驗證步驟。**

1.  **Scan Artifacts (掃描 Auditor 的產出)**:
    * 目標 A：`artifacts/auditor_handoff.md` (Auditor 的反饋單)
    * 目標 B：`artifacts/audit_approval_*.md` (Auditor 的通行證)

2.  **Verify Status & Lock Path (狀態驗證與路徑鎖定)**:
    * **情況 A (被拒絕/需修正)**:
        * 條件：發現 `auditor_handoff.md` 為最新修改。
        * **Action**: 讀取該文件中的 "Blockers List"。 **(注意：不要去讀 `handoff_notes.md`，那是你自己的筆記)**
        * ➡️ **鎖定路徑**: 進入 **修正模式 (Fix Mode)**。
    * **情況 B (已批准)**:
        * 條件：發現 `audit_approval_*.md` 為最新。
        * **Action**: 讀取該文件中的授權指令。
        * ➡️ **鎖定路徑**: 進入 **執行模式 (Execute Mode)**。
    * **情況 C (無文件)**:
        * 🛑 **HARD STOP**: 嚴禁自行開始工作。
        * 回覆：「錯誤：找不到 Auditor 的審計報告。請檢查 `artifacts/`。」

---

## 執行步驟 (基於鎖定路徑)

### 路徑 A：修正模式 (Fix Mode)
1.  **Fix Blockers**: 針對 `auditor_handoff.md` 的要求進行修改（修改 Plan 或 Code）。
2.  **Update Handoff**: 更新 `artifacts/handoff_notes.md`，說明已修復的項目。
3.  **STOP**: 通知用戶「修正已完成，請重新呼叫 Auditor。」

### 路徑 B：執行模式 (Execute Mode)
1.  **Activate Workflow**: 調用 `/vibe-build` 邏輯。
    * 若是 **Plan Approved**: 進入 `vibe-build` Step 3 (Coding)。
    * 若是 **Code Approved**: 執行合併並準備下一階段規劃 (`vibe-build` Step 1)。
2.  **Deliver**: 更新 `handoff_notes.md` 並通知用戶。