---
id: table-temperature-descending
title: 溫度遞減順序檢查
category: table
severity: ERROR
target: table
script: validators/table_temperature_descending.py
---

## 溫度遞減順序檢查

**嚴重程度:** ERROR

確保溫度表格中，當 Temperature 值越高時，對應的「攝氏溫度值」欄位數值應越低，整體呈現遞減排序。

### 目標識別

**章節限定：**

```yaml
scope:
  chapters: [10] # 只在第 10 章套用此規則
```

**表格匹配條件：**

```yaml
matcher:
  type: column-headers
  columns:
    - Temperature
    - 攝氏溫度值
```

### 驗證邏輯

> **腳本驗證**: `validators/table_temperature_descending.py`

**規則：** 依 Temperature 欄位由高到低排序時，「攝氏溫度值」欄位的數值必須呈現遞減（或相等）。

**錯誤範例：**

```
| Temperature | 攝氏溫度值 |
|-------------|------------|
| 100         | 50         |
| 80          | 60         |  ← 錯誤：Temperature 降低，但攝氏溫度值反而升高
```

**正確範例：**

```
| Temperature | 攝氏溫度值 |
|-------------|------------|
| 100         | 80         |
| 80          | 60         |
| 60          | 40         |
```

### 例外情況

- 空值不參與排序驗證
- 非數值內容會被跳過並發出警告
