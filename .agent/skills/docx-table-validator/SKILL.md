---
name: docx-table-validator
description: Validate tables and content in DOCX documents. Performs two-phase validation based on rules defined in the rules/ directory: (1) Target identification (2) Apply rules. Generates Markdown validation reports.
dependencies:
  - anthropics/skills/docx  # Depends on official DOCX SKILL for document parsing
---

# DOCX Document Validator

Validate correctness, consistency, and formatting of tables and text content in Word documents (.docx).

## Overview

This skill provides a two-phase validation workflow:

1. **Target Identification** - Identify tables by column headers, or extract content using regex
2. **Apply Rules** - Execute validation rules on identified targets

## DOCX Document Parsing

> **Dependency**: Uses [Anthropic DOCX SKILL](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md) for document parsing

### Reading Document Content

**Method 1: Convert to Markdown using Pandoc (recommended for quick analysis)**

```bash
pandoc document.docx -o output.md
```

**Method 2: Unpack OOXML for raw XML (precise table structure)**

```bash
# Use official DOCX SKILL unpack script
python ooxml/scripts/unpack.py document.docx ./unpacked/

# Key files:
# - word/document.xml  # Main document content
# - word/comments.xml  # Comments
```

**Method 3: Use this SKILL's extraction script**

```bash
python scripts/extract_tables.py document.docx --chapter 10 --output tables.json
```

### Table Extraction Workflow

```
DOCX File
    ↓
[DOCX SKILL] Unpack/Convert
    ↓
Identify Chapter → Locate Tables → Extract Fields and Content
    ↓
Output JSON Structured Data
```

---

## Two-Phase Validation Workflow

### Phase 1: Target Identification

#### Chapter Scope (Optional)

```yaml
scope:
  chapters: [10]               # Apply only in chapter 10
  chapters: [10, 11, 12]       # Apply in chapters 10, 11, 12
  chapter-pattern: 'Risk.*'    # Match chapter name pattern
```

#### Table Identification (using column headers)

```yaml
matcher:
  type: column-headers
  columns:
    - Risk ID
    - Description
    - Impact Level
```

#### Content Identification (using regex)

```yaml
matcher:
  type: regex
  pattern: '\d{4}[-/]\d{1,2}[-/]\d{1,2}'
  scope: all-text
```

### Phase 2: Apply Rules

Execute validation on identified targets, checking if they meet rule-defined conditions.

---

## Rule Structure

Rule files are located in the `rules/` directory:

```
rules/
├── _sections.md           # Rule category definitions
├── _template.md           # Rule file template
├── table-*.md             # Table validation rules
└── content-*.md           # Content validation rules
```

## Rule Categories

| Category             | Prefix       | Impact   | Description                                            |
| -------------------- | ------------ | -------- | ------------------------------------------------------ |
| Table Validation     | `table-`     | CRITICAL | Required fields, allowed values, cross-field relations |
| Content Validation   | `content-`   | HIGH     | Date format, terminology consistency                   |
| Structure Validation | `structure-` | MEDIUM   | Chapter order, required sections                       |
| Format Validation    | `format-`    | LOW      | Fonts, spacing, styles                                 |

## Existing Rules

### Table Validation (table-\*)

- `table-required-fields.md` - Required fields check
- `table-allowed-values.md` - Allowed values check
- `table-conditional-required.md` - Conditional required check
- `table-temperature-descending.md` - Temperature descending order
- `table-row-completeness.md` - Row completeness check

### Content Validation (content-\*)

- `content-date-format.md` - Date format consistency
- `content-terminology.md` - Terminology consistency

---

## Usage

### Method 1: AI Direct Validation

Ask AI to read DOCX file and apply rules:

```
Please use DOCX SKILL to read document.docx,
then validate tables in chapter 10 according to
docx-table-validator/rules/, and generate a validation report.
```

### Method 2: Using Scripts

```bash
# 1. Extract tables (using this SKILL's script)
python scripts/extract_tables.py document.docx --chapter 10 --output tables.json

# 2. Execute validation
python scripts/validate_table.py tables.json --rules rules/ --output results.json

# 3. Generate report
python scripts/generate_report.py results.json --output report.md
```

### Method 3: Combined with Official DOCX SKILL

```bash
# Use official DOCX SKILL to unpack
python ooxml/scripts/unpack.py document.docx ./unpacked/

# Then this SKILL's script can read XML
python scripts/extract_tables.py ./unpacked/ --output tables.json
```

---

## Adding New Rules

1. Copy `rules/_template.md`
2. Name according to category: `{category}-{rule-name}.md`
3. Fill in frontmatter and rule content
4. Rules will be automatically loaded

---

## Report Format

```markdown
# 📋 Document Validation Report

## 📊 Summary

| Item            | Count |
| --------------- | ----- |
| Validated Items | 5     |
| ❌ Errors       | 3     |
| ⚠️ Warnings     | 2     |

## 📑 Detailed Results

### Table 1: Risk Assessment ❌

| Row | Column      | Rule            | Issue          |
| --- | ----------- | --------------- | -------------- |
| 3   | Description | Required Fields | Field is empty |
```

---

## Dependencies

### Official DOCX SKILL (Document Parsing)

- pandoc - Text extraction
- python ooxml scripts - XML unpacking

### This SKILL's Scripts

```bash
pip install python-docx lxml
```
