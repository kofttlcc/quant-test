---
name: skill-cleaner
description:  Standardizes and refactors other skills into the Antigravity skill format (separating scripts, examples, and resources).
trigger: when_refactoring_skills
language: zh-TW
version: 1.0.0
---

# SKILL-CLEANER 技能整理指南

本技能用於指導 Agent 將舊版或結構混亂的技能重構為標準的 Antigravity 技能結構。

## 使用情境

- 當現有技能只有一個龐大的 `SKILL.md`，其中混雜了大量代碼塊時。
- 當需要將技能的配置、範例代碼或腳本分離到獨立文件時。
- 當需要標準化技能目錄結構時。

## 標準目錄結構

重構後的技能應遵循以下結構：

```text
.agent/skills/<skill-name>/
├── SKILL.md       # 核心指令文件
├── scripts/       # 可執行的輔助腳本 (Python, Bash 等)
├── examples/      # 範例代碼、模板或是 Reference Implementations
└── resources/     # 靜態資源、模板文件、字典等
```

## 執行步驟

### 第一步：分析 (Analysis)
1. 讀取目標技能的 `SKILL.md`。
2. 識別其中的代碼塊：
    - 是否為可執行的工具腳本？ -> 歸類為 `scripts/`
    - 是否為用戶參考的實作範本？ -> 歸類為 `examples/`
    - 是否為靜態配置或數據？ -> 歸類為 `resources/`

### 第二步：結構化 (Structuring)
1. 在目標技能目錄下建立 `scripts`, `examples`, `resources` 子目錄。
2. 確保 `.gitignore` (如果有的話) 不會忽略這些新目錄。

### 第三步：提取 (Extraction)
1. 將識別出的代碼塊寫入對應目錄的新獨立文件中。
2. 文件命名應具描述性，例如 `implementation_template.py` 或 `setup_env.sh`。

### 第四步：清理與連結 (Cleanup & Linking)
1. 編輯 `SKILL.md`，移除已提取的大段代碼塊。
2. 在原位置加入對新文件的引用連結。
    - 格式：`參考實作：[filename](examples/filename.py)`
    - 或簡要說明：`請使用 scripts/ 目錄下的腳本進行操作。`

## 輔助工具

可使用 `scripts/extract_code_blocks.py` 來快速分析 Markdown 文件中的代碼塊（需根據具體需求手動執行或作為參考）。
