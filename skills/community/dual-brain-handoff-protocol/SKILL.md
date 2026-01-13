---
name: dual-brain-handoff-protocol
description: Builder/Auditor 雙腦協議的標準交接流程
---

# 雙腦協議交接流程 (Handoff Protocol)

## 適用場景
當 Builder (Team A) 和 Auditor (Team B) 進行代碼交接時，確保資訊完整傳遞且符合品質標準。

## Builder → Auditor 交接清單

### 必備產出物
1. **`handoff_notes.md`** - 移交筆記
   - What was built
   - Shortcuts taken
   - Uncertainties
   
2. **`walkthrough_phase[N].md`** - 階段總結報告
   - 關鍵升級說明
   - 驗證結果
   - 下一步建議

3. **Git 分支**
   - 命名規範: `feat/phase[N]-[name]` 或 `fix/[issue]-[desc]`
   - 每個 commit 職責單一

### 語言規範
- 所有產出物必須使用**繁體中文**
- 技術術語可保留英文 (如 `VaR`, `MAD`, `Arena`)

## Auditor → Builder 移交清單

### 審計通過
1. **`audit_approval_[phase].md`** - 審計批准報告
2. 合併命令
3. 下一階段建議

### 審計拒絕
1. **`auditor_handoff.md`** - 修正指令
   - 阻塞項 (Blocking)
   - 建議項 (Non-Blocking)

## 快捷指令
- `/handoff-to-auditor` - Builder 完成後呼叫
- `/handoff-to-builder` - Auditor 審計後呼叫
- `/dual-brain-status` - 查看進度

## 進化來源
- **本次迭代**: 成功完成 4 階段無阻塞交接
- **Auditor 審計**: 標準化流程提升協作效率
