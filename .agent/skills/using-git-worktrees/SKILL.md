---
name: using-git-worktrees
description: >-
  Use when starting feature work that needs isolation from current workspace or
  before executing implementation plans - creates isolated git worktrees with
  smart directory selection and safety verification
trigger: when_needed
language: zh-TW
adapted_from: openskills/using-git-worktrees
version: 1.0.0-antigravity
original_license: Unknown
---
# USING-GIT-WORKTREES 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/using-git-worktrees  
> **語言**: 繁體中文

## 概述

Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification

---


# Using Git Worktrees

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 概述

Git worktrees create isolated workspaces sharing the same repository, allowing work on multiple branches simultaneously without switching.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Directory Selection Process

Follow this priority order:

### 1. Check Existing Directories

```bash
# Check in priority order
ls -d .worktrees 2>/dev/null     # Preferred (hidden)
ls -d worktrees 2>/dev/null      # Alternative

詳細內容請參閱：[example_3.txt](examples/example_3.txt)


**If preference specified:** Use it without asking.

### 3. Ask User

If no directory exists and no CLAUDE.md preference:


詳細內容請參閱：[example_4.txt](examples/example_4.txt)


## Safety Verification

### For Project-Local Directories (.worktrees or worktrees)

**MUST verify directory is ignored before creating worktree:**

```bash
# Check if directory is ignored (respects local, global, and system gitignore)
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null

詳細內容請參閱：[example_5.txt](examples/example_5.txt)


### 2. Create Worktree


詳細內容請參閱：[script_4.sh](scripts/script_4.sh)


### 3. Run Project Setup

Auto-detect and run appropriate setup:


詳細內容請參閱：[script_5.sh](scripts/script_5.sh)


### 4. Verify Clean Baseline

Run tests to ensure worktree starts clean:

```bash
# 範例 - use project-appropriate command
npm test
cargo test
pytest
go test ./...

詳細內容請參閱：[example_6.txt](examples/example_6.txt)

Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>

詳細內容請參閱：[example_7.txt](examples/example_7.txt)

You: I'm using the using-git-worktrees skill to set up an isolated workspace.

[Check .worktrees/ - exists]
[Verify ignored - git check-ignore confirms .worktrees/ is ignored]
[Create worktree: git worktree add .worktrees/auth -b feature/auth]
[Run npm install]
[Run npm test - 47 passing]

Worktree ready at /Users/jesse/myproject/.worktrees/auth
Tests passing (47 tests, 0 failures)
Ready to implement auth feature
```

## Red Flags

**Never:**
- Create worktree without verifying it's ignored (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking
- Assume directory location when ambiguous
- Skip CLAUDE.md check

**Always:**
- Follow directory priority: existing > CLAUDE.md > ask
- Verify directory is ignored for project-local
- Auto-detect and run project setup
- Verify clean test baseline

## Integration

**Called by:**
- **brainstorming** (Phase 4) - REQUIRED when design is approved and implementation follows
- Any skill needing isolated workspace

**Pairs with:**
- **finishing-a-development-branch** - REQUIRED for cleanup after work complete
- **executing-plans** or **subagent-driven-development** - Work happens in this worktree


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