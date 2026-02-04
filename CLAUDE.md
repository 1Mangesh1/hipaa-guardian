# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**dev-skills** is a multi-skill collection for AI coding agents. Skills are self-contained packages that follow the Agent Skills standard for distribution across 40+ AI agents.

## Repository Structure

```
dev-skills/
├── README.md                    # Collection overview
├── AGENTS.md                    # Agent guidance (collection-level)
├── CLAUDE.md                    # This file
├── package.json                 # npm metadata
├── .claude-plugin/
│   └── marketplace.json         # Claude Code plugin config
└── skills/
    └── hipaa-guardian/          # HIPAA compliance skill
        ├── SKILL.md             # Entry point
        ├── README.md            # Documentation
        ├── AGENTS.md            # Agent guidance (skill-level)
        ├── agent-skills.json    # Manifest
        ├── scripts/             # Executables
        ├── references/          # Knowledge base
        └── examples/            # Sample outputs
```

## Available Skills

### hipaa-guardian (v1.2.0)

HIPAA compliance skill for PHI/PII detection, code scanning, and healthcare format support.

**Commands:**
```bash
/hipaa-guardian scan <path>           # Scan for PHI/PII
/hipaa-guardian scan-code <path>      # Scan source code
/hipaa-guardian scan-auth <path>      # Check auth gates
/hipaa-guardian scan-logs <path>      # Detect PHI in logs
/hipaa-guardian scan-response <path>  # Check API responses
/hipaa-guardian audit <path>          # Full compliance audit
```

**Scripts:**
```bash
python skills/hipaa-guardian/scripts/detect-phi.py <path>
python skills/hipaa-guardian/scripts/scan-code.py <path>
python skills/hipaa-guardian/scripts/scan-auth.py <path>
python skills/hipaa-guardian/scripts/scan-logs.py <path>
python skills/hipaa-guardian/scripts/scan-response.py <path>
```

**Key Files:**
- `skills/hipaa-guardian/SKILL.md` - Primary entry point
- `skills/hipaa-guardian/AGENTS.md` - Detailed agent instructions
- `skills/hipaa-guardian/references/` - Detection patterns, HIPAA rules

## Installation

```bash
# Install all skills
npx skills add 1Mangesh1/dev-skills

# Install specific skill
npx skills add 1Mangesh1/dev-skills --skill hipaa-guardian
```

## Adding New Skills

1. Create `skills/<skill-name>/` directory
2. Add required files:
   - `SKILL.md` - Skill definition and workflow
   - `README.md` - Human documentation
   - `AGENTS.md` - Agent instructions
   - `agent-skills.json` - Manifest with capabilities
3. Update `package.json` with skill metadata
4. Update `.claude-plugin/marketplace.json`
5. Update root `README.md` and `AGENTS.md` tables

## Skill Standard

### Required Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Entry point, workflow, commands |
| `README.md` | Human documentation |
| `AGENTS.md` | Agent/LLM instructions |
| `agent-skills.json` | Capabilities, scripts, references |

### Optional Directories

| Directory | Purpose |
|-----------|---------|
| `scripts/` | Python/Shell executables |
| `references/` | Knowledge base, patterns |
| `examples/` | Sample outputs, test data |

## Security Guidelines

All skills must follow these practices:

- Never output sensitive data in plain text
- Use hashes or [REDACTED] for sensitive values
- Default to synthetic/test data mode
- Clean up temporary files after processing
- Warn before processing potentially real sensitive data

## Development Commands

```bash
# Test skill discovery
npx skills add . --list

# Verify structure
tree -L 3 skills/

# Run hipaa-guardian tests
python skills/hipaa-guardian/scripts/detect-phi.py examples/
```
