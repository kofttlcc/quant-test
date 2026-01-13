# Skill-Antigravity CLI

一鍵完成 skill 轉換，適配 Antigravity 系統。

## 安裝

```bash
cd cli
npm install
npm run build
```

## 使用方式

```bash
# 同步所有 skills 到 AGENTS.md
npx skill-antigravity sync

# 從 Git URL 安裝 skill
npx skill-antigravity install https://github.com/anthropics/skills

# 列出已安裝的 skills
npx skill-antigravity list
```

## 命令

| 命令 | 說明 |
|------|------|
| `sync` | 將 skills/ 目錄下的所有 SKILL.md 同步到 AGENTS.md |
| `install <url>` | 從 Git URL 克隆並安裝 skill |
| `list` | 列出所有已安裝的 skills |
| `help` | 顯示幫助信息 |

## 輸出格式

CLI 會在 AGENTS.md 中生成標準 `<skills_system>` XML 區塊，與 openskills 格式完全一致：

```xml
<skills_system priority="1">
  <available_skills>
    <skill>
      <name>skill-name</name>
      <description>...</description>
      <location>project</location>
    </skill>
  </available_skills>
</skills_system>
```
