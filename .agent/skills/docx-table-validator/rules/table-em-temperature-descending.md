---
id: table-em-temperature-descending
title: EM Temperature Data Descending Check
category: table
severity: ERROR
target: table
---

## EM Temperature Data Descending Check

**Severity:** ERROR

Ensure that in EM lifetime tables, MTTF/normalized values decrease monotonically as temperature increases (left to right columns). An increase at higher temperature indicates a data anomaly.

---

### Phase 1: Find Targets

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Metal Layer
  column-pattern: '\d+°C'
  match-mode: contains
```

---

### Phase 2: Apply Validation

**Validation Conditions:**

- For each row, temperature column values must be non-increasing from left to right
- If a value at a higher temperature is greater than a value at a lower temperature, this is an ERROR

**Incorrect Example:**

```
| Metal Layer   | 100°C | 120°C | 150°C | 175°C | 200°C |
|---------------|-------|-------|-------|-------|-------|
| Metal 5 (M5)  | 11000 | 7900  | 4500  | 2700  | 2900  |  ← 200°C > 175°C, ERROR
```

**Correct Example:**

```
| Metal Layer   | 100°C | 120°C | 150°C | 175°C | 200°C |
|---------------|-------|-------|-------|-------|-------|
| Metal 1 (M1)  | 12500 | 8900  | 5200  | 3100  | 1800  |  ← monotonically decreasing
```

---

### Phase 3: Collect Results

Results are automatically collected during validation. Each failure generates a result entry:

```json
{
  "rule_id": "table-em-temperature-descending",
  "status": "FAIL",
  "target": { "table_index": 3, "row": 8, "column": "200°C" },
  "message": "Value at 200°C (2900) is greater than value at 175°C (2700), expected monotonic decrease",
  "severity": "error"
}
```

---

### Exceptions

- Empty cells are skipped
- Non-numeric values are skipped with a warning
