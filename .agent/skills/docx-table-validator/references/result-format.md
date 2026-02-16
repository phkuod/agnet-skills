# Result Format Reference

Each validation produces result entries in JSON format.

---

## Failure Entry

```json
{
  "rule_id": "table-required-fields",
  "status": "FAIL",
  "target": { "table_index": 1, "row": 3, "column": "Description" },
  "message": "Field is empty",
  "severity": "error"
}
```

## Pass Entry

```json
{
  "rule_id": "table-required-fields",
  "status": "PASS",
  "target": { "table_index": 1 },
  "message": "All required fields present",
  "severity": "info"
}
```

---

## Field Descriptions

| Field      | Type   | Description                                          |
| ---------- | ------ | ---------------------------------------------------- |
| `rule_id`  | string | ID matching the rule's frontmatter `id` field        |
| `status`   | string | `PASS` or `FAIL`                                     |
| `target`   | object | Location of the validated item (varies by rule type) |
| `message`  | string | Human-readable description of the result             |
| `severity` | string | `error`, `warning`, or `info`                        |

### Target Object Variants

**For table rules:**

```json
{ "table_index": 1, "row": 3, "column": "Description" }
```

**For content rules:**

```json
{ "chapter": "10.2", "heading": "Summary", "paragraph": 1 }
```

**For structure rules:**

```json
{ "section": "Risk Assessment", "expected": true, "found": false }
```
