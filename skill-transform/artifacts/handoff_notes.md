# Handoff Notes - Skill Transformation & Sync

**分支**: `feat/20260112-vibe-doc` (Integrated Vibe Build)
**任務目標**: 實現一鍵安裝 Skill 並自動轉換為 Antigravity 適配格式 (同步至 `AGENTS.md`)。

## 已完成項目 (What was built)
1.  **Skill Registry Service (`skillRegistry.ts`)**:
    - 實作了 `syncSkills()` 函數。
    - 功能：掃描 `skills/` 目錄下的所有 `SKILL.md`，解析元數據，生成 `<skills_system>` XML 區塊。
    - 自動更新項目根目錄的 `AGENTS.md`，將新技能註冊到系統中。

2.  **Installer Integration (`skillInstaller.ts`)**:
    - 修改了 `installSkillFromUrl` 流程。
    - 在 Git Clone 和物理複製完成後，自動調用 `syncSkills()`。
    - 實現了「下載 -> 安裝 -> 註冊」的全鏈條自動化。

3.  **文檔更新**:
    - 更新了 `skill_transformation_logic.md` 以反映真實的 Sync 機制。

## 捷徑與限制 (Shortcuts & Limitations)
- **重複技能**: 安裝器目前使用時間戳 (`[name]-[timestamp]`) 作為目錄名以避免衝突，這導致同一技能的多次安裝會在 `AGENTS.md` 中產生重複條目（因為它們共享相同的 `name`）。未來應增加去重或版本管理邏輯。
- **錯誤處理**: `glob` 導入問題已修復 (使用 `globSync`)，但在特定環境下可能需注意 `glob` 版本差異。

## 待確認事項 (Uncertainties)
- 無。

## 下一步 (Next Steps)
- 建議 `@auditor` 測試從 UI 安裝技能，並檢查 `AGENTS.md` 是否即時更新。
- 考慮增加「卸載」功能，同步移除 `AGENTS.md` 中的條目。
