---
name: invoice-organizer
description: >-
  Automatically organizes invoices and receipts for tax preparation by reading
  messy files, extracting key information, renaming them consistently, and
  sorting them into logical folders. Turns hours of manual bookkeeping into
  minutes of automated organization.
trigger: when_needed
language: zh-TW
adapted_from: openskills/invoice-organizer
version: 1.0.0-antigravity
original_license: Unknown
---
# INVOICE-ORGANIZER 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/invoice-organizer  
> **語言**: 繁體中文

## 概述

Automatically organizes invoices and receipts for tax preparation by reading messy files, extracting key information, renaming them consistently, and sorting them into logical folders. Turns hours of manual bookkeeping into minutes of automated organization.

---


# Invoice Organizer

This skill transforms chaotic folders of invoices, receipts, and financial documents into a clean, tax-ready filing system without manual effort.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

- Preparing for tax season and need organized records
- Managing business expenses across multiple vendors
- Organizing receipts from a messy folder or email downloads
- Setting up automated invoice filing for ongoing bookkeeping
- Archiving financial records by year or category
- Reconciling expenses for reimbursement
- Preparing documentation for accountants

## What This Skill Does

1. **Reads Invoice Content**: Extracts information from PDFs, images, and documents:
   - Vendor/company name
   - Invoice number
   - Date
   - Amount
   - Product or service description
   - Payment method

2. **Renames Files Consistently**: Creates standardized filenames:
   - Format: `YYYY-MM-DD Vendor - Invoice - ProductOrService.pdf`
   - 範例: `2024-03-15 Adobe - Invoice - Creative Cloud.pdf`

3. **Organizes by Category**: Sorts into logical folders:
   - By vendor
   - By expense category (software, office, travel, etc.)
   - By time period (year, quarter, month)
   - By tax category (deductible, personal, etc.)

4. **Handles Multiple Formats**: Works with:
   - PDF invoices
   - Scanned receipts (JPG, PNG)
   - Email attachments
   - Screenshots
   - Bank statements

5. **Maintains Originals**: Preserves original files while organizing copies

## How to Use

### Basic 使用方式

Navigate to your messy invoice folder:
```
cd ~/Desktop/receipts-to-sort
```

Then ask Claude Code:
```
Organize these invoices for taxes
```

Or more specifically:
```
Read all invoices in this folder, rename them to 
"YYYY-MM-DD Vendor - Invoice - Product.pdf" format, 
and organize them by vendor
```

### Advanced Organization

```
Organize these invoices:
1. Extract date, vendor, and description from each file
2. Rename to standard format
3. Sort into folders by expense category (Software, Office, Travel, etc.)
4. Create a CSV spreadsheet with all invoice details for my accountant

詳細內容請參閱：[example_9.txt](examples/example_9.txt)

   
   Report findings:
   - Total number of files
   - File types
   - Date range (if discernible from names)
   - Current organization (or lack thereof)

2. **Extract Information from Each File**
   
   For each invoice, extract:
   
   **From PDF invoices**:
   - Use text extraction to read invoice content
   - Look for common patterns:
     - "Invoice Date:", "Date:", "Issued:"
     - "Invoice #:", "Invoice Number:"
     - Company name (usually at top)
     - "Amount Due:", "Total:", "Amount:"
     - "Description:", "Service:", "Product:"
   
   **From image receipts**:
   - Read visible text from images
   - Identify vendor name (often at top)
   - Look for date (common formats)
   - Find total amount
   
   **Fallback for unclear files**:
   - Use filename clues
   - Check file creation/modification date
   - Flag for manual review if critical info missing

3. **Determine Organization Strategy**
   
   Ask user preference if not specified:
   

詳細內容請參閱：[example_10.txt](examples/example_10.txt)


4. **Create Standardized Filename**
   
   For each invoice, create a filename following this pattern:
   
   ```
   YYYY-MM-DD Vendor - Invoice - Description.ext

詳細內容請參閱：[example_11.txt](examples/example_11.txt)

   Invoices/
   ├── 2023/
   │   ├── Software/
   │   │   ├── Adobe/
   │   │   └── Microsoft/
   │   ├── Services/
   │   └── Office/
   └── 2024/
       ├── Software/
       ├── Services/
       └── Office/

詳細內容請參閱：[example_12.txt](examples/example_12.txt)

   
   After approval:

詳細內容請參閱：[script_1.sh](scripts/script_1.sh)


6. **Generate Summary Report**
   
   Create a CSV file with all invoice details:
   
   ```csv
   Date,Vendor,Invoice Number,Description,Amount,Category,File Path
   2024-03-15,Adobe,INV-12345,Creative Cloud,52.99,Software,Invoices/2024/Software/Adobe/2024-03-15 Adobe - Invoice - Creative Cloud.pdf
   2024-03-10,Amazon,123-4567890-1234567,Office Supplies,127.45,Office,Invoices/2024/Office/Amazon/2024-03-10 Amazon - Receipt - Office Supplies.pdf
   ...

詳細內容請參閱：[example_13.txt](examples/example_13.txt)

   Invoices/
   ├── 2024/ (45 files)
   │   ├── Software/ (23 files)
   │   ├── Services/ (12 files)
   │   └── Office/ (10 files)
   └── 2023/ (12 files)

詳細內容請參閱：[example_14.txt](examples/example_14.txt)


## 範例

### Example 1: Tax Preparation (From Martin Merschroth)

**User**: "I have a messy folder of invoices for taxes. Sort them and rename properly."

**Process**:
1. Scans folder: finds 147 PDFs and images
2. Reads each invoice to extract:
   - Date
   - Vendor name
   - Invoice number
   - Product/service description
3. Renames all files: `YYYY-MM-DD Vendor - Invoice - Product.pdf`
4. Organizes into: `2024/Software/`, `2024/Travel/`, etc.
5. Creates `invoice-summary.csv` for accountant
6. Result: Tax-ready organized invoices in minutes

### Example 2: Monthly Expense Reconciliation

**User**: "Organize my business receipts from last month by category."

**Output**:

詳細內容請參閱：[example_15.txt](examples/example_15.txt)


### Example 3: Multi-Year Archive

**User**: "I have 3 years of random invoices. Organize them by year, then by vendor."

**Output**: Creates structure:

詳細內容請參閱：[example_16.txt](examples/example_16.txt)


Each file properly renamed with date and description.

### Example 4: Email Downloads Cleanup

**User**: "I download invoices from Gmail. They're all named 'invoice.pdf', 'invoice(1).pdf', etc. Fix this mess."

**Output**:

詳細內容請參閱：[example_17.txt](examples/example_17.txt)


## Common Organization Patterns

### By Vendor (Simple)
```
Invoices/
├── Adobe/
├── Amazon/
├── Google/
└── Microsoft/
```

### By Year and Category (Tax-Friendly)

詳細內容請參閱：[example_18.txt](examples/example_18.txt)


### By Quarter (Detailed Tracking)

詳細內容請參閱：[example_19.txt](examples/example_19.txt)


### By Tax Category (Accountant-Ready)

詳細內容請參閱：[example_20.txt](examples/example_20.txt)


## Automation Setup

For ongoing organization:

```
Create a script that watches my ~/Downloads/invoices folder 
and auto-organizes any new invoice files using our standard 
naming and folder structure.
```

This creates a persistent solution that organizes invoices as they arrive.

## Pro Tips

1. **Scan emails to PDF**: Use Preview or similar to save email invoices as PDFs first
2. **Consistent downloads**: Save all invoices to one folder for batch processing
3. **Monthly routine**: Organize invoices monthly, not annually
4. **Backup originals**: Keep original files before reorganizing
5. **Include amounts in CSV**: Useful for budget tracking
6. **Tag by deductibility**: Note which expenses are tax-deductible
7. **Keep receipts 7 years**: Standard audit period

## Handling Special Cases

### Missing Information
If date/vendor can't be extracted:
- Flag file for manual review
- Use file modification date as fallback
- Create "Needs-Review/" folder

### Duplicate Invoices
If same invoice appears multiple times:
- Compare file hashes
- Keep highest quality version
- Note duplicates in summary

### Multi-Page Invoices
For invoices split across files:
- Merge PDFs if needed
- Use consistent naming for parts
- Note in CSV if invoice is split

### Non-Standard Formats
For unusual receipt formats:
- Extract what's possible
- Standardize what you can
- Flag for review if critical info missing

## Related Use Cases

- Creating expense reports for reimbursement
- Organizing bank statements
- Managing vendor contracts
- Archiving old financial records
- Preparing for audits
- Tracking subscription costs over time



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