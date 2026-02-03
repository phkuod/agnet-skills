---
id: rule-id-here
title: 規則標題
category: table | content | structure | format
severity: ERROR | WARNING
target: table | content
script: validators/rule_script.py # 可選：對應的 Python 驗證腳本
---

## 規則標題

**嚴重程度:** ERROR | WARNING

簡短說明此規則的用途和為什麼重要。

### 目標識別

**章節限定（可選）：**

```yaml
scope:
  chapters: [10, 11] # 只在第 10、11 章套用
  chapter-pattern: "風險.*" # 章節名稱匹配正則
```

**表格匹配條件（當 target: table）：**

```yaml
matcher:
  type: column-headers
  columns:
    - 欄位名稱1
    - 欄位名稱2
  match-mode: contains | exact
```

**內容匹配條件（當 target: content）：**

```yaml
matcher:
  type: regex
  pattern: "正則表達式"
  scope: all-text | paragraphs | headings
```

### 驗證邏輯

> **腳本驗證**: `validators/rule_script.py`（可選）

說明驗證的具體邏輯。若有對應腳本，AI 會優先使用腳本執行精確驗證。

**錯誤範例：**

```
| 欄位A | 欄位B |
|-------|-------|
| 值    |       |  ← 欄位B 為空，違反規則
```

**正確範例：**

```
| 欄位A | 欄位B |
|-------|-------|
| 值    | 值    |  ← 所有欄位都有值
```

### 例外情況

說明此規則的例外情況（如果有）。

---

## 開發驗證腳本

當規則需要精確的程式化驗證時，可以在 `validators/` 目錄建立對應的 Python 腳本：

### 腳本模板

```python
#!/usr/bin/env python3
"""
rule_script.py - 規則驗證腳本

用法：
    python validators/rule_script.py <table_json>

    from validators.rule_script import validate
    errors = validate(table_data)
"""

from dataclasses import dataclass
from typing import List

@dataclass
class ValidationError:
    row: int
    column: str
    message: str
    severity: str = "error"
    rule_id: str = "rule-id"
    rule_name: str = "規則名稱"

def validate(table: dict) -> List[ValidationError]:
    """
    驗證表格資料

    Args:
        table: {"headers": [...], "rows": [[...], ...]}

    Returns:
        驗證錯誤列表
    """
    errors = []
    # 驗證邏輯
    return errors
```

### 命名規範

- 規則檔案：`rules/{category}-{rule-name}.md`
- 腳本檔案：`validators/{category}_{rule_name}.py`（將 `-` 改為 `_`）
