---
description: Builder 接收 Auditor 審計反饋並執行下一階段
---

# Builder 接棒指令

請以 @builder 身份接收 @auditor 的審計結果並執行下一階段工作。

## 執行步驟

// turbo
1. 讀取角色定義 `.agent/roles/builder.md` 和規則 `.agent/rules/constitution.md`

// turbo
2. 讀取 Auditor 移交物：
   - `artifacts/auditor_handoff.md`（如有修正要求）
   - `artifacts/audit_approval_*.md`（審計批准報告）
   - `artifacts/iteration_plan.md`（迭代計劃）

3. 如果有**拒絕/待修正項**：
   - 執行所有阻塞項修正
   - 更新相關產出物
   - 更新 `handoff_notes.md`
   - 提交變更後通知用戶呼叫 @auditor 重審

4. 如果**已批准**：
   // turbo
   - 執行合併命令（從審計報告中取得）
   - 創建下一階段分支：`git checkout -b feat/phase[N]-[name]`
   - 開始執行 `iteration_plan.md` 中的下一階段任務

5. 完成階段工作後：
   - 生成 `artifacts/walkthrough_phase[N].md`
   - 更新 `artifacts/handoff_notes.md`
   - 更新 `iteration_plan.md` 標記完成項 `[x]`
   - 提交所有變更

## 執行完成後

通知用戶：「Build complete. 請呼叫 /handoff-to-auditor 進行審計。」
