---
name: docx
description: >-
  全面的 文檔 creation, editing, and analysis with support for tracked changes,
  comments, formatting preservation, and text extraction. 當需要 to work with
  professional 文檔 (.docx files) for: (1) Creating new 文檔, (2) Modifying or
  editing content, (3) Working with tracked changes, (4) Adding comments, or any
  other 文檔 tasks
trigger: when_needed
language: zh-TW
adapted_from: openskills/docx
version: 1.0.0-antigravity
original_license: Proprietary. LICENSE.txt has complete terms
---
# DOCX 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/docx  
> **語言**: 繁體中文

## 概述

全面的 文檔 creation, editing, and analysis with support for tracked changes, comments, formatting preservation, and text extraction. 當需要 to work with professional 文檔 (.docx files) for: (1) Creating new 文檔, (2) Modifying or editing content, (3) Working with tracked changes, (4) Adding comments, or any other 文檔 tasks

---


# DOCX creation, editing, and analysis

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 概述

A user may ask you to create, edit, or analyze the contents of a .docx file. A .docx file is essentially a ZIP archive containing XML files and other resources that you can read or edit. You have different tools and workflows available for different tasks.

## Workflow Decision Tree

### Reading/Analyzing Content
Use "Text extraction" or "Raw XML access" sections below

### Creating New Document
Use "Creating a new Word document" workflow

### Editing Existing Document
- **Your own document + simple changes**
  Use "Basic OOXML editing" workflow

- **Someone else's document**
  Use **"Redlining workflow"** (recommended default)

- **Legal, academic, business, or government docs**
  Use **"Redlining workflow"** (required)

## Reading and analyzing content

### Text extraction
If you just need to read the text contents of a document, you should convert the document to markdown using pandoc. Pandoc provides excellent support for preserving document structure and can show tracked changes:

```bash
# Convert document to markdown with tracked changes
pandoc --track-changes=all path-to-file.docx -o output.md
# Options: --track-changes=accept/reject/all

詳細內容請參閱：[example_2.txt](examples/example_2.txt)


### Tracked changes workflow

1. **Get markdown representation**: Convert document to markdown with tracked changes preserved:
   ```bash
   pandoc --track-changes=all path-to-file.docx -o current.md

詳細內容請參閱：[example_3.txt](examples/example_3.txt)


6. **Final verification**: Do a comprehensive check of the complete document:
   - Convert final document to markdown:
     ```bash
     pandoc --track-changes=all reviewed-document.docx -o verification.md
     ```
   - Verify ALL changes were applied correctly:
     ```bash
     grep "original phrase" verification.md  # Should NOT find it
     grep "replacement phrase" verification.md  # Should find it

詳細內容請參閱：[example_4.txt](examples/example_4.txt)


2. **Convert PDF pages to JPEG images**:
   ```bash
   pdftoppm -jpeg -r 150 document.pdf page

詳細內容請參閱：[example_5.txt](examples/example_5.txt)


## Code Style Guidelines
**IMPORTANT**: When generating code for DOCX operations:
- Write concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements

## Dependencies

Required dependencies (install if not available):

- **pandoc**: `sudo apt-get install pandoc` (for text extraction)
- **docx**: `npm install -g docx` (for creating new documents)
- **LibreOffice**: `sudo apt-get install libreoffice` (for PDF conversion)
- **Poppler**: `sudo apt-get install poppler-utils` (for pdftoppm to convert PDF to images)
- **defusedxml**: `pip install defusedxml` (for secure XML parsing)

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