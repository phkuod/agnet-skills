---
id: content-date-format
title: 日期格式一致性
category: content
severity: WARNING
target: content
---

## 日期格式一致性

**嚴重程度:** WARNING

確保文件中的日期格式統一，提升可讀性和專業度。

### 目標識別

**內容匹配條件：**

```yaml
matcher:
  type: regex
  pattern: '\d{1,4}[-/年.]\d{1,2}[-/月.]\d{1,2}[日]?'
  scope: all-text
```

### 驗證邏輯

**標準日期格式：** YYYY-MM-DD 或 YYYY年MM月DD日

檢測到的日期應符合標準格式。

**錯誤範例：**

```
完成日期：2024/1/5
更新時間：24-01-05
截止日：1月5日
```

**正確範例：**

```
完成日期：2024-01-05
更新時間：2024年01月05日
截止日：2024-01-05
```

### 例外情況

表格內的日期由表格規則處理。
