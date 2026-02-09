---
id: table-required-fields
title: Required Fields Check
category: table
severity: ERROR
target: table
---

## Required Fields Check

**Severity:** ERROR

Ensure required fields in tables are not empty. Empty values may cause incomplete data or processing failures.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Risk ID
    - Description
    - Impact Level
    - Probability
```

### Validation Logic

Check that all cells in specified columns have values.

**Required Fields:**

- Risk ID
- Description
- Impact Level
- Probability

**Incorrect Example:**

```
| Risk ID | Description    | Impact Level | Probability |
|---------|----------------|--------------|-------------|
| R001    | System failure | High         | Medium      |
| R002    |                | Low          |             |  ← Description and Probability are empty
```

**Correct Example:**

```
| Risk ID | Description    | Impact Level | Probability |
|---------|----------------|--------------|-------------|
| R001    | System failure | High         | Medium      |
| R002    | Data loss      | Low          | Low         |
```

### Exceptions

None.
