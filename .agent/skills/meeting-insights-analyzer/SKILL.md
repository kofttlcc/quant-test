---
name: meeting-insights-analyzer
description: >-
  Analyzes meeting transcripts and recordings to uncover behavioral patterns,
  communication insights, and actionable feedback. Identifies when you avoid
  conflict, use filler words, dominate conversations, or miss opportunities to
  listen. Perfect for professionals seeking to improve their communication and
  leadership skills.
trigger: when_needed
language: zh-TW
adapted_from: openskills/meeting-insights-analyzer
version: 1.0.0-antigravity
original_license: Unknown
---
# MEETING-INSIGHTS-ANALYZER 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/meeting-insights-analyzer  
> **語言**: 繁體中文

## 概述

Analyzes meeting transcripts and recordings to uncover behavioral patterns, communication insights, and actionable feedback. Identifies when you avoid conflict, use filler words, dominate conversations, or miss opportunities to listen. Perfect for professionals seeking to improve their communication and leadership skills.

---


# Meeting Insights Analyzer

This skill transforms your meeting transcripts into actionable insights about your communication patterns, helping you become a more effective communicator and leader.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

- Analyzing your communication patterns across multiple meetings
- Getting feedback on your leadership and facilitation style
- Identifying when you avoid difficult conversations
- Understanding your speaking habits and filler words
- Tracking improvement in communication skills over time
- Preparing for performance reviews with concrete examples
- Coaching team members on their communication style

## What This Skill Does

1. **Pattern Recognition**: Identifies recurring behaviors across meetings like:
   - Conflict avoidance or indirect communication
   - Speaking ratios and turn-taking
   - Question-asking vs. statement-making patterns
   - Active listening indicators
   - Decision-making approaches

2. **Communication Analysis**: Evaluates communication effectiveness:
   - Clarity and directness
   - Use of filler words and hedging language
   - Tone and sentiment patterns
   - Meeting control and facilitation

3. **Actionable Feedback**: Provides specific, timestamped examples with:
   - What happened
   - Why it matters
   - How to improve

4. **Trend Tracking**: Compares patterns over time when analyzing multiple meetings

## How to Use

### Basic Setup

1. Download your meeting transcripts to a folder (e.g., `~/meetings/`)
2. Navigate to that folder in Claude Code
3. Ask for the analysis you want

### 快速開始 範例

```
Analyze all meetings in this folder and tell me when I avoided conflict.
```

```
Look at my meetings from the past month and identify my communication patterns.
```

```
Compare my facilitation style between these two meeting folders.
```

### Advanced Analysis


詳細內容請參閱：[example_3.txt](examples/example_3.txt)


## Instructions

When a user requests meeting analysis:

1. **Discover Available Data**
   - Scan the folder for transcript files (.txt, .md, .vtt, .srt, .docx)
   - Check if files contain speaker labels and timestamps
   - Confirm the date range of meetings
   - Identify the user's name/identifier in transcripts

2. **Clarify Analysis Goals**
   
   If not specified, ask what they want to learn:
   - Specific behaviors (conflict avoidance, interruptions, filler words)
   - Communication effectiveness (clarity, directness, listening)
   - Meeting facilitation skills
   - Speaking patterns and ratios
   - Growth areas for improvement
   
3. **Analyze Patterns**

   For each requested insight:
   
   **Conflict Avoidance**:
   - Look for hedging language ("maybe", "kind of", "I think")
   - Indirect phrasing instead of direct requests
   - Changing subject when tension arises
   - Agreeing without commitment ("yeah, but...")
   - Not addressing obvious problems
   
   **Speaking Ratios**:
   - Calculate percentage of meeting spent speaking
   - Count interruptions (by and of the user)
   - Measure average speaking turn length
   - Track question vs. statement ratios
   
   **Filler Words**:
   - Count "um", "uh", "like", "you know", "actually", etc.
   - Note frequency per minute or per speaking turn
   - Identify situations where they increase (nervous, uncertain)
   
   **Active Listening**:
   - Questions that reference others' previous points
   - Paraphrasing or summarizing others' ideas
   - Building on others' contributions
   - Asking clarifying questions
   
   **Leadership & Facilitation**:
   - Decision-making approach (directive vs. collaborative)
   - How disagreements are handled
   - Inclusion of quieter participants
   - Time management and agenda control
   - Follow-up and action item clarity

4. **Provide Specific 範例**

   For each pattern found, include:
   

詳細內容請參閱：[example_4.txt](examples/example_4.txt)


5. **Synthesize Insights**

   After analyzing all patterns, provide:
   

詳細內容請參閱：[example_5.txt](examples/example_5.txt)


6. **Offer Follow-Up Options**
   - Track these same metrics in future meetings
   - Deep dive into specific meetings or patterns
   - Compare to industry benchmarks
   - Create a personal communication development plan
   - Generate a summary for performance reviews

## 範例

### Example 1: Conflict Avoidance Analysis (Inspired by Dan Shipper)

**User**: "I download all of my meeting recordings and put them in a folder. Tell me all the times I've subtly avoided conflict."

**Output**: 

詳細內容請參閱：[example_6.txt](examples/example_6.txt)


### Example 2: Leadership Facilitation

**User**: "Analyze my team meetings and tell me about my facilitation style."

**Output**: Provides insights on:
- How much you speak vs. team members (60% vs. 40%)
- Whether you ask questions or make statements (3:1 ratio)
- How you handle disagreements (tendency to resolve too quickly)
- Who speaks least and whether you draw them in
- 範例 of good and missed facilitation moments

### Example 3: Personal Development Tracking

**User**: "Compare my meetings from Q1 vs. Q2 to see if I've improved my listening skills."

**Output**: Creates a comparative analysis showing:
- Decrease in interruptions (8 per meeting → 3 per meeting)
- Increase in clarifying questions (2 → 7 per meeting)
- Improvement in building on others' ideas
- Specific examples showing the difference
- Remaining areas for growth

## Setup Tips

### Getting Meeting Transcripts

**From Granola** (free with Lenny's newsletter subscription):
- Granola auto-transcribes your meetings
- Export transcripts to a folder: [Instructions on how]
- Point Claude Code to that folder

**From Zoom**:
- Enable cloud recording with transcription
- Download VTT or SRT files after meetings
- Store in a dedicated folder

**From Google Meet**:
- Use Google Docs auto-transcription
- Save transcript docs to a folder
- Download as .txt files or give Claude Code access

**From Fireflies.ai, Otter.ai, etc.**:
- Export transcripts in bulk
- Store in a local folder
- Run analysis on the folder

### 最佳實踐

1. **Consistent naming**: Use `YYYY-MM-DD - Meeting Name.txt` format
2. **Regular analysis**: Review monthly or quarterly for trends
3. **Specific queries**: Ask about one behavior at a time for depth
4. **Privacy**: Keep sensitive meeting data local
5. **Action-oriented**: Focus on one improvement area at a time

## Common Analysis Requests

- "When do I avoid difficult conversations?"
- "How often do I interrupt others?"
- "What's my speaking vs. listening ratio?"
- "Do I ask good questions?"
- "How do I handle disagreement?"
- "Am I inclusive of all voices?"
- "Do I use too many filler words?"
- "How clear are my action items?"
- "Do I stay on agenda or get sidetracked?"
- "How has my communication changed over time?"

## Related Use Cases

- Creating a personal development plan from insights
- Preparing performance review materials with examples
- Coaching direct reports on their communication
- Analyzing customer calls for sales or support patterns
- Studying negotiation tactics and outcomes



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