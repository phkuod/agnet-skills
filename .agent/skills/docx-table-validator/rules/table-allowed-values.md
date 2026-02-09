---
id: table-allowed-values
title: Allowed Values Check
category: table
severity: ERROR
target: table
---

## Allowed Values Check

**Severity:** ERROR

Ensure specific column values are within the allowed range. Non-standard values may cause data inconsistency.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Impact Level
    - Probability
```

### Validation Logic

Check that column values are in the allowed list.

**Column: Impact Level**
Allowed values:

- High
- Medium
- Low

**Column: Probability**
Allowed values:

- High
- Medium
- Low

**Incorrect Example:**

```
| Risk ID | Impact Level | Probability |
|---------|--------------|-------------|
| R001    | Severe       | Very High   |  ← "Severe" and "Very High" not in allowed values
```

**Correct Example:**

```
| Risk ID | Impact Level | Probability |
|---------|--------------|-------------|
| R001    | High         | High        |
```

### Exceptions

Empty values do not trigger this rule (handled by `table-required-fields`).
