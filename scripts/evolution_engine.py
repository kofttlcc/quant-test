from fastmcp import FastMCP, Context
import os
import time
from typing import Literal

# 初始化 MCP 服務器
mcp = FastMCP("Vibe Evolution Engine")

# 定義知識庫路徑
SKILLS_DIR = "skills"
LOG_FILE = "skills/evolution_history.log"

@mcp.tool
def search_knowledge(query: str, ctx: Context = None) -> str:
    """
    搜尋現有的開發模式和最佳實踐。
    在寫代碼前必須調用此工具。
    """
    results =
    if ctx: ctx.info(f"Searching skills for: {query}")
    
    for root, _, files in os.walk(SKILLS_DIR):
        for file in files:
            if file.endswith(".md"):
                try:
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # 簡單的關鍵字匹配，生產環境可換成 Vector Search
                        if query.lower() in content.lower():
                            results.append(f"### Pattern: {file}\n{content[:800]}...\n(Source: {path})")
                except Exception:
                    continue
    
    if not results:
        return "No exact matching patterns found. You are free to innovate, but adhere to global constitution."
    return "\n\n".join(results)

@mcp.tool
def evolve_skill(
    category: Literal["01-patterns", "02-troubleshooting", "03-architecture"],
    title: str,
    content: str,
    ctx: Context = None
) -> str:
    """
    將新的知識固化為技能文件。
    只有在發現通用模式或需要糾正 Team A 的錯誤行為時調用。
    """
    # 1. 安全檢查：防止路徑遍歷
    safe_title = "".join([c for c in title if c.isalnum() or c in "-_"]).lower()
    target_dir = os.path.join(SKILLS_DIR, category, "community")
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, f"{safe_title}.md")
    
    # 2. 寫入知識文件
    markdown_content = f"""---
title: {title}
created_at: {time.strftime('%Y-%m-%d %H:%M:%S')}
status: experimental
---

# {title}

{content}
"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        # 3. 寫入進化日誌
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f" EVOLVED: {category}/{safe_title}\n")
            
        if ctx: ctx.info(f"Knowledge evolved: {file_path}")
        return f"Successfully crystallized knowledge into {file_path}"
    except Exception as e:
        return f"Failed to evolve skill: {str(e)}"

if __name__ == "__main__":
    mcp.run()