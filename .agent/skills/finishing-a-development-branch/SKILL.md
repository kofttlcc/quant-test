---
name: finishing-a-development-branch
description: >-
  Use when implementation is complete, all tests pass, and you need to decide
  how to integrate the work - guides completion of development work by
  presenting structured options for merge, PR, or cleanup
trigger: when_needed
language: zh-TW
adapted_from: openskills/finishing-a-development-branch
version: 1.0.0-antigravity
original_license: Unknown
---
# FINISHING-A-DEVELOPMENT-BRANCH 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/finishing-a-development-branch  
> **語言**: 繁體中文

## 概述

Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup

---


# Finishing a Development Branch

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 概述

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed with merge/PR until tests pass.

詳細內容請參閱：[example_4.txt](examples/example_4.txt)


Or ask: "This branch split from main - is that correct?"

### Step 3: Present Options

Present exactly these 4 options:


詳細內容請參閱：[example_5.txt](examples/example_5.txt)


**Don't add explanation** - keep options concise.

### Step 4: Execute Choice

#### Option 1: Merge Locally


詳細內容請參閱：[script_3.sh](scripts/script_3.sh)


Then: Cleanup worktree (Step 5)

#### Option 2: Push and Create PR


詳細內容請參閱：[script_4.sh](scripts/script_4.sh)


Then: Cleanup worktree (Step 5)

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**

詳細內容請參閱：[example_6.txt](examples/example_6.txt)


Wait for exact confirmation.

If confirmed:
```bash
git checkout <base-branch>
git branch -D <feature-branch>

詳細內容請參閱：[example_7.txt](examples/example_7.txt)


If yes:
```bash
git worktree remove <worktree-path>
```

**For Option 3:** Keep worktree.

## 快速參考

| Option | Merge | Push | Keep Worktree | Cleanup Branch |
|--------|-------|------|---------------|----------------|
| 1. Merge locally | ✓ | - | - | ✓ |
| 2. Create PR | - | ✓ | ✓ | - |
| 3. Keep as-is | - | - | ✓ | - |
| 4. Discard | - | - | - | ✓ (force) |

## Common Mistakes

**Skipping test verification**
- **Problem:** Merge broken code, create failing PR
- **Fix:** Always verify tests before offering options

**Open-ended questions**
- **Problem:** "What should I do next?" → ambiguous
- **Fix:** Present exactly 4 structured options

**Automatic worktree cleanup**
- **Problem:** Remove worktree when might need it (Option 2, 3)
- **Fix:** Only cleanup for Options 1 and 4

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Force-push without explicit request

**Always:**
- Verify tests before offering options
- Present exactly 4 options
- Get typed confirmation for Option 4
- Clean up worktree for Options 1 & 4 only

## Integration

**Called by:**
- **subagent-driven-development** (Step 7) - After all tasks complete
- **executing-plans** (Step 5) - After all batches complete

**Pairs with:**
- **using-git-worktrees** - Cleans up worktree created by that skill


---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 與 `skills/_base/architecture.md` 架構模式一致
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

可搭配以下技能使用：
- `systematic-debugging` - 系統化除錯
- `verification-before-completion` - 完成前驗證