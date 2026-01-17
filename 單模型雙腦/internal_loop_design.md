# IDE 內原生雙腦循環 (Internal Dual Brain Loop)

## 1. 核心概念
與外部 CLI 腳本需要「物理」切換進程不同，在 IDE 環境中，我們的「單模型雙腦」是通過 **動態人格切換 (Dynamic Persona Switching)** 來實現的。

**原理**:
Agent 不會在每次 Handoff 時停止等待用戶，而是直接 **自我對話 (Self-Handoff)**。
*   **前半程**: 戴上 "Builder" 面具，產出代碼。
*   **後半程**: 摘下面具，戴上 "Auditor" 面具，審視此前的自己。

## 2. 實現機制：`/vibe-auto-loop` Workflow

我們將創建一個新的工作流 `.agent/workflows/vibe-auto-loop.md`，它將兩個獨立的 SOP 強制串聯：

### Phase 1: The Build (Builder Persona)
1.  Agent 讀取 `contexts/builder.md`。
2.  執行任務，生成 `artifacts/handoff_notes.md`。
3.  **關鍵點**: **不調用 `notify_user` 停止**，而是直接進入 Phase 2。

### Phase 2: The Audit (Auditor Persona)
1.  Agent 讀取 `contexts/auditor.md`。
2.  以「第三人稱」視角審計 Phase 1 的產出。
3.  **決策**:
    *   **🔴 駁回**: 在記憶中標記 "REJECTED"，並自動跳回 Phase 1 修正 (Reflection Loop)。
    *   **🟢 批准**: 生成 `audit_approval_*.md`。
    *   **🔁 繼續循環**: 若需求未全部完成，**強制跳回 Phase 1** 繼續開發。

### Phase 3: Final Handoff
1.  只有在 **Phase 2 批准** 且 **所有需求清單歸零** 後，才調用 `notify_user` 通知人類用戶。

## 3. 關鍵約束 (Critical Constraints)
*   **強制角色切換**: Build -> Audit, Audit -> Build (or Finish)。
*   **禁止中途退出**: 除非所有 Checklist 項目都打勾，否則不能停止。
*   **自我驅動**: 不依賴用戶輸入來推進步驟。

## 4. 如何落地
1.  創建 `.agent/workflows/vibe-auto-loop.md`。
2.  在項目中配置好 `contexts/` 目錄 (已完成)。
3.  用戶只需輸入指令：`@antigravity /vibe-auto-loop "我的需求..."`。
