# Antigravity Skill System 使用文檔

> **版本**: v1.0  
> **最後更新**: 2026-01-12  
> **適用對象**: Antigravity Agent 使用者

---

## 目錄

1. [系統概述](#系統概述)
2. [快速開始](#快速開始)
3. [一鍵轉換技能](#一鍵轉換技能)
4. [Agent 對話中使用技能](#agent-對話中使用技能)
5. [從市集安裝新技能](#從市集安裝新技能)
6. [常見問題](#常見問題)
7. [最佳實踐](#最佳實踐)

---

## 系統概述

Antigravity Skill System 讓您的 AI Agent 能夠：

- 📚 **調用專業技能** - 根據任務需求動態加載專業知識
- 🔄 **一鍵適配** - 將英文技能轉換為繁體中文版本
- 📦 **市集安裝** - 從社區市集一鍵安裝新技能

### 架構圖

```
┌─────────────────────────────────────────────────────────┐
│                    AGENTS.md                             │
│  ┌─────────────────────────────────────────────────┐    │
│  │ <skills_system>                                  │    │
│  │   <usage>openskills read <skill-name></usage>   │    │
│  │   <available_skills>                             │    │
│  │     <skill><name>pdf</name>...</skill>          │    │
│  │   </available_skills>                            │    │
│  │ </skills_system>                                 │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   openskills CLI                         │
│  優先讀取: SKILL.antigravity.md > SKILL.md              │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                    skills/ 目錄                          │
│  ├── pdf/                                               │
│  │   ├── SKILL.md              (英文原版)               │
│  │   └── SKILL.antigravity.md  (繁中適配版) ⭐          │
│  ├── xlsx/                                              │
│  │   ├── SKILL.md                                       │
│  │   └── SKILL.antigravity.md  ⭐                       │
│  └── systematic-debugging/                              │
│      └── SKILL.md              (未轉換，使用英文)       │
└─────────────────────────────────────────────────────────┘
```

---

## 快速開始

### 1. 確認環境

確保以下服務正在運行：

```bash
# 啟動 Skill Antigravity 服務
cd /Users/jerrylee/coding/skill-transform/skill-antigravity
./start.sh

# 或分別啟動前後端
cd server && npm run dev &
cd client && npm run dev &
```

### 2. 打開管理介面

瀏覽器訪問：**http://localhost:5173**

---

## 一鍵轉換技能

### 方法一：使用 Web UI

1. 打開 http://localhost:5173
2. 找到要轉換的技能卡片
3. 點擊 **「🔄 適配」** 按鈕
4. 等待轉換完成，按鈕變為 **「已適配」**

### 方法二：使用 CLI

```bash
# 轉換單個技能
cd /Users/jerrylee/coding
node skill-transform/skill-antigravity/cli/dist/index.js transform pdf

# 轉換所有技能
node skill-transform/skill-antigravity/cli/dist/index.js transform --all

# 預覽轉換結果（不寫入文件）
node skill-transform/skill-antigravity/cli/dist/index.js transform pdf --preview
```

### 轉換效果

| 項目 | 轉換前 | 轉換後 |
|------|--------|--------|
| 語言 | English | 繁體中文 |
| 標題 | Overview | 概述 |
| Frontmatter | 基本欄位 | 添加 `trigger`, `language`, `adapted_from` |
| 結構 | 自由格式 | 標準化（概述→使用情境→快速開始） |

---

## Agent 對話中使用技能

### SOP：在對話中調用技能

#### 步驟 1：確認技能可用

在對話中詢問 Agent：

```
請列出目前可用的技能
```

Agent 會參考 AGENTS.md 中的 `<available_skills>` 區塊回覆。

#### 步驟 2：請求 Agent 調用技能

**方式 A：直接請求任務**

```
請幫我處理這份 PDF 文件，提取其中的表格數據
```

Agent 會自動判斷需要使用 `pdf` 技能，並執行：

```bash
openskills read pdf
```

**方式 B：明確指定技能**

```
請使用 pdf 技能來合併這三份文件
```

#### 步驟 3：Agent 執行流程

```
1. Agent 識別任務需要 pdf 技能
2. 執行 Bash("openskills read pdf")
3. 獲取 SKILL.antigravity.md 內容（繁中版）
4. 根據技能指導完成任務
```

### 實際範例

#### 範例 1：PDF 處理

**用戶輸入：**
```
請幫我把這三份 PDF 合併成一個文件：report1.pdf, report2.pdf, report3.pdf
```

**Agent 行為：**
```python
# Agent 內部執行
Bash("openskills read pdf")

# 獲取技能內容後，執行：
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["report1.pdf", "report2.pdf", "report3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### 範例 2：系統化除錯

**用戶輸入：**
```
我的程式一直報錯，請幫我分析
```

**Agent 行為：**
```
1. 調用 openskills read systematic-debugging
2. 遵循「四階段除錯流程」：
   - Phase 1: 根因調查
   - Phase 2: 模式分析
   - Phase 3: 假設測試
   - Phase 4: 實施修復
```

---

## 從市集安裝新技能

### 使用 Web UI

1. 打開 http://localhost:5173
2. 點擊 **「技能市集」** 標籤
3. 瀏覽可用技能
4. 點擊 **「下載並安裝」**
5. 等待安裝完成

### 使用 CLI

```bash
# 從 GitHub 安裝
node skill-transform/openskills/dist/cli.js install https://github.com/obra/superpowers

# 同步到 AGENTS.md
node skill-transform/openskills/dist/cli.js sync
```

### 安裝後自動轉換

安裝新技能後，建議立即轉換：

```bash
# 安裝後轉換
node skill-transform/skill-antigravity/cli/dist/index.js transform <新技能名稱>
```

---

## 常見問題

### Q1：Agent 調用技能時讀取的是哪個版本？

**A：** 優先讀取 `SKILL.antigravity.md`（繁中版）。如果不存在，則回退到 `SKILL.md`（英文原版）。

### Q2：如何確認技能已成功轉換？

**A：** 檢查技能目錄：

```bash
ls skills/pdf/
# 應該看到：SKILL.md 和 SKILL.antigravity.md
```

或使用 CLI 讀取：

```bash
openskills read pdf | head -10
# 如果顯示 "language: zh-TW"，表示已成功使用繁中版
```

### Q3：轉換後可以回退嗎？

**A：** 可以。刪除 `SKILL.antigravity.md` 即可回退：

```bash
rm skills/pdf/SKILL.antigravity.md
# 之後 Agent 會讀取原始 SKILL.md
```

### Q4：為什麼市集下載失敗？

**A：** 常見原因：

1. **網絡問題** - 確認能訪問 GitHub
2. **Repo 無效** - 該 repo 可能沒有 SKILL.md 文件
3. **權限問題** - 私有 repo 需要配置認證

### Q5：如何添加自定義技能？

**A：** 在 `skills/` 目錄創建新資料夾：

```bash
mkdir skills/my-skill
cat > skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: 我的自定義技能描述
---

# 我的技能

技能內容...
EOF

# 同步到 AGENTS.md
openskills sync
```

---

## 最佳實踐

### ✅ 建議

1. **優先使用繁中版** - 符合 Constitution 語言規範
2. **定期同步 AGENTS.md** - 確保技能列表最新
3. **轉換後驗證** - 使用 `openskills read` 確認內容正確
4. **保留原始文件** - 不要刪除 SKILL.md，便於參考和回退

### ❌ 避免

1. **不要手動編輯 AGENTS.md 的 skills 區塊** - 使用 `openskills sync` 自動管理
2. **不要在對話中重複調用同一技能** - 技能內容已在上下文中
3. **不要使用未列出的技能** - 只調用 `<available_skills>` 中的技能

---

## 附錄：命令速查表

| 命令 | 功能 |
|------|------|
| `openskills read <name>` | 讀取技能內容 |
| `openskills list` | 列出所有已安裝技能 |
| `openskills sync` | 同步技能到 AGENTS.md |
| `openskills install <url>` | 從 Git URL 安裝技能 |
| `skill-antigravity transform <name>` | 轉換單個技能 |
| `skill-antigravity transform --all` | 轉換所有技能 |

---

> **需要幫助？** 請在 Antigravity Agent 對話中詢問相關問題。
