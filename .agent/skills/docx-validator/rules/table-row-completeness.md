---
id: table-row-completeness
title: Row Completeness Check
category: table
severity: ERROR
target: table
---

## Row Completeness Check

**Severity:** ERROR

When the first column of a table has a value, indicating it's a valid data row, all subsequent columns cannot be empty.

### Target Identification

**Table Matcher:**

```yaml
matcher:
  type: any-table
  # This rule applies to all tables
```

### Validation Logic

**Rule:** If row[first column] has value, then row[all other columns] must have values.

**Check Process:**

1. Check first column of each row
2. If first column has value (not empty)
3. Then check all other columns in that row
4. If any column is empty, flag as error

**Incorrect Example:**

```
| ID   | Name      | Quantity | Notes  |
|------|-----------|----------|--------|
| 001  | Product A | 100      | Normal |
| 002  | Product B |          |        |  ← Error: ID has value, but Quantity and Notes are empty
| 003  |           | 50       | Test   |  ← Error: ID has value, but Name is empty
```

**Correct Example:**

```
| ID   | Name      | Quantity | Notes  |
|------|-----------|----------|--------|
| 001  | Product A | 100      | Normal |
| 002  | Product B | 200      | Normal |
|      |           |          |        |  ← Correct: First column is empty, entire row can be empty
```

**Another Correct Example (empty rows allowed):**

```
| ID   | Name      | Quantity |
|------|-----------|----------|
| 001  | Product A | 100      |
|      |           |          |  ← Correct: Not checked when first column is empty
| 003  | Product C | 300      |
```

### Exceptions

- Rows with empty first column do not trigger this rule (treated as blank or separator rows)
- Header row is not validated
