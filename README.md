# dev-skills

A collection of AI agent skills for development, compliance, and security workflows.

## Installation

Works with 40+ AI coding agents including Claude Code, Cursor, Windsurf, Aider, Continue, Cline, and more.

### Install All Skills

```bash
npx skills add 1Mangesh1/dev-skills
```

### Install Specific Skill

```bash
npx skills add 1Mangesh1/dev-skills --skill hipaa-guardian
npx skills add 1Mangesh1/dev-skills --skill secret-scanner
```

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [hipaa-guardian](./skills/hipaa-guardian/) | HIPAA compliance, PHI/PII detection, healthcare format support | 1.2.0 |
| [secret-scanner](./skills/secret-scanner/) | Secret detection, API keys, tokens, credentials (50+ providers) | 1.0.0 |

## Skills Overview

### hipaa-guardian

Comprehensive HIPAA compliance skill for AI agents with developer code security patterns and healthcare data format support.

**Features:**
- PHI/PII Detection (18 HIPAA Safe Harbor identifiers)
- Healthcare Format Support (FHIR R4, HL7 v2.x, CDA/C-CDA)
- Code Scanning (Python, JavaScript, TypeScript, Java, Go, C#)
- Authentication Gate Detection
- Log Safety Audit
- API Response PHI Exposure Check
- Risk Scoring (0-100)
- HIPAA Rule Mapping
- Pre-commit Hook for CI/CD

**Usage:**
```bash
/hipaa-guardian scan <path>           # Scan for PHI/PII
/hipaa-guardian scan-code <path>      # Scan source code
/hipaa-guardian scan-auth <path>      # Check authentication gates
/hipaa-guardian scan-logs <path>      # Detect PHI in logs
/hipaa-guardian audit <path>          # Full compliance audit
```

[View full documentation](./skills/hipaa-guardian/README.md)

---

### secret-scanner

Comprehensive secret detection skill for AI agents. Detects API keys, tokens, passwords, and credentials across 50+ providers.

**Features:**
- Pattern Detection (200+ regex patterns for known secret formats)
- Entropy Analysis (detect high-entropy strings)
- 50+ Providers (AWS, GCP, Azure, GitHub, Stripe, Slack, OpenAI, etc.)
- Git History Scanning (find secrets in commit history)
- Risk Scoring (0-100 severity-based)
- Pre-commit Hook for CI/CD
- SARIF Output (GitHub Security integration)
- Remediation Guidance (rotation instructions)

**Usage:**
```bash
/secret-scanner scan <path>           # Scan for secrets
/secret-scanner scan-git <path>       # Scan git history
/secret-scanner audit <path>          # Full security audit
/secret-scanner verify "sk_live_xxx"  # Check specific string
```

[View full documentation](./skills/secret-scanner/README.md)

---

## Compatibility

| Agent | Status | Install Method |
|-------|--------|----------------|
| Claude Code | Supported | `/plugin install` or manual |
| Cursor | Supported | Add to `.cursor/skills/` |
| Windsurf | Supported | Add to workspace skills |
| Aider | Supported | Add to `.aider/skills/` |
| Continue | Supported | Add to config |
| Cline | Supported | Add to workspace |

## Repository Structure

```
dev-skills/
├── README.md                    # This file
├── AGENTS.md                    # Collection-level agent guidance
├── CLAUDE.md                    # Development instructions
├── package.json                 # npm metadata
├── .claude-plugin/
│   └── marketplace.json         # Claude Code plugin config
└── skills/
    ├── hipaa-guardian/          # HIPAA compliance skill
    │   ├── SKILL.md
    │   ├── scripts/
    │   ├── references/
    │   └── examples/
    └── secret-scanner/          # Secret detection skill
        ├── SKILL.md
        ├── scripts/
        ├── references/
        └── examples/
```

## Adding New Skills

To add a new skill to this collection:

1. Create a new directory under `skills/`
2. Include at minimum: `SKILL.md`, `README.md`, `agent-skills.json`
3. Update `package.json` with the new skill
4. Update `.claude-plugin/marketplace.json`

## License

MIT

## Author

[1mangesh1](https://github.com/1Mangesh1)
