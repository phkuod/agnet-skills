---
id: content-terminology
title: Terminology Consistency
category: content
severity: WARNING
target: content
---

## Terminology Consistency

**Severity:** WARNING

Ensure consistent terminology throughout the document, avoiding multiple spellings for the same concept.

### Target Identification

**Content Matcher:**

```yaml
matcher:
  type: glossary
  glossary_file: glossary/terms.md
  scope: all-text
```

### Validation Logic

Compare against terms and variants defined in `glossary/terms.md`. Issue warning when variant spellings are found.

**Terminology Reference Example:**

| Standard Term  | Common Variants         |
| -------------- | ----------------------- |
| API            | api, Api, A.P.I.        |
| User Interface | user interface, UI, gui |
| Database       | database, DB, data base |

**Incorrect Example:**

```
This system provides an api interface with a user interface using responsive design.
```

**Correct Example:**

```
This system provides an API interface with a User Interface using responsive design.
```

### Exceptions

Terms within code blocks and quoted text are not checked.
