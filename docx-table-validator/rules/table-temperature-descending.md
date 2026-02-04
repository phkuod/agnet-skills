---
id: table-temperature-descending
title: Temperature Descending Order Check
category: table
severity: ERROR
target: table
script: validators/table_temperature_descending.py
---

## Temperature Descending Order Check

**Severity:** ERROR

Ensure in temperature tables, when Temperature value is higher, the corresponding "Celsius Value" column should be lower, showing a descending pattern.

### Target Identification

**Chapter Scope:**

```yaml
scope:
  chapters: [10] # Apply only in chapter 10
```

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Temperature
    - Celsius Value
```

### Validation Logic

> **Script Validation**: `validators/table_temperature_descending.py`

**Rule:** When sorted by Temperature column from high to low, "Celsius Value" column must show descending (or equal) values.

**Incorrect Example:**

```
| Temperature | Celsius Value |
|-------------|---------------|
| 100         | 50            |
| 80          | 60            |  ← Error: Temperature decreased, but Celsius Value increased
| 60          | 40            |
```

**Correct Example:**

```
| Temperature | Celsius Value |
|-------------|---------------|
| 100         | 80            |
| 80          | 60            |
| 60          | 40            |
```

### Exceptions

- Empty values do not participate in order validation
- Non-numeric content is skipped with a warning
