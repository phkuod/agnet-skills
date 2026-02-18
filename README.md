# Agent Skills Repository

A collection of specialized AI agent skills that extend capabilities for complex, domain-specific tasks.

## 📁 Repository Structure

```
agnet-skills/
├── README.md                    # This file
├── CONTRIBUTING.md              # How to create new skills
├── .agent/
│   └── workflows/               # Development workflows
│       └── create-skill.md      # Workflow for creating new skills
└── {skill-name}/                # Individual skill directories
    ├── SKILL.md                 # Main skill definition (required)
    ├── rules/                   # Rule definitions (if applicable)
    ├── scripts/                 # Helper scripts
    ├── templates/               # Output templates
    ├── examples/                # Usage examples
    └── ...                      # Additional resources
```

## 🎯 Available Skills

| Skill                               | Description                                                              |
| ----------------------------------- | ------------------------------------------------------------------------ |
| [docx-validator](./docx-validator/) | Validate tables and content in DOCX documents with rule-based validation |

## 🚀 Using Skills

Skills are designed to be used by AI agents. Each skill contains a `SKILL.md` file that defines:

1. **Name & Description** - YAML frontmatter with skill metadata
2. **Dependencies** - Other skills or tools required
3. **Instructions** - Detailed usage instructions in Markdown

### Example Usage

```
Please use the docx-validator skill to validate
tables in chapter 10 of document.docx and generate a report.
```

## 📝 Creating New Skills

1. Copy the skill template: `/@create-skill {skill-name}`
2. Or manually create a new directory with `SKILL.md`

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed guidelines.

## 📋 Skill Requirements

Every skill must have:

- **SKILL.md** (required) - Main instruction file with YAML frontmatter
- Clear, actionable instructions
- Examples of usage
- Any helper scripts or resources needed

## 🔗 Related

- [Anthropic Skills Repository](https://github.com/anthropics/skills)
