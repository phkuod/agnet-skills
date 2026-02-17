---
name: docx-table-validator
description: Validate tables and content in DOCX documents using rule-based validation. Use when asked to "check this Word document", "validate the tables", "audit document data", "verify formatting compliance", "review document quality", or "check terminology consistency". Also handles AIP-encrypted DOCX files. Supports checking required fields, allowed values, date formats, terminology consistency, and structural completeness.
compatibility: Requires anthropics/skills/docx skill for DOCX parsing and aip-decrypt skill for AIP-encrypted files.
metadata:
  author: phkuo
  version: 1.2.0
  category: document-validation
  tags: [docx, validation, tables, compliance, audit]
  dependencies: [anthropics/skills/docx, aip-decrypt]
---

# DOCX Document Validator

Validate correctness, consistency, and formatting of tables and text content in `.docx` files.

## Instructions

Copy this checklist and track progress:

```
Validation Progress:
- [ ] Step 1: Decrypt document (if AIP-encrypted)
- [ ] Step 2: Parse document content
- [ ] Step 3: Run validation rules
- [ ] Step 4: Generate report
```

### Step 1: Decrypt (skip if not encrypted)

Use `aip-decrypt` skill to decrypt the file, producing a decrypted `.docx`.

### Step 2: Parse Document

Use DOCX skill to read document content.

- **Default method** — convert with pandoc: `pandoc doc.docx -o output.md`
- **For precise table XML** — unpack with OOXML: `python ooxml/scripts/unpack.py doc.docx ./unpacked/`

> Choose OOXML when tables contain merged cells, nested structures, or when pandoc output loses table formatting.

### Step 3: Validate

Apply rules from `rules/` directory. Each rule follows three phases:

| Phase        | Action                                                |
| ------------ | ----------------------------------------------------- |
| **Find**     | Identify target tables/content using matchers         |
| **Validate** | Check each target against rule conditions → PASS/FAIL |
| **Collect**  | Store results for report                              |

**Matchers:** See [references/matchers.md](references/matchers.md) for full matcher documentation.

### Step 4: Report

Generate a Markdown report from collected results.

- **Template:** [templates/report.md](templates/report.md)
- **Example:** [examples/sample-report.md](examples/sample-report.md)

---

## Rules

**Categories:** See [rules/\_sections.md](rules/_sections.md) for definitions.
**Template:** See [rules/\_template.md](rules/_template.md) to create new rules.

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

## Examples

### Example 1: Validate a risk assessment document

**User says:** "Check this risk assessment DOCX for data completeness"

**Steps executed:**

1. Parse with pandoc → `output.md`
2. Apply rules: `table-required-fields`, `table-allowed-values`, `table-conditional-required`
3. Generate report with per-table pass/fail details

**Result:** Markdown report showing 3 tables validated, 5 errors, 2 warnings with row/column locations.

### Example 2: Check terminology consistency

**User says:** "Audit this document for terminology issues"

**Steps executed:**

1. Parse with pandoc → `output.md`
2. Apply rule: `content-terminology` using [glossary/terms.md](glossary/terms.md)
3. Report non-standard variants found

**Result:** List of non-standard terms with suggested replacements (e.g., "DB" → "Database").

### Example 3: Validate encrypted document

**User says:** "Validate this AIP-encrypted DOCX"

**Steps executed:**

1. Decrypt using `aip-decrypt` skill → decrypted `.docx`
2. Parse with pandoc → `output.md`
3. Apply all applicable rules
4. Generate report

**Result:** Full validation report identical to unencrypted workflow.

---

## Troubleshooting

### Error: No tables found in document

**Cause:** Document was parsed as markdown but tables are embedded as images or non-standard XML.
**Solution:** Use OOXML unpacking instead of pandoc: `python ooxml/scripts/unpack.py doc.docx ./unpacked/`

### Error: Rule file not recognized

**Cause:** Rule file missing YAML frontmatter or incorrect category prefix.
**Solution:** Verify file follows `rules/{category}-{name}.md` naming and has required frontmatter fields (`id`, `title`, `category`, `severity`, `target`).

### Error: AIP decryption failed

**Cause:** Missing `aip-decrypt` skill or invalid credentials.
**Solution:** Ensure `aip-decrypt` skill is installed and authentication is configured.

### Error: Pandoc conversion loses table structure

**Cause:** Complex tables with merged cells or nested content.
**Solution:** Switch to OOXML parsing: `python ooxml/scripts/unpack.py doc.docx ./unpacked/`

### Error: Matcher finds no matching tables

**Cause:** Column headers in the document don't match the matcher's expected headers (case or wording mismatch).
**Solution:** Check actual column headers in the parsed output and update the rule's matcher `columns` list to match exactly.

---

## Scripts

Validation and report generation scripts in `scripts/`:

```bash
python scripts/validate_table.py tables.json --rules rules/ -o results.json
python scripts/generate_report.py results.json -o report.md
```

---

## Reference Files

- **Matchers:** [references/matchers.md](references/matchers.md) — full matcher syntax and options
- **Result format:** [references/result-format.md](references/result-format.md) — JSON result schema
- **Rules:** [rules/](rules/) — all rule definitions
- **Glossary:** [glossary/terms.md](glossary/terms.md) — terminology reference
- **Validators:** [validators/](validators/) — Python validation scripts
