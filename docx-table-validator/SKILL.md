---
name: docx-table-validator
description: 驗證 DOCX 文件中的表格和內容。根據 rules/ 目錄中定義的規則進行兩階段驗證：(1) 識別目標 (2) 套用規則。產生 Markdown 格式的驗證報告。
dependencies:
  - anthropics/skills/docx # 依賴官方 DOCX SKILL 進行文件解析
---

# DOCX 文件驗證器

驗證 Word 文件 (.docx) 中的表格內容和文字內容的正確性、一致性和格式規範。

## 概述

此技能提供兩階段驗證流程：

1. **識別目標** - 根據 column headers 識別表格，或使用 regex 抓取內容
2. **套用規則** - 對識別的目標執行驗證規則

## DOCX 文件解析

> **依賴**: 使用 [Anthropic DOCX SKILL](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md) 進行文件解析

### 讀取文件內容

**方式 1：使用 Pandoc 轉換 Markdown（推薦用於快速分析）**

```bash
pandoc document.docx -o output.md
```

**方式 2：解包 OOXML 取得原始 XML（精確表格結構）**

```bash
# 使用官方 DOCX SKILL 的 unpack 腳本
python ooxml/scripts/unpack.py document.docx ./unpacked/

# 主要檔案：
# - word/document.xml  # 主文件內容
# - word/comments.xml  # 註解
```

**方式 3：使用本 SKILL 的提取腳本**

```bash
python scripts/extract_tables.py document.docx --chapter 10 --output tables.json
```

### 表格提取流程

```
DOCX 檔案
    ↓
[DOCX SKILL] 解包/轉換
    ↓
識別章節 → 定位表格 → 提取欄位和內容
    ↓
輸出 JSON 結構化資料
```

---

## 兩階段驗證流程

### 階段 1：識別目標

#### 章節限定（可選）

```yaml
scope:
  chapters: [10]               # 只在第 10 章
  chapters: [10, 11, 12]       # 在第 10、11、12 章
  chapter-pattern: '風險.*'    # 章節名稱匹配
```

#### 表格識別（使用 column headers）

```yaml
matcher:
  type: column-headers
  columns:
    - 風險編號
    - 風險描述
    - 影響程度
```

#### 內容識別（使用 regex）

```yaml
matcher:
  type: regex
  pattern: '\d{4}[-/年]\d{1,2}[-/月]\d{1,2}'
  scope: all-text
```

### 階段 2：套用規則

對識別到的目標執行驗證，檢查是否符合規則定義的條件。

---

## 規則結構

規則檔案位於 `rules/` 目錄：

```
rules/
├── _sections.md           # 規則分類定義
├── _template.md           # 規則檔案模板
├── table-*.md             # 表格驗證規則
└── content-*.md           # 內容驗證規則
```

## 規則分類

| 分類     | 前綴         | 影響程度 | 說明                           |
| -------- | ------------ | -------- | ------------------------------ |
| 表格驗證 | `table-`     | CRITICAL | 必填欄位、值域限制、跨欄位關聯 |
| 內容驗證 | `content-`   | HIGH     | 日期格式、術語一致性           |
| 結構驗證 | `structure-` | MEDIUM   | 章節順序、必要章節             |
| 格式驗證 | `format-`    | LOW      | 字體、間距等樣式               |

## 現有規則

### 表格驗證 (table-\*)

- `table-required-fields.md` - 必填欄位檢查
- `table-allowed-values.md` - 值域限制檢查
- `table-conditional-required.md` - 條件必填檢查
- `table-temperature-descending.md` - 溫度遞減順序
- `table-row-completeness.md` - 行完整性檢查

### 內容驗證 (content-\*)

- `content-date-format.md` - 日期格式一致性
- `content-terminology.md` - 術語一致性

---

## 使用方式

### 方式 1：AI 直接驗證

請 AI 讀取 DOCX 檔案並套用規則：

```
請使用 DOCX SKILL 讀取 document.docx，
然後根據 docx-table-validator/rules/ 中的規則
驗證第 10 章的表格，產生驗證報告。
```

### 方式 2：使用腳本

```bash
# 1. 提取表格（使用本 SKILL 腳本）
python scripts/extract_tables.py document.docx --chapter 10 --output tables.json

# 2. 執行驗證
python scripts/validate_table.py tables.json --rules rules/ --output results.json

# 3. 產生報告
python scripts/generate_report.py results.json --output report.md
```

### 方式 3：結合官方 DOCX SKILL

```bash
# 使用官方 DOCX SKILL 解包
python ooxml/scripts/unpack.py document.docx ./unpacked/

# 然後本 SKILL 的腳本可讀取 XML
python scripts/extract_tables.py ./unpacked/ --output tables.json
```

---

## 新增規則

1. 複製 `rules/_template.md`
2. 根據分類命名：`{category}-{rule-name}.md`
3. 填寫 frontmatter 和規則內容
4. 規則會自動被載入使用

---

## 報告格式

```markdown
# 📋 文件驗證報告

## 📊 摘要

| 項目       | 數量 |
| ---------- | ---- |
| 驗證項目數 | 5    |
| ❌ 錯誤    | 3    |
| ⚠️ 警告    | 2    |

## 📑 詳細結果

### 表格 1：風險評估表 ❌

| 行號 | 欄位     | 規則         | 問題     |
| ---- | -------- | ------------ | -------- |
| 3    | 風險描述 | 必填欄位檢查 | 欄位為空 |
```

---

## 依賴

### 官方 DOCX SKILL（文件解析）

- pandoc - 文字提取
- python ooxml 腳本 - XML 解包

### 本 SKILL 腳本

```bash
pip install python-docx lxml
```
