---
id: content-paragraph-extract
title: Paragraph Text Extraction and Validation
category: content
severity: WARNING
target: content
---

## Paragraph Text Extraction and Validation

**Severity:** WARNING

Extract and validate specific paragraph text from designated sections. Ensures critical sections contain required information patterns.

---

### Phase 1: Find Targets

**Chapter Scope:**

```yaml
scope:
  chapters: [10]
```

**Content Matcher (Option A - Regex):**

```yaml
matcher:
  type: regex
  pattern: 'Version:\s*\d+\.\d+(\.\d+)?'
  scope: paragraphs
```

**Content Matcher (Option B - Heading Path):**

```yaml
matcher:
  type: heading-path
  path: "10.2 > Summary"
  scope: paragraphs
```

This will locate all paragraph text under the heading path `Chapter 10.2 → Summary`.

---

### Phase 2: Apply Validation

**Validation Logic:**

1. **Presence check** — The target section must contain at least one matching paragraph
2. **Format check** — Extracted text must match the expected pattern
3. **Consistency check** — Values extracted from multiple locations must be consistent

**Example: Version String Validation**

**Incorrect Example:**

```
10.2 Summary

This document describes the system architecture.
Product version: v2.1
```

↑ Version format `v2.1` does not match expected pattern `Version: X.Y.Z`

**Correct Example:**

```
10.2 Summary

This document describes the system architecture.
Version: 2.1.0
```

↑ Version format matches `Version: X.Y.Z`

**Example: Heading Path Extraction**

To extract all paragraphs under "10.2 > Risk Summary":

```
10.2 Risk Assessment
  ...
  Risk Summary           ← Target heading
    Paragraph 1 text     ← Extracted
    Paragraph 2 text     ← Extracted
  Risk Details           ← Stop here (next sibling heading)
```

---

### Phase 3: Collect Results

```json
{
  "rule_id": "content-paragraph-extract",
  "status": "FAIL",
  "target": { "chapter": "10.2", "heading": "Summary", "paragraph": 1 },
  "message": "Version format 'v2.1' does not match expected pattern 'Version: X.Y.Z'",
  "severity": "warning"
}
```

**Pass criteria:** All paragraphs in the target section contain text matching the required patterns.

---

### Exceptions

- Empty sections are flagged as WARNING (section exists but has no content)
- Code blocks and quoted text are not validated
- If the target heading path does not exist, the rule is skipped with a note in the report
