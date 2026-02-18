---
id: table-risk-required-fields
title: Risk Assessment Required Fields
category: table
severity: ERROR
target: table
---

## Risk Assessment Required Fields

**Severity:** ERROR

Ensure all required fields in risk assessment tables are filled.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: column-headers
  columns:
    - Risk Item
    - Severity
    - Owner
    - Due Date
```

## Validation Rules

### Required Fields [ERROR]

All columns must not be empty. Required fields:

- Risk Item
- Severity
- Likelihood
- Mitigation Status
- Owner
- Due Date

### Date Format [WARNING]

Date format must match regex `^\d{4}-\d{2}-\d{2}$`

- Due Date
