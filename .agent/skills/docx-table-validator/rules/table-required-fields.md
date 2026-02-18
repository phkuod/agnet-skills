---
id: table-required-fields
title: Required Fields Check
category: table
severity: ERROR
target: table
---

## Required Fields Check

**Severity:** ERROR

No empty value is allowed in any table under the **Reliability Rules** chapter. Every cell in every column must contain a value.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: section
  section-pattern: "Reliability Rules"
  match-mode: contains
```

Tables are matched by their location under any heading containing "Reliability Rules".

### Validation Logic

For every matched table, check that **all cells in all columns** are non-empty.

**Incorrect Example:**

```
## 10.1 EM Lifetime Data

| Metal Layer  | 100°C | 150°C | 200°C |
|--------------|-------|-------|-------|
| Metal 1 (M1) | 12500 |       | 1800  |  ← 150°C is empty, ERROR
| Metal 2 (M2) | 11000 | 4500  |       |  ← 200°C is empty, ERROR
```

**Correct Example:**

```
## 10.1 EM Lifetime Data

| Metal Layer  | 100°C | 150°C | 200°C |
|--------------|-------|-------|-------|
| Metal 1 (M1) | 12500 | 5200  | 1800  |
| Metal 2 (M2) | 11000 | 4500  | 2700  |
```

### Exceptions

- Header rows are not validated
