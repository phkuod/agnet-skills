---
id: rule-id-here
title: Rule Title
category: table | content | structure | format
severity: ERROR | WARNING
target: table | content
script: validators/rule_script.py # Optional: corresponding Python validation script
---

## Rule Title

**Severity:** ERROR | WARNING

Brief description of the rule's purpose and why it matters.

### Target Identification

**Chapter Scope (Optional):**

```yaml
scope:
  chapters: [10, 11] # Apply only in chapters 10, 11
  chapter-pattern: "Risk.*" # Match chapter name pattern
```

**Table Matcher (when target: table):**

```yaml
matcher:
  type: column-headers
  columns:
    - Column Name 1
    - Column Name 2
  match-mode: contains | exact
```

**Content Matcher (when target: content):**

```yaml
matcher:
  type: regex
  pattern: "regular expression"
  scope: all-text | paragraphs | headings
```

### Validation Logic

> **Script Validation**: `validators/rule_script.py` (optional)

Describe the specific validation logic. If a corresponding script exists, AI will prioritize using the script for precise validation.

**Incorrect Example:**

```
| Column A | Column B |
|----------|----------|
| value    |          |  ← Column B is empty, violates rule
```

**Correct Example:**

```
| Column A | Column B |
|----------|----------|
| value    | value    |  ← All fields have values
```

### Exceptions

Describe exceptions to this rule (if any).

---

## Developing Validation Scripts

When a rule requires precise programmatic validation, create a corresponding Python script in the `validators/` directory:

### Script Template

```python
#!/usr/bin/env python3
"""
rule_script.py - Rule Validation Script

Usage:
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
    rule_name: str = "Rule Name"

def validate(table: dict) -> List[ValidationError]:
    """
    Validate table data

    Args:
        table: {"headers": [...], "rows": [[...], ...]}

    Returns:
        List of validation errors
    """
    errors = []
    # Validation logic
    return errors
```

### Naming Convention

- Rule file: `rules/{category}-{rule-name}.md`
- Script file: `validators/{category}_{rule_name}.py` (replace `-` with `_`)
