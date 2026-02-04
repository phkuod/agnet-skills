---
id: content-date-format
title: Date Format Consistency
category: content
severity: WARNING
target: content
---

## Date Format Consistency

**Severity:** WARNING

Ensure date formats in the document are uniform, improving readability and professionalism.

### Target Identification

**Content Matcher:**

```yaml
matcher:
  type: regex
  pattern: '\d{1,4}[-/年.]\d{1,2}[-/月.]\d{1,2}[日]?'
  scope: all-text
```

### Validation Logic

**Standard Date Formats:** YYYY-MM-DD or YYYY/MM/DD

Detected dates should conform to standard format.

**Incorrect Example:**

```
Completion date: 2024/1/5
Update time: 24-01-05
Deadline: Jan 5
```

**Correct Example:**

```
Completion date: 2024-01-05
Update time: 2024/01/05
Deadline: 2024-01-05
```

### Exceptions

Dates within tables are handled by table rules.
