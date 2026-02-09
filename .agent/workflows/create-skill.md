---
description: Create a new agent skill from template
---

# Create Skill Workflow

This workflow creates a new skill directory with the proper structure.

## Usage

```
/@create-skill {skill-name}
```

## Steps

1. **Validate skill name**
   - Must be lowercase with hyphens
   - Must not already exist

2. **Create skill directory structure**

   ```
   {skill-name}/
   ├── SKILL.md
   ├── scripts/
   ├── examples/
   └── templates/
   ```

3. **Create SKILL.md with template**

   ```markdown
   ---
   name: { skill-name }
   description: { description to be filled }
   ---

   # {Skill Title}

   {Overview}

   ## Usage

   {How to use this skill}

   ## Features

   - Feature 1
   - Feature 2

   ## Examples

   {Usage examples}

   ## Dependencies

   {Required tools or other skills}
   ```

4. **Create placeholder files**
   - `scripts/.gitkeep`
   - `examples/.gitkeep`
   - `templates/.gitkeep`

5. **Output success message**
   - Confirm skill was created
   - Remind user to fill in SKILL.md details
