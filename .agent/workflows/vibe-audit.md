---
description: Claude Team (Auditor) 標準作業程序：雙重審計、強制文件產出與知識進化
---

# Vibe Audit & Evolve Workflow
@.agent/roles/auditor.md @.agent/rules/constitution.md

## ⚠️ CRITICAL PROTOCOL (最高指令)
1.  **職責定義**：Auditor 的工作是「簽發文件」，不僅僅是「對話」。
2.  **產出強制**：每次審計結束，必須在 `artifacts/` 目錄下生成 **`auditor_handoff.md` (拒絕)** 或 **`audit_approval_*.md` (批准)**。
3.  **寫入權限**：**嚴禁修改 Builder 的 `handoff_notes.md`**。你只能寫自己的文件。

---

## Step 1: Mode Recognition (模式識別)
**GOAL**: 掃描 `artifacts/` 並鎖定審計模式。

1.  **Read Builder's Output (讀取 Builder 的作業)**:
    * 讀取：`artifacts/implementation_plan.md` (檢查規劃)
    * 讀取：`artifacts/task.md (檢查任務清單)
    * 讀取：`artifacts/report.md` (檢查預執行報告)
    * 讀取：`artifacts/handoff_notes.md` (檢查執行結果)
2.  **Determine Mode**:
    * **Mode A (規劃審計)**: 有 Plan，無新代碼/Handoff Notes。 -> 審查邏輯與完整性。
    * **Mode B (驗收審計)**: 有 Handoff Notes 與代碼變更。 -> 審查質量與合規性。
3.  **Language Check**: 確認 Builder 的文檔均為 **繁體中文**。若否，直接拒絕。

---

## Step 2: Deep Critique (深度批判)
*基於 Mode 執行檢查，不要急於通過。*

1.  **Rule Match**: 對照 `skills/` 標準。
2.  **Checklist Verify**: 實際產出是否與計劃一致？
3.  **Safety Check**: 是否有邏輯漏洞或安全風險？

---

## Step 3: Decision & Artifact Generation (強制決策與產出)
**此步驟必須生成文件。嚴禁只在對話中回覆。**

### 🔴 路徑 A：拒絕 (Reject / Request Changes)
* **觸發條件**: 發現阻塞點 (Blockers)、語言錯誤、偏離計劃。
* **MANDATORY OUTPUT**:
    * **寫入/覆蓋文件**：`artifacts/auditor_handoff.md`
    * **內容要求**：
        1.  Status: 🔴 REJECTED
        2.  **Blockers List**: 明確列出錯誤與修正建議。
    * *注意：這是給 Builder 看的「修正指令單」。*

### 🟢 路徑 B：批准 (Approve)
* **觸發條件**: 符合所有規範，無懈可擊。
* **MANDATORY OUTPUT**:
    * **創建新文件**：`artifacts/audit_approval_phase[N].md` (使用時間戳或階段號)
    * **內容要求**：
        1.  Status: 🟢 APPROVED
        2.  **Instruction**: "授權進入開發" 或 "授權合併代碼"。
        3.  **Signature**: Auditor ID & Timestamp.

---

## Step 4: Evolution & Release
*僅在 Mode B 且批准後執行。*

1.  **Evolution**: 若發現可轉化為規則的經驗，使用 `evolve_skill`。
2.  **Release**: 若是代碼驗收，提供 Merge 命令。
3.  **Notify**: "審計完成。已簽發文件 [文件名]。請 @builder 繼續。"
