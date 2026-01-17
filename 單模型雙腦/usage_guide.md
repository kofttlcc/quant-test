# 單模型雙腦系統使用指南 (Single Model Dual Brain)

## 目錄內容
*   `design.md`: 架構設計說明。
*   `auto_loop_driver.py`: 自動化驅動腳本。

## 系統需求
1.  **Python 3**: 用於運行驅動腳本。
2.  **gemini-cli**: 必須安裝並配置好 PATH。
    *   驗證安裝: 終端輸入 `gemini --version`。
3.  **Antigravity Workspace**: 您的工作區應包含 `artifacts/` 目錄（腳本會自動創建，但建議確認寫入權限）。

## 快速開始

### 1. 設置環境變量 (可選)
如果您的模型名稱不是默認的 `gemini-3-pro`，請設置：
```bash
export GEMINI_MODEL="gemini-1.5-pro"  # 或您實際使用的模型ID
```

### 2. 運行驅動腳本
在您的專案根目錄 (`/Users/jerrylee/coding`) 下運行：

```bash
python3 單模型雙腦/auto_loop_driver.py
```

### 3. 觀察與交互
*   **終端輸出**: 腳本會顯示當前是哪個「大腦」(Builder 或 Auditor) 在思考。
*   **思考過程**: `gemini-cli` 的輸出會直接流式顯示在您的終端上。
*   **人工介入**:
    *   若要暫停，按 `Ctrl+C`。
    *   若需修改方向，可直接編輯 `artifacts/` 下生成的 Markdown 文件，AI 在下一輪讀取時會看到您的修改。

## 故障排除
*   **找不到 gemini 命令**: 請確認 `npm install -g @google/gemini-cli` (或對應安裝方式) 已執行。
*   **權限錯誤**: 確保腳本對 `artifacts/` 目錄有讀寫權限。
*   **模型錯誤**: 檢查 `GEMINI_MODEL` 是否正確。
