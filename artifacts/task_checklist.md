# 任務執行清單 (Task Checklist)

## Phase 5 Audit Fixes

- [ ] **Context**: 讀取並理解 `artifacts/auditor_handoff.md` 中的錯誤詳情。
- [ ] **Fix CORS**:
    - [ ] 修改 `src/api/main.py` 添加 `CORSMiddleware`。
- [ ] **Fix Frontend Port**:
    - [ ] 搜索 `src/frontend/src` 中的 `5001`。
    - [ ] 替換為 `666` 或 `VITE_API_BASE`。
- [ ] **Verify**:
    - [ ] 運行 `start.sh`。
    - [ ] 驗證 CORS Headers。
    - [ ] 驗證 UI 連接。
