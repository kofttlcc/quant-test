---
description: 呼叫 Auditor 審計 Builder 最新產出物
---

# Auditor 審計指令

請以 @auditor 身份審核 @builder 最新的產出物。

## 執行步驟

// turbo
1. 讀取角色定義 `.agent/roles/auditor.md` 和規則 `.agent/rules/constitution.md`

// turbo
2. 掃描 `artifacts/` 目錄，找到最新的移交物（如 `handoff_notes.md`, `walkthrough*.md`）

// turbo
3. 檢查當前 Git 分支和最新提交內容

4. 對比代碼變更與 `skills/` 技能規範

5. 生成審計報告 `artifacts/audit_approval_[phase].md`，包含：
   - 代碼審計結果（通過/不通過）
   - 技能合規性檢查
   - 語言規範審計（繁體中文）
   - 合併決定

6. 如果批准：提供合併命令
   如果拒絕：列出必須修正項並生成 `artifacts/auditor_handoff.md`

7. 如果@builder 的最新生成或修改的代碼成功通過審計，且無缺陷，則將這部分生成代碼的邏輯和設計思路等相關能力更新到知識庫
   如果審計不通過： 在移交文檔中提出修改建議，並明確指出@builder 的問題，讓其後續避免再次踩坑

## 審計完成後

通知用戶審計結論並提供下一步行動建議。