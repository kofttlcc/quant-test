---
name: test-driven-development
description: >-
  Use when implementing any feature or bugfix, before writing implementation
  code
trigger: when_needed
language: zh-TW
adapted_from: openskills/test-driven-development
version: 1.0.0-antigravity
original_license: Unknown
---
# TEST-DRIVEN-DEVELOPMENT 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/test-driven-development  
> **語言**: 繁體中文

## 概述

Use when implementing any feature or bugfix, before writing implementation code

---


# Test-Driven Development (TDD)

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 概述

Write the test first. Watch it fail. Write minimal code to pass.

**Core principle:** If you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

**Always:**
- New features
- Bug fixes
- Refactoring
- Behavior changes

**Exceptions (ask your human partner):**
- Throwaway prototypes
- Generated code
- 配置 files

Thinking "skip TDD just this once"? Stop. That's rationalization.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

詳細內容請參閱：[example_8.txt](examples/example_8.txt)


### RED - Write Failing Test

Write one minimal test showing what should happen.

<Good>

詳細內容請參閱：[example_9.txt](examples/example_9.txt)

Clear name, tests real behavior, one thing
</Good>

<Bad>

詳細內容請參閱：[example_10.txt](examples/example_10.txt)

Vague name, tests mock not code
</Bad>

**需求:**
- One behavior
- Clear name
- Real code (no mocks unless unavoidable)

### Verify RED - Watch It Fail

**MANDATORY. Never skip.**

```bash
npm test path/to/test.test.ts

詳細內容請參閱：[example_11.txt](examples/example_11.txt)

Just enough to pass
</Good>

<Bad>

詳細內容請參閱：[example_12.txt](examples/example_12.txt)

Over-engineered
</Bad>

Don't add features, refactor other code, or "improve" beyond the test.

### Verify GREEN - Watch It Pass

**MANDATORY.**

```bash
npm test path/to/test.test.ts

詳細內容請參閱：[example_13.txt](examples/example_13.txt)


**Verify RED**
```bash
$ npm test
FAIL: expected 'Email required', got undefined

詳細內容請參閱：[example_14.txt](examples/example_14.txt)


**Verify GREEN**
```bash
$ npm test
PASS

詳細內容請參閱：[example_15.txt](examples/example_15.txt)

Production code → test exists and failed first
Otherwise → not TDD
```

No exceptions without your human partner's permission.


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