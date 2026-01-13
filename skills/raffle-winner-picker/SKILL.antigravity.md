---
name: raffle-winner-picker
description: >-
  Picks random winners from lists, 電子表格s, or Google Sheets for giveaways,
  raffles, and contests. Ensures fair, unbiased selection with transparency.
trigger: when_needed
language: zh-TW
adapted_from: openskills/raffle-winner-picker
version: 1.0.0-antigravity
original_license: Unknown
---
# RAFFLE-WINNER-PICKER 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/raffle-winner-picker  
> **語言**: 繁體中文

## 概述

Picks random winners from lists, 電子表格s, or Google Sheets for giveaways, raffles, and contests. Ensures fair, unbiased selection with transparency.

---


# Raffle Winner Picker

This skill randomly selects winners from lists, spreadsheets, or Google Sheets for giveaways and contests.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

- Running social media giveaways
- Picking raffle winners at events
- Randomly selecting participants for surveys or tests
- Choosing winners from contest submissions
- Fair distribution of limited spots or resources
- Random team assignments

## What This Skill Does

1. **Random Selection**: Uses cryptographically random selection
2. **Multiple Sources**: Works with CSV, Excel, Google Sheets, or plain lists
3. **Multiple Winners**: Can pick one or multiple winners
4. **Duplicate Prevention**: Ensures the same person can't win twice
5. **Transparent Results**: Shows the selection process clearly
6. **Winner Details**: Displays all relevant information about winners

## How to Use

### From Google Sheets

```
Pick a random row from this Google Sheet to select a winner 
for a giveaway: [Sheet URL]
```

### From Local File

```
Pick 3 random winners from entries.csv
```

### From List

```
Pick a random winner from this list:
- Alice (alice@email.com)
- Bob (bob@email.com)
- Carol (carol@email.com)
...
```

### Multiple Winners

```
Pick 5 random winners from contest-entries.xlsx, 
make sure no duplicates
```

## Example

**User**: "Pick a random row from this Google Sheet to select a winner for a giveaway."

**Output**:
```
Accessing Google Sheet...
Total entries found: 247

Randomly selecting winner...

🎉 WINNER SELECTED! 🎉

Row #142
Name: Sarah Johnson
Email: sarah.j@email.com
Entry Date: March 10, 2024
Comment: "Love your newsletter!"

Selection method: Cryptographically random
Timestamp: 2024-03-15 14:32:18 UTC

Would you like to:
- Pick another winner (excluding Sarah)?
- Export winner details?
- Pick runner-ups?
```

**Inspired by:** Lenny's use case - picking a Sora 2 giveaway winner from his subscriber Slack community

## Features

### Fair Selection
- Uses secure random number generation
- No bias or patterns
- Transparent process
- Repeatable with seed (for verification)

### Exclusions
```
Pick a random winner excluding previous winners: 
Alice, Bob, Carol
```

### Weighted Selection
```
Pick a winner with weighted probability based on 
the "entries" column (1 entry = 1 ticket)
```

### Runner-ups
```
Pick 1 winner and 3 runner-ups from the list
```

## Example Workflows

### Social Media Giveaway
1. Export entries from Google Form to Sheets
2. "Pick a random winner from [Sheet URL]"
3. Verify winner details
4. Announce publicly with timestamp

### Event Raffle
1. Create CSV of attendee names and emails
2. "Pick 10 random winners from attendees.csv"
3. Export winner list
4. Email winners directly

### Team Assignment
1. Have list of participants
2. "Randomly split this list into 4 equal teams"
3. Review assignments
4. Share team rosters

## Tips

- **Document the process**: Save the timestamp and method
- **Public announcement**: Share selection details for transparency
- **Check eligibility**: Verify winner meets contest rules
- **Have backups**: Pick runner-ups in case winner is ineligible
- **Export results**: Save winner list for records

## Privacy & Fairness

✓ Uses cryptographically secure randomness
✓ No manipulation possible
✓ Timestamp recorded for verification
✓ Can provide seed for third-party verification
✓ Respects data privacy

## Common Use Cases

- Newsletter subscriber giveaways
- Product launch raffles
- Conference ticket drawings
- Beta tester selection
- Focus group participant selection
- Random prize distribution at events



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
