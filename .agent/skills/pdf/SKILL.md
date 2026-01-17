---
name: pdf
description: >-
  全面的 PDF 操作 工具包 for 提取文字 and 表格, 創建新的 PDFs, 合併/分割 文檔, and 處理表單. 當需要 to fill in
  a PDF form or 以程式方式 處理, 生成, or 分析 PDF 文檔 大規模.
trigger: when_needed
language: zh-TW
adapted_from: openskills/pdf
version: 1.0.0-antigravity
original_license: Proprietary. LICENSE.txt has complete terms
---
# PDF 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/pdf  
> **語言**: 繁體中文

## 概述

全面的 PDF 操作 工具包 for 提取文字 and 表格, 創建新的 PDFs, 合併/分割 文檔, and 處理表單. 當需要 to fill in a PDF form or 以程式方式 處理, 生成, or 分析 PDF 文檔 大規模.

---


# PDF 處理指南
## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 概述

本指南 covers essential PDF processing operations using Python libraries and command-line tools. For advanced features, JavaScript libraries, and detailed examples, see reference.md. If you need to fill out a PDF form, read forms.md and follow its instructions.

## 快速開始


詳細內容請參閱：[example_5.py](examples/example_5.py)


## Python 函式庫
### pypdf - Basic Operations

#### Merge PDFs

詳細內容請參閱：[example_6.py](examples/example_6.py)


#### Split PDF

詳細內容請參閱：[example_7.py](examples/example_7.py)


#### Extract Metadata

詳細內容請參閱：[example_8.py](examples/example_8.py)


#### Rotate Pages

詳細內容請參閱：[example_9.py](examples/example_9.py)


### pdfplumber - Text and Table Extraction

#### Extract Text with Layout

詳細內容請參閱：[example_10.py](examples/example_10.py)


#### Extract Tables

詳細內容請參閱：[example_11.py](examples/example_11.py)


#### Advanced Table Extraction

詳細內容請參閱：[example_12.py](examples/example_12.py)


### reportlab - Create PDFs

#### Basic PDF Creation

詳細內容請參閱：[example_13.py](examples/example_13.py)


#### Create PDF with Multiple Pages

詳細內容請參閱：[example_14.py](examples/example_14.py)


## 命令行工具
### pdftotext (poppler-utils)

詳細內容請參閱：[script_14.sh](scripts/script_14.sh)


### qpdf

詳細內容請參閱：[script_15.sh](scripts/script_15.sh)


### pdftk (if available)

詳細內容請參閱：[script_16.sh](scripts/script_16.sh)


## 常見任務

### Extract Text from Scanned PDFs

詳細內容請參閱：[example_15.py](examples/example_15.py)


### 添加水印

詳細內容請參閱：[example_16.py](examples/example_16.py)


### 提取圖片
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.

詳細內容請參閱：[example_17.txt](examples/example_17.txt)


## 快速參考

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first |
| Fill PDF forms | pdf-lib or pypdf (see forms.md) | See forms.md |

## 後續步驟

- For advanced pypdfium2 usage, see reference.md
- For JavaScript libraries (pdf-lib), see reference.md
- If you need to fill out a PDF form, follow the instructions in forms.md
- For troubleshooting guides, see reference.md


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