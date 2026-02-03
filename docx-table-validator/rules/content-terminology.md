---
id: content-terminology
title: 術語一致性
category: content
severity: WARNING
target: content
---

## 術語一致性

**嚴重程度:** WARNING

確保文件中的術語使用統一，避免同一概念使用多種寫法。

### 目標識別

**內容匹配條件：**

```yaml
matcher:
  type: glossary
  glossary_file: glossary/terms.md
  scope: all-text
```

### 驗證邏輯

比對 `glossary/terms.md` 中定義的術語及其變體。當發現變體寫法時發出警告。

**術語對照範例：**

| 標準術語   | 常見變體         |
| ---------- | ---------------- |
| API        | api, Api, A.P.I. |
| 使用者介面 | 用戶界面, UI     |
| 資料庫     | 数据库, DB       |

**錯誤範例：**

```
本系統提供 api 接口，用戶界面採用響應式設計。
```

**正確範例：**

```
本系統提供 API 接口，使用者介面採用響應式設計。
```

### 例外情況

程式碼區塊和引用文字中的術語不做檢查。
