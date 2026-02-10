---
name: docx-table-validator
description: Validate tables and content in DOCX documents using rule-based validation. Use when asked to check, verify, or audit a Word document for data correctness, table completeness, terminology consistency, or formatting compliance. Also use when processing AIP-encrypted DOCX files for validation.
dependencies:
  - anthropics/skills/docx
  - aip-decrypt
---

# DOCX Document Validator

Validate correctness, consistency, and formatting of tables and text content in `.docx` files.

## Workflow

Copy this checklist and track progress:

````
Validation Progress:
- [ ] Step 1: Decrypt document (if AIP-encrypted)
- [ ] Step 2: Parse document content
- [ ] Step 3: Run validation rules
- [ ] Step 4: Generate report

```mermaid
flowchart LR
    Start([Start]) --> Encrypted{Encrypted?}
    Encrypted -- Yes --> Decrypt[Step 1: Decrypt]
    Encrypted -- No --> Parse[Step 2: Parse]
    Decrypt --> Parse
    Parse --> Validate[Step 3: Validate]
    Validate --> Report[Step 4: Report]
    Report --> End([End])
````

````

**Step 1: Decrypt** (skip if not encrypted)

Use `aip-decrypt` SKILL to decrypt the file, producing a decrypted `.docx`.

**Step 2: Parse**

Use DOCX SKILL to read document content. Default: convert with `pandoc doc.docx -o output.md`. For precise table XML structure, unpack with OOXML: `python ooxml/scripts/unpack.py doc.docx ./unpacked/`.

**Step 3: Validate**

Apply rules from `rules/` directory. Each rule follows three phases:

| Phase        | Action                                                |
| ------------ | ----------------------------------------------------- |
| **Find**     | Identify target tables/content using matchers         |
| **Validate** | Check each target against rule conditions → PASS/FAIL |
| **Collect**  | Store results for report                              |

**Step 4: Report**

Generate a Markdown report from collected results.
See [templates/report.md](templates/report.md) for format template.
See [examples/sample-report.md](examples/sample-report.md) for complete example.

---

## Target Matchers

Matchers define what to validate (used in Find phase).

**Table matcher** — identify tables by column headers:

```yaml
matcher:
  type: column-headers
  columns: [Risk ID, Description, Impact Level]
  match-mode: contains # or exact
````

**Content matcher** — find text by regex:

```yaml
matcher:
  type: regex
  pattern: '\d{4}[-/]\d{1,2}[-/]\d{1,2}'
  scope: all-text # or paragraphs, headings
```

**Content matcher** — extract text under heading:

```yaml
matcher:
  type: heading-path
  path: "10.2 > Risk Summary"
  scope: paragraphs
```

**Chapter scope** (optional, combinable with any matcher):

```yaml
scope:
  chapters: [10, 11, 12]
  chapter-pattern: "Risk.*"
```

---

## Rules

**Rule categories:** See [rules/\_sections.md](rules/_sections.md) for definitions.
**Rule template:** See [rules/\_template.md](rules/_template.md) to create new rules.

| Category  | Prefix       | Severity |
| --------- | ------------ | -------- |
| Table     | `table-`     | CRITICAL |
| Content   | `content-`   | HIGH     |
| Structure | `structure-` | MEDIUM   |
| Format    | `format-`    | LOW      |

### Existing rules

**Table:** `table-required-fields` · `table-allowed-values` · `table-conditional-required` · `table-temperature-descending` · `table-row-completeness`

**Content:** `content-date-format` · `content-terminology` · `content-paragraph-extract`

### Adding new rules

1. Copy `rules/_template.md` → `rules/{category}-{name}.md`
2. Set frontmatter: `id`, `title`, `category`, `severity`, `target`
3. Define **Find** (matcher), **Validate** (logic + examples), **Collect** (auto)
4. _(Optional)_ Add script: `validators/{category}_{name}.py`

---

## Result format

Each validation failure:

```json
{
  "rule_id": "table-required-fields",
  "status": "FAIL",
  "target": { "table_index": 1, "row": 3, "column": "Description" },
  "message": "Field is empty",
  "severity": "error"
}
```

---

## Scripts

Validation and report generation scripts in `scripts/`:

```bash
python scripts/validate_table.py tables.json --rules rules/ -o results.json
python scripts/generate_report.py results.json -o report.md
```

---

## Reference files

**Rules:** See [rules/](rules/) for all rule definitions
**Glossary:** See [glossary/terms.md](glossary/terms.md) for terminology reference
**Validators:** See [validators/](validators/) for Python validation scripts
