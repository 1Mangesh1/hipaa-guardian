# dev-skills

**Version 1.0.0**
1mangesh1
February 2026

> **Note:**
> This document provides guidance to AI agents and LLMs when working with skills
> in this collection. Each skill has its own AGENTS.md with detailed instructions.

---

## Overview

This is a multi-skill collection following the Agent Skills standard. Skills are
self-contained packages that can be installed individually or as a collection.

## Available Skills

| Skill | Version | Entry Point | Description |
|-------|---------|-------------|-------------|
| [hipaa-guardian](./skills/hipaa-guardian/) | 1.2.0 | `SKILL.md` | HIPAA compliance, PHI/PII detection, healthcare format support |

## Installation

```bash
# Install all skills
npx skills add 1Mangesh1/dev-skills

# Install specific skill
npx skills add 1Mangesh1/dev-skills --skill hipaa-guardian
```

## Skill Discovery

When a user request matches a skill's activation triggers, follow that skill's
AGENTS.md for detailed instructions:

### hipaa-guardian

**Triggers:** "scan for PHI", "detect PII", "HIPAA compliance", "check for protected
health information", "scan logs for PHI", "check authentication on PHI endpoints",
"FHIR", "HL7", "CDA"

**Agent Guide:** `skills/hipaa-guardian/AGENTS.md`

---

## Repository Structure

```
dev-skills/
├── README.md                    # Collection overview
├── AGENTS.md                    # This file
├── CLAUDE.md                    # Development guidance
├── package.json                 # npm metadata
├── .claude-plugin/
│   └── marketplace.json         # Claude Code plugin config
└── skills/
    └── hipaa-guardian/          # Self-contained skill
        ├── SKILL.md             # Skill definition (entry point)
        ├── README.md            # Human documentation
        ├── AGENTS.md            # Agent-specific guidance
        ├── agent-skills.json    # Skill manifest
        ├── scripts/             # Executable scripts
        ├── references/          # Knowledge base
        └── examples/            # Sample outputs
```

## Skill Structure Standard

Each skill in this collection follows this structure:

### Required Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Primary entry point with skill definition and workflow |
| `README.md` | Human-readable documentation |
| `AGENTS.md` | Agent/LLM-optimized instructions |
| `agent-skills.json` | Skill manifest with capabilities and metadata |

### Optional Directories

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Executable Python/Shell scripts |
| `references/` | Knowledge base and detection patterns |
| `examples/` | Sample outputs and test data |

## Adding to This Collection

When adding a new skill:

1. Create `skills/<skill-name>/` directory
2. Include all required files (SKILL.md, README.md, AGENTS.md, agent-skills.json)
3. Update root `package.json` with skill metadata
4. Update `.claude-plugin/marketplace.json`
5. Add skill to table in this file

## Security Notes

All skills in this collection follow security best practices:

- Never output sensitive data in plain text
- Use hashes or [REDACTED] for sensitive values
- Default to synthetic/test data mode
- Clean up temporary files after processing
- Warn before processing potentially real sensitive data

---

## Quick Reference

For skill-specific guidance, refer to each skill's AGENTS.md:

- **hipaa-guardian**: `skills/hipaa-guardian/AGENTS.md`
