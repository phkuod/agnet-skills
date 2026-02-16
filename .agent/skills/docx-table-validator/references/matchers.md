# Target Matchers Reference

Matchers define what to validate (used in the Find phase of each rule).

---

## Table Matcher

Identify tables by column headers:

```yaml
matcher:
  type: column-headers
  columns: [Risk ID, Description, Impact Level]
  match-mode: contains # or exact
```

- `contains` — table must have at least these columns (may have more)
- `exact` — table must have exactly these columns

---

## Content Matcher — Regex

Find text by regular expression pattern:

```yaml
matcher:
  type: regex
  pattern: '\d{4}[-/]\d{1,2}[-/]\d{1,2}'
  scope: all-text # or paragraphs, headings
```

**Scope values:**

| Scope        | Description                     |
| ------------ | ------------------------------- |
| `all-text`   | Search all text in the document |
| `paragraphs` | Search only paragraph body text |
| `headings`   | Search only heading text        |

---

## Content Matcher — Heading Path

Extract text under a specific heading hierarchy:

```yaml
matcher:
  type: heading-path
  path: "10.2 > Risk Summary"
  scope: paragraphs
```

The `>` separator navigates the heading hierarchy. Text between the target heading and the next sibling heading is extracted.

---

## Chapter Scope (Optional)

Combinable with any matcher to restrict validation to specific chapters:

```yaml
scope:
  chapters: [10, 11, 12]
  chapter-pattern: "Risk.*"
```

- `chapters` — list of chapter numbers to include
- `chapter-pattern` — regex pattern to match chapter names
