---
name: developer-growth-analysis
description: >-
  Analyzes your recent Claude Code chat history to identify coding patterns,
  development gaps, and areas for improvement, curates relevant learning
  resources from HackerNews, and automatically sends a personalized growth
  report to your Slack DMs.
trigger: when_needed
language: zh-TW
adapted_from: openskills/developer-growth-analysis
version: 1.0.0-antigravity
original_license: Unknown
---
# DEVELOPER-GROWTH-ANALYSIS 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/developer-growth-analysis  
> **語言**: 繁體中文

## 概述

Analyzes your recent Claude Code chat history to identify coding patterns, development gaps, and areas for improvement, curates relevant learning resources from HackerNews, and automatically sends a personalized growth report to your Slack DMs.

---


# Developer Growth Analysis

This skill provides personalized feedback on your recent coding work by analyzing your Claude Code chat interactions and identifying patterns that reveal strengths and areas for growth.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

Use this skill when you want to:
- Understand your development patterns and habits from recent work
- Identify specific technical gaps or recurring challenges
- Discover which topics would benefit from deeper study
- Get curated learning resources tailored to your actual work patterns
- Track improvement areas across your recent projects
- Find high-quality articles that directly address the skills you're developing

This skill is ideal for developers who want structured feedback on their growth without waiting for code reviews, and who prefer data-driven insights from their own work history.

## What This Skill Does

This skill performs a six-step analysis of your development work:

1. **Reads Your Chat History**: Accesses your local Claude Code chat history from the past 24-48 hours to understand what you've been working on.

2. **Identifies Development Patterns**: Analyzes the types of problems you're solving, technologies you're using, challenges you encounter, and how you approach different kinds of tasks.

3. **Detects Improvement Areas**: Recognizes patterns that suggest skill gaps, repeated struggles, inefficient approaches, or areas where you might benefit from deeper knowledge.

4. **Generates a Personalized Report**: Creates a comprehensive report showing your work summary, identified improvement areas, and specific recommendations for growth.

5. **Finds Learning Resources**: Uses HackerNews to curate high-quality articles and discussions directly relevant to your improvement areas, providing you with a reading list tailored to your actual development work.

6. **Sends to Your Slack DMs**: Automatically delivers the complete report to your own Slack direct messages so you can reference it anytime, anywhere.

## How to Use

Ask Claude to analyze your recent coding work:

```
Analyze my developer growth from my recent chats
```

Or be more specific about which time period:

```
Analyze my work from today and suggest areas for improvement

詳細內容請參閱：[example_2.txt](examples/example_2.txt)


5. **Search for Learning Resources**

   Use Rube MCP to search HackerNews for articles related to each improvement area:

   - For each improvement area, construct a search query targeting high-quality resources
   - Search HackerNews using RUBE_SEARCH_TOOLS with queries like:
     - "Learn [Technology/Pattern] best practices"
     - "[Technology] advanced patterns and techniques"
     - "Debugging [specific problem type] in [language]"
   - Prioritize posts with high engagement (comments, upvotes)
   - For each area, include 2-3 most relevant articles with:
     - Article title
     - Publication date
     - Brief description of why it's relevant
     - Link to the article

   Add this section to the report:


詳細內容請參閱：[example_3.txt](examples/example_3.txt)


6. **Present the Complete Report**

   Deliver the report in a clean, readable format that the user can:
   - Quickly scan for key takeaways
   - Use for focused learning planning
   - Reference over the next week as they work on improvements
   - Share with mentors if they want external feedback

7. **Send Report to Slack DMs**

   Use Rube MCP to send the complete report to the user's own Slack DMs:

   - Check if Slack connection is active via RUBE_SEARCH_TOOLS
   - If not connected, use RUBE_MANAGE_CONNECTIONS to initiate Slack auth
   - Use RUBE_MULTI_EXECUTE_TOOL to send the report as a formatted message:
     - Send the report title and period as the first message
     - Break the report into logical sections (Summary, Improvements, Strengths, Actions, Resources)
     - Format each section as a well-structured Slack message with proper markdown
     - Include clickable links for the learning resources
   - Confirm delivery in the CLI output

   This ensures the user has the report in a place they check regularly and can reference it throughout the week.

## Example 使用方式

### Input

```
Analyze my developer growth from my recent chats

詳細內容請參閱：[example_4.txt](examples/example_4.txt)


## Tips and 最佳實踐

- Run this analysis once a week to track your improvement trajectory over time
- Pick one improvement area at a time and focus on it for a few days before moving to the next
- Use the learning resources as a study guide; work through the recommended materials and practice applying the patterns
- Revisit this report after focusing on an area for a week to see how your work patterns change
- The learning resources are intentionally curated for your actual work, not generic topics, so they'll be highly relevant to what you're building

## How Accuracy and Quality Are Maintained

This skill:
- Analyzes your actual work patterns from timestamped chat history
- Generates evidence-based recommendations grounded in real projects
- Curates learning resources that directly address your identified gaps
- Focuses on actionable improvements, not vague feedback
- Provides specific time estimates based on complexity
- Prioritizes areas that will have the most impact on your development velocity


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