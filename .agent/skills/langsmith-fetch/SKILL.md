---
name: langsmith-fetch
description: >-
  Debug LangChain and LangGraph agents by fetching execution traces from
  LangSmith Studio. Use when debugging agent behavior, investigating errors,
  analyzing tool calls, checking memory operations, or examining agent
  performance. Automatically fetches recent traces and 分析s execution patterns.
  Requires langsmith-fetch CLI installed.
trigger: when_needed
language: zh-TW
adapted_from: openskills/langsmith-fetch
version: 1.0.0-antigravity
original_license: Unknown
---
# LANGSMITH-FETCH 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/langsmith-fetch  
> **語言**: 繁體中文

## 概述

Debug LangChain and LangGraph agents by fetching execution traces from LangSmith Studio. Use when debugging agent behavior, investigating errors, analyzing tool calls, checking memory operations, or examining agent performance. Automatically fetches recent traces and 分析s execution patterns. Requires langsmith-fetch CLI installed.

---


# LangSmith Fetch - Agent Debugging Skill

Debug LangChain and LangGraph agents by fetching execution traces directly from LangSmith Studio in your terminal.

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## When to Use This Skill

Automatically activate when user mentions:
- 🐛 "Debug my agent" or "What went wrong?"
- 🔍 "Show me recent traces" or "What happened?"
- ❌ "Check for errors" or "Why did it fail?"
- 💾 "Analyze memory operations" or "Check LTM"
- 📊 "Review agent performance" or "Check token usage"
- 🔧 "What tools were called?" or "Show execution flow"

## Prerequisites

### 1. Install langsmith-fetch
```bash
pip install langsmith-fetch
```

### 2. Set Environment Variables
```bash
export LANGSMITH_API_KEY="your_langsmith_api_key"
export LANGSMITH_PROJECT="your_project_name"
```

**Verify setup:**
```bash
echo $LANGSMITH_API_KEY
echo $LANGSMITH_PROJECT

詳細內容請參閱：[example_6.txt](examples/example_6.txt)


**Analyze and report:**
1. ✅ Number of traces found
2. ⚠️ Any errors or failures
3. 🛠️ Tools that were called
4. ⏱️ Execution times
5. 💰 Token usage

**Example response format:**

詳細內容請參閱：[example_7.txt](examples/example_7.txt)


---

### Workflow 2: Deep Dive Specific Trace

**When user provides:** Trace ID or says "investigate that error"

**Execute:**
```bash
langsmith-fetch trace <trace-id> --format json

詳細內容請參閱：[example_8.txt](examples/example_8.txt)

Deep Dive Analysis - Trace abc123

Goal: User asked "Find all projects in Neo4j"

Execution Flow:
1. ✅ search_nodes(query: "projects")
   → Found 24 nodes

2. ❌ get_node_details(node_id: "proj_123")
   → Error: "Node not found"
   → This is the failure point

3. ⏹️ Execution stopped

Root Cause:
The search_nodes tool returned node IDs that no longer exist in the database,
possibly due to recent deletions.

Suggested Fix:
1. Add error handling in get_node_details tool
2. Filter deleted nodes in search results
3. Update cache invalidation strategy

Token 使用方式: 1,842 tokens ($0.0276)
Execution Time: 8.7 seconds

詳細內容請參閱：[example_9.txt](examples/example_9.txt)


**Report:**

詳細內容請參閱：[example_10.txt](examples/example_10.txt)


---

### Workflow 4: Error Detection

**When user asks:** "Show me errors" or "What's failing?"

**Execute:**
```bash
# Fetch recent traces
langsmith-fetch traces --last-n-minutes 30 --limit 50 --format json > recent-traces.json

# Search for errors
grep -i "error\|failed\|exception" recent-traces.json

詳細內容請參閱：[example_11.txt](examples/example_11.txt)

Error Analysis - Last 30 Minutes

Total Traces: 50
Failed Traces: 7 (14% failure rate)

Error Breakdown:
1. Neo4j Connection Timeout (4 occurrences)
   - Agent: cypher
   - Tool: search_nodes
   - First occurred: 14:32
   - Last occurred: 14:45
   - Pattern: Happens during peak load

2. Memory Store Failed (2 occurrences)
   - Agent: memento
   - Tool: store_memory
   - Error: "Pinecone rate limit exceeded"
   - Occurred: 14:38, 14:41

3. Tool Not Found (1 occurrence)
   - Agent: sqlcrm
   - Attempted tool: "export_report" (doesn't exist)
   - Occurred: 14:35

💡 Recommendations:
1. Add retry logic for Neo4j timeouts
2. Implement rate limiting for Pinecone
3. Fix sqlcrm tool configuration

詳細內容請參閱：[example_12.txt](examples/example_12.txt)


2. **If NO traces found:**
   - Tracing might be disabled
   - Check: `LANGCHAIN_TRACING_V2=true` in environment
   - Check: `LANGCHAIN_API_KEY` is set
   - Verify agent actually ran

3. **If traces found:**
   - Review for errors
   - Check execution time (hanging?)
   - Verify tool calls completed

---

### Use Case 2: "Wrong Tool Called"

**User says:** "Why did it use the wrong tool?"

**Steps:**
1. Get the specific trace
2. Review available tools at execution time
3. Check agent's reasoning for tool selection
4. Examine tool descriptions/instructions
5. Suggest prompt or tool config improvements

---

### Use Case 3: "Memory Not Working"

**User says:** "Agent doesn't remember things"

**Steps:**
1. Search for memory operations:
   ```bash
   langsmith-fetch traces --last-n-minutes 10 --limit 20 --format raw | grep -i "memory\|recall\|store"

詳細內容請參閱：[example_13.txt](examples/example_13.txt)


2. Analyze:
   - Execution time per trace
   - Tool call latencies
   - Token usage (context size)
   - Number of iterations
   - Slowest operations

3. Identify bottlenecks and suggest optimizations

---

## Output Format Guide

### Pretty Format (Default)
```bash
langsmith-fetch traces --limit 5 --format pretty
```
**Use for:** Quick visual inspection, showing to users

### JSON Format
```bash
langsmith-fetch traces --limit 5 --format json
```
**Use for:** Detailed analysis, syntax-highlighted review

### Raw Format
```bash
langsmith-fetch traces --limit 5 --format raw

詳細內容請參閱：[example_14.txt](examples/example_14.txt)


### Include Metadata
```bash
# Get extra context
langsmith-fetch traces --limit 10 --include-metadata

# Metadata includes: agent type, model, tags, environment
```

### Concurrent Fetching (Faster)
```bash
# Speed up large exports
langsmith-fetch traces ./output --limit 100 --concurrent 10

詳細內容請參閱：[example_15.txt](examples/example_15.txt)


### "Project not found"

**Solution:**

詳細內容請參閱：[script_10.sh](scripts/script_10.sh)


### Environment variables not persisting

**Solution:**

詳細內容請參閱：[script_11.sh](scripts/script_11.sh)


---

## 最佳實踐

### 1. Regular Health Checks
```bash
# Quick check after making changes
langsmith-fetch traces --last-n-minutes 5 --limit 5
```

### 2. Organized Storage

詳細內容請參閱：[example_16.txt](examples/example_16.txt)


### 3. Document Findings
When you find bugs:
1. Export the problematic trace
2. Save to `error-cases/` folder
3. Note what went wrong in a README
4. Share trace ID with team

### 4. Integration with Development
```bash
# Before committing code
langsmith-fetch traces --last-n-minutes 10 --limit 5

# If errors found
langsmith-fetch trace <error-id> --format json > pre-commit-error.json

詳細內容請參閱：[example_17.txt](examples/example_17.txt)


---

## Resources

- **LangSmith Fetch CLI:** https://github.com/langchain-ai/langsmith-fetch
- **LangSmith Studio:** https://smith.langchain.com/
- **LangChain Docs:** https://docs.langchain.com/
- **This Skill Repo:** https://github.com/OthmanAdi/langsmith-fetch-skill

---

## Notes for Claude

- Always check if `langsmith-fetch` is installed before running commands
- Verify environment variables are set
- Use `--format pretty` for human-readable output
- Use `--format json` when you need to parse and analyze data
- When exporting sessions, create organized folder structures
- Always provide clear analysis and actionable insights
- If commands fail, help troubleshoot configuration issues

---

**Version:** 0.1.0
**Author:** Ahmad Othman Ammar Adi
**授權:** MIT
**Repository:** https://github.com/OthmanAdi/langsmith-fetch-skill


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