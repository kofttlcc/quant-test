# Antigravity model System

本專案採用先進的 **AI 雙腦協作架構 (Antigravity Dual-Brain Architecture)** 進行開發。此架構通過嚴格區分「生成」與「審計」職責，確保代碼的高速迭代與安全品質。

## 核心機制：雙腦協議 (The Dual-Mind Protocol)

本系統將開發過程分為兩個獨立的角色，彼此透過文件系統進行非同步協作：

| 角色 | **The Builder (建造者)** | **The Auditor (審計者)** |
| :--- | :--- | :--- |
| **職責** | 快速生成代碼、驗證創意、實現功能 | 審查邏輯、驗證安全性、檢查規範 |
| **特點** | **速度優先 (Speed)**。允許編寫「髒」代碼以快速驗證。 | **安全優先 (Safety)**。「進化」系統，將錯誤轉化為技能規則。 |
| **權限** | 僅在 `feat/` 分支工作，**禁止**推送到主分支。 | 唯一擁有合併代碼到 `main` 分支權限的角色。 |


---

## 角色責任與知識庫權限 (Role Responsibilities & Knowledge Governance)

本系統實施嚴格的 **讀寫分離 (Read/Write Separation)** 機制，以確保系統長期運行的穩定性與自我進化能力。

### 1. 權限矩陣 (Permission Matrix)

| 資源領域 (Domain) | **The Builder (Gemini)** | **The Auditor (Claude)** |
| :--- | :--- | :--- |
| **代碼庫 (Codebase)** | **Write (Draft)**<br>僅限 `feat/` 分支，允許快速與實驗性代碼。 | **Merge (Master)**<br>唯一擁有合併至 `main` 的權限，需確保代碼乾淨且通過測試。 |
| **知識庫 (Knowledge Base)**<br>(`.agent/skills/`) | **Read-Only**<br>必須讀取並遵循現有技能與規範。 | **Write (Evolve)**<br>唯一有權調用 `evolution_engine` 將發現的模式固化為新技能。 |
| **記憶文件 (Memory)**<br>(`rules/`, `roles/`) | **Read-Only**<br>依據角色文檔扮演特定 Persona。 | **Curate**<br>負責維護與更新系統憲法與角色定義。 |

### 2. 雙腦協作循環 (The Collaboration Loop)

1.  **Builder 開發**:
    *   讀取現有知識庫 (`skills/`) 獲取最佳實踐。
    *   在 `feat/` 分支上快速實現功能。
    *   提交 `handoff_notes.md` 請求審計。
2.  **Auditor 審計**:
    *   審查代碼邏輯與安全性。
    *   **進化判斷 (Evolution Check)**:
        *   若發現 Builder 犯了重複性錯誤 -> 調用 `evolution_engine` 寫入新規則，防止再犯。
        *   若發現通用優秀模式 -> 固化為新 Skill。
    *   批准合併或駁回重修。


## 運行模式

本專案支持兩種雙腦運作模式，以適應不同的資源與環境需求。

### 1. 雙腦雙模型 (Dual-Brain Dual-Model)

這是 Vibe Coding 的標準型態，利用不同模型的特性達到最佳效果。

*   **機制**:
    *   **Builder**: 由 **Gemini (如 1.5 Pro / Flash)** 擔任。擅長處理超長上下文，快速讀取大量文檔與代碼庫進行規劃與實作。
    *   **Auditor**: 由 **Claude (如 3.5 Sonnet)** 擔任。擅長邏輯推理、細節捕捉與安全審計，把控代碼品質的最後一道防線。
    *   **物理隔離**: 使用兩個完全不同的模型 API，天然具備思維隔離，避免模型對自己的錯誤產生「盲視」。
*   **優勢**: 取各家模型之長，互補性強，審計效果最佳。
*   **使用方法**:
    *   依照 `.agent/rules/constitution.md` 進行角色扮演。
    *   互動命令：
        *   `/vibe-build`: 喚起 Builder 進行開發。
        *   `/vibe-audit`: 喚起 Auditor 進行審查。

### 2. 單模型雙腦 (Single-Model Dual-Brain)

這是在資源受限、成本考量或單一模型環境下的變通方案，通過技術手段模擬雙腦互搏。

*   **機制**:
    *   **模型**: 統一使用 **Gemini 3 Pro** (或其他具備 Session 功能的強模型)。
    *   **邏輯隔離**: 利用 **Context (Session)** 機制區分 `builder_session` 與 `auditor_session`。
        *   雖然背後是同一個大腦，但擁有兩套獨立的短期記憶 (Context)，避免 Builder 的開發思路污染 Auditor 的審查判斷，實現「左手畫圓，右手畫方」。
*   **優勢**: 成本低（只需一份模型訂閱）、部署簡單、回應速度通常較快。
*   **使用方法**:
    1.  在專案對話模式下執行/vibe-auto-loop
    2.  腳本會自動監控 `artifacts/` 目錄的文件交互（如 `handoff_notes.md` 與 `audit_approval.md`），在 Builder 和 Auditor 角色間自動切換 Session。

---

