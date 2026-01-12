# Troubleshooting Patterns (錯誤排查模式)

> **版本**: v1.0
> **最後更新**: 2026-01-12
> **維護者**: @auditor

---

## 目錄

1. [PATTERN-001: Bare Except 反模式](#pattern-001-bare-except-反模式)
2. [PATTERN-002: 重複模組導入](#pattern-002-重複模組導入)

---

## PATTERN-001: Bare Except 反模式

### 錯誤症狀

```python
try:
    data = yf.download(ticker)
except:
    data = None
```

**問題**:
- 捕獲所有異常 (包括 `KeyboardInterrupt`, `SystemExit`)
- 掩蓋真正的錯誤原因
- 無法進行調試和錯誤追蹤

### 正確寫法

```python
try:
    data = yf.download(ticker)
except Exception as e:
    logger.warning(f"Download failed: {e}")
    data = None
```

**或更精確的異常捕獲**:

```python
try:
    data = yf.download(ticker)
except (requests.RequestException, ValueError) as e:
    logger.warning(f"Download failed: {e}")
    data = None
```

### 原理簡述

1. **`except:` vs `except Exception:`**:
   - `except:` 捕獲所有異常，包括系統級異常
   - `except Exception:` 只捕獲標準異常，不會干擾 `Ctrl+C` 等操作

2. **異常變量 `as e`**:
   - 提供錯誤上下文用於日誌記錄
   - 便於調試和追蹤問題根源

3. **精確異常類型**:
   - 如果知道可能發生的異常類型，應明確指定
   - 例如網路請求常見: `requests.RequestException`, `TimeoutError`

### 檢測規則

```bash
# 使用 grep 搜索 bare except
grep -rn "except:" --include="*.py" src/ | grep -v "except Exception"
```

---

## PATTERN-002: 重複模組導入

### 錯誤症狀

```python
from src.models.sentiment_engine import SentimentEngine
from src.models.sentiment_engine import SentimentEngine  # 重複
```

**問題**:
- 浪費導入時間
- 增加代碼混亂度
- 可能是複製粘貼錯誤的徵兆

### 正確寫法

```python
from src.models.sentiment_engine import SentimentEngine
```

### 原理簡述

1. **Python 導入機制**:
   - Python 會緩存已導入的模組，重複導入不會真正重載
   - 但重複語句增加閱讀負擔

2. **自動檢測**:
   - 使用 `flake8` (F811) 或 `pylint` 可檢測重複導入
   - 使用 `isort` 可自動整理導入語句

### 檢測規則

```bash
# 使用 flake8 檢測
flake8 --select=F811 src/
```

---

## 通用最佳實踐

### 異常處理金字塔

```
精確 ───────────────────────────▶ 模糊
  │                                   │
  ▼                                   ▼
except ValueError:              except Exception:
except (KeyError, IndexError):  except:  ❌ 禁止
```

### 日誌級別選擇

| 情境 | 級別 | 示例 |
|------|------|------|
| 可預期的後備 | `logger.debug()` | 可選數據源不可用 |
| 功能降級 | `logger.warning()` | 主數據源失敗，使用備用 |
| 功能失效 | `logger.error()` | 關鍵操作失敗 |
| 需要堆棧 | `logger.exception()` | 未預期的錯誤 |

---

## Evolution Log

| 日期 | 規則 | 來源 |
|------|------|------|
| 2026-01-12 | PATTERN-001, PATTERN-002 | Audit Report (Phase 7.x) |
