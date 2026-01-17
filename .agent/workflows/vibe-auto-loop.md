---
description: 單模型雙腦自動循環 (Internal Auto Loop)：在一次會話中連續執行 Builder 和 Auditor 的角色切換
---

# Vibe Auto Loop Workflow

此工作流的目的是在 **IDE 內部** 模擬雙腦循環。你將依次扮演 Builder 和 Auditor，直到任務通過審計且**用戶需求全部完成**。

## ⚠️ CRITICAL RULES (最高指令)
1.  **無限循環 (Infinite Loop)**:
    *   循環條件：只要 `task.md` 或 `handoff_notes.md` 中仍有未完成的項目 (`[ ]` 或 `[/]`)，**嚴禁停止**。
    *   **Builder 完成後** -> 必須強制切換到 Phase 2 (Auditor)。
    *   **Auditor 駁回後** -> 必須強制切換回 Phase 1 (Builder)。
    *   **Auditor 批准後** -> 必須檢查「是否還有剩餘需求？」：
        *   若有 -> 強制切換回 Phase 1 (Builder) 繼續開發下一功能。
        *   若無 (全數 `[x]`) -> 才能進入 Phase 3 結束。
2.  **禁止中途退出 (No Early Exit)**:
    *   在滿足上述「全數完成」條件前，**嚴禁**調用 `notify_user`。
    *   嚴禁請求用戶幫助或等待用戶輸入。遇到困難請自我反思或調用 `search_knowledge`。
3.  **角色切換 (Mandatory Switching)**:
    *   必須通過 `task_boundary` 明確宣告角色的切換。
    *   切換時必須 `view_file` 對應的 context 文件。

---

## Phase 1: Builder Execution (扮演 Team A)

1.  **Role Setup**:
    *   Call `view_file("coding/單模型雙腦/contexts/builder.md")`.
    *   Set `task_boundary(TaskName="Builder Phase", TaskStatus="Executing Vibe Build logic")`.

2.  **Execute**:
    *   檢查 `task.md` 或用戶需求清單。
    *   執行規劃、寫代碼、驗證。
    *   遵循 `/vibe-build` 的 SOP。

3.  **Internal Handoff**:
    *   生成 `artifacts/handoff_notes.md`。
    *   **STOP! DO NOT CALL NOTIFY_USER.**
    *   **MANDATORY SWITCH**: 直接進入 Phase 2。

---

## Phase 2: Auditor Verification (扮演 Team B)

1.  **Role Setup**:
    *   Call `view_file("coding/單模型雙腦/contexts/auditor.md")`.
    *   Set `task_boundary(TaskName="Auditor Phase", TaskStatus="Auditing Builder's work")`.

2.  **Audit**:
    *   讀取 `artifacts/handoff_notes.md` 和剛修改的代碼。
    *   遵循 `/vibe-audit` 的 SOP。

3.  **Decision & Loop Control**:
    *   **🔴 REJECTED**:
        *   生成 `artifacts/auditor_handoff.md` (列出錯誤)。
        *   **FORCE SWITCH**: 重新進入 **Phase 1** (Builder 修正錯誤)。
    *   **🟢 APPROVED**:
        *   生成 `artifacts/audit_approval_*.md`。
        *   **Check Remaining Tasks**:
            *   還有未完成項？ -> **FORCE SWITCH**: 重新進入 **Phase 1** (Builder 開發下一功能)。
            *   全部完成？ -> **Proceed to Phase 3**.

---

## Phase 3: Final Completion

1.  **Notification**:
    *   Call `notify_user`。
    *   報告：「任務已完成所有需求的自動循環開發與審計。最終狀態：ALL CLEARED。」
