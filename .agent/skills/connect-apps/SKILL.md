---
name: connect-apps
description: >-
  Connect Claude to external apps like Gmail, Slack, GitHub. Use this skill when
  the user wants to send emails, create issues, post messages, or take actions
  in external services.
trigger: when_needed
language: zh-TW
adapted_from: openskills/connect-apps
version: 1.0.0-antigravity
original_license: Unknown
---
# CONNECT-APPS 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/connect-apps  
> **語言**: 繁體中文

## 概述

Connect Claude to external apps like Gmail, Slack, GitHub. Use this skill when the user wants to send emails, create issues, post messages, or take actions in external services.

---


# Connect Apps

Connect Claude to 1000+ apps. Actually send emails, create issues, post messages - not just generate text about it.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## 快速開始

### Step 1: Install the Plugin

```
/plugin install composio-toolrouter
```

### Step 2: Run Setup

```
/composio-toolrouter:setup

詳細內容請參閱：[example_1.txt](examples/example_1.txt)

Send me a test email at YOUR_EMAIL@example.com
```

If it works, you're connected!

## What You Can Do

| Ask Claude to... | What happens |
|------------------|--------------|
| "Send email to sarah@acme.com about the launch" | Actually sends the email |
| "Create GitHub issue: fix login bug" | Creates the issue |
| "Post to Slack #general: deploy complete" | Posts the message |
| "Add meeting notes to Notion" | Adds to Notion |

## Supported Apps

**Email:** Gmail, Outlook, SendGrid
**Chat:** Slack, Discord, Teams, Telegram
**Dev:** GitHub, GitLab, Jira, Linear
**Docs:** Notion, Google Docs, Confluence
**Data:** Sheets, Airtable, PostgreSQL
**And 1000+ more...**

## How It Works

1. You ask Claude to do something
2. Composio Tool Router finds the right tool
3. First time? You'll authorize via OAuth (one-time)
4. Action executes and returns result

## 故障排除

- **"Plugin not found"** → Make sure you ran `/plugin install composio-toolrouter`
- **"Need to authorize"** → Click the OAuth link Claude provides, then say "done"
- **Action failed** → Check you have permissions in the target app

---

<p align="center">
  <b>Join 20,000+ developers building agents that ship</b>
</p>

<p align="center">
  <a href="https://platform.composio.dev/?utm_source=Github&utm_content=AwesomeSkills">
    <img src="https://img.shields.io/badge/Get_Started_Free-4F46E5?style=for-the-badge" alt="Get Started"/>
  </a>
</p>


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