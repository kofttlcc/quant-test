# Builder 移交文檔：問題修復 Sprint

**Date**: 2026-01-13  
**From**: @pm → @builder  
**Status**: 🔴 待處理

---

## 背景

用戶在 Sprint 1 UI 落地驗收時發現 4 個問題，需緊急修復。

---

## 問題清單

| # | 問題 | 嚴重度 | 預估工時 |
|---|------|--------|---------|
| 1 | 回測點擊彈出告警 | **P0** | 0.5h |
| 2 | 新聞實時更新失敗 | P1 | 2h |
| 3 | 日期格式改變 | P2 | 0.5h |
| 4 | 價格數據未更新 | P1 | 1h |

---

## 問題 1：回測告警（P0 緊急）

### 現象
點擊回測後彈出告警，無法正常使用。

### 根因
`src/api/main.py` 第 54 行：
```python
storage = ResultStorage() if ResultStorage else None
```
若 `ResultStorage` 導入失敗，`storage` 為 None，導致：
- 第 757 行 `storage.save_run()` 報錯
- 第 1037 行 `storage.save_run()` 報錯

### 修復方案

#### [MODIFY] [main.py](file:///Users/jerrylee/coding/src/api/main.py)

**位置 1**: 第 757 行附近
```python
# 修改前
storage.save_run(...)

# 修改後
if storage:
    storage.save_run(...)
```

**位置 2**: 第 1037 行附近
```python
# 同樣添加 null check
if storage:
    storage.save_run(...)
```

---

## 問題 2：新聞更新失敗（P1）

### 現象
新聞實時更新有問題，無法顯示。

### 根因
```
WARNING:src.services.news_service:Yahoo RSS 獲取失敗: not well-formed (invalid token)
```
Yahoo Finance RSS 返回的 XML 格式不規範。

### 修復方案

#### [MODIFY] [news_service.py](file:///Users/jerrylee/coding/src/services/news_service.py)

```python
# 方案 A: 使用 feedparser 庫
import feedparser
feed = feedparser.parse(rss_url)

# 方案 B: 添加錯誤處理，靜默失敗
try:
    # 解析邏輯
except Exception as e:
    logger.warning(f"RSS 解析失敗: {e}")
    return []  # 返回空列表，不影響主流程
```

---

## 問題 3：日期格式問題（P2）

### 現象
回測圖表日期顯示格式從 `YYYY-MM-DD` 變為 `MM-DD`。

### 根因
`QuantDashboard.jsx` 第 449 行：
```javascript
time: d.time.substring(5), // "MM-DD" 格式
```

### 修復方案

#### [MODIFY] [QuantDashboard.jsx](file:///Users/jerrylee/coding/src/frontend/src/components/QuantDashboard.jsx)

```javascript
// 修改前
time: d.time.substring(5), // "MM-DD"

// 修改後 - 選項 A: 保留完整日期
time: d.time, // "YYYY-MM-DD"

// 修改後 - 選項 B: 縮短年份
time: d.time.substring(2), // "YY-MM-DD"
```

---

## 問題 4：價格數據未更新（P1）

### 現象
價格數據一直沒有更新成功。

### 根因
```
INFO:src.data_loader.downloader:Cache Hit for AAPL (Rows: 508)
```
數據緩存機制未過期，持續返回舊數據。

### 修復方案

#### [MODIFY] [downloader.py](file:///Users/jerrylee/coding/src/data_loader/downloader.py)

```python
# 添加強制刷新參數
def fetch_data(ticker, start_date=None, end_date=None, force_refresh=False):
    if force_refresh:
        # 跳過緩存，直接獲取
        ...
```

#### [MODIFY] [main.py](file:///Users/jerrylee/coding/src/api/main.py)

```python
# API 添加 force_refresh 參數
force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
df = fetch_data(ticker, start_date=start_date, force_refresh=force_refresh)
```

---

## 驗收標準

| 問題 | 驗收標準 |
|------|---------|
| 問題 1 | 回測正常執行，無告警彈出 |
| 問題 2 | 新聞區域不報錯（可顯示空或 fallback） |
| 問題 3 | 日期顯示為完整格式或用戶可接受格式 |
| 問題 4 | 添加刷新按鈕或 API 支持強制刷新 |

---

## 優先級執行順序

1. ✅ **P0**: 問題 1 (回測告警) - 立即修復
2. ⏳ **P1**: 問題 4 (價格數據) - 次優先
3. ⏳ **P1**: 問題 2 (新聞更新) - 次優先
4. ⏳ **P2**: 問題 3 (日期格式) - 可選

---

**PM Signature**: @pm  
**Date**: 2026-01-13 23:14
