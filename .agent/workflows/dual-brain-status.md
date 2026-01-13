---
description: 查看雙腦協議當前狀態和迭代進度
---

# 雙腦協議狀態查詢

顯示當前迭代進度和交接狀態。

## 執行步驟

// turbo
1. 讀取 `artifacts/iteration_plan.md` 檢查各階段完成狀態

// turbo
2. 檢查 Git 分支狀態：`git branch -a && git log --oneline -5`

// turbo
3. 列出 `artifacts/` 目錄中的所有產出物

4. 生成狀態摘要：

```
## 迭代進度
- Phase 0: [狀態]
- Phase 1: [狀態]
- Phase 2: [狀態]
- Phase 3: [狀態]

## 當前分支
[分支名稱]

## 最新產出物
[列表]

## 下一步行動
[建議呼叫 /handoff-to-auditor 或 /handoff-to-builder]
```
