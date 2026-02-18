# Contributing to Agent Skills

This guide explains how to create and contribute new skills to this repository.

## Skill Structure

Each skill is a self-contained directory with the following structure:

```
{skill-name}/
├── SKILL.md           # Required: Main skill definition
├── scripts/           # Optional: Helper scripts
├── rules/             # Optional: Rule definitions
├── templates/         # Optional: Output/report templates
├── examples/          # Optional: Usage examples
├── glossary/          # Optional: Domain terminology
└── validators/        # Optional: Validation logic
```

## SKILL.md Format

The `SKILL.md` file is the entry point for every skill. It must follow this format:

```markdown
---
name: { skill-name }
description: { brief description of what the skill does }
dependencies:
  - { optional: list of other skills this depends on }
---

# {Skill Title}

{Overview of the skill and its purpose}

## Overview

{High-level description of what this skill provides}

## Usage

{How to use this skill - both AI-driven and script-based methods}

## Features

{List of key features}

## Examples

{Usage examples}

## Dependencies

{Required tools, packages, or other skills}
```

## Naming Conventions

| Item            | Convention                 | Example                    |
| --------------- | -------------------------- | -------------------------- |
| Skill directory | lowercase with hyphens     | `docx-validator`           |
| SKILL.md        | Exactly `SKILL.md`         | Required                   |
| Rule files      | `{category}-{name}.md`     | `table-required-fields.md` |
| Scripts         | lowercase with underscores | `extract_tables.py`        |

## Creating a New Skill

### Option 1: Use the Workflow

```
/@create-skill my-new-skill
```

### Option 2: Manual Creation

1. Create a new directory: `mkdir my-new-skill`
2. Create `SKILL.md` with the required frontmatter
3. Add supporting files as needed
4. Test the skill with example usage

## Best Practices

### 1. Clear Instructions

- Write instructions that are clear to both humans and AI agents
- Include step-by-step workflows where applicable
- Provide examples for complex operations

### 2. Modular Design

- Keep skills focused on a single domain or task
- Use dependencies for shared functionality
- Avoid duplicating logic across skills

### 3. Documentation

- Document all scripts with usage examples
- Include expected input/output formats
- Provide sample data in the `examples/` directory

### 4. Error Handling

- Define clear error conditions
- Provide troubleshooting guidance
- Include validation for inputs

## Checklist for New Skills

- [ ] SKILL.md with proper YAML frontmatter
- [ ] Clear description of the skill's purpose
- [ ] Usage instructions (AI and/or script-based)
- [ ] At least one example
- [ ] Dependencies documented
- [ ] Helper scripts have docstrings/comments
- [ ] README or examples for complex features
