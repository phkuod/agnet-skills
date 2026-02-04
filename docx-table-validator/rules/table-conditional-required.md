---
id: table-conditional-required
title: Conditional Required Check
category: table
severity: ERROR
target: table
---

## Conditional Required Check

**Severity:** ERROR

When a column matches a specific condition, another column must have a value. This ensures related data completeness.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Impact Level
    - Mitigation
```

### Validation Logic

**Conditional Rule:**

- When "Impact Level" = "High", "Mitigation" cannot be empty

**Incorrect Example:**

```
| Risk ID | Impact Level | Mitigation |
|---------|--------------|------------|
| R001    | High         |            |  ← Impact is High, but Mitigation is empty
```

**Correct Example:**

```
| Risk ID | Impact Level | Mitigation           |
|---------|--------------|----------------------|
| R001    | High         | Add redundant system |
| R002    | Low          |                      |  ← Impact is Low, Mitigation can be empty
```

### Exceptions

When trigger condition column is empty, this rule is not triggered.
