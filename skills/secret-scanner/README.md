# Secret Scanner Skill

Comprehensive secret detection for AI coding agents. Detects API keys, tokens, passwords, and credentials across 50+ providers.

## Quick Start

```bash
# Install via skills.sh CLI
npx skills add 1Mangesh1/dev-skills --skill secret-scanner

# Or install all skills in the collection
npx skills add 1Mangesh1/dev-skills
```

## Capabilities

- **Pattern Detection** - 200+ regex patterns for known secret formats
- **Entropy Analysis** - Detect high-entropy strings that may be secrets
- **50+ Providers** - AWS, GCP, Azure, GitHub, Stripe, Slack, OpenAI, and more
- **Git History Scan** - Find secrets in commit history
- **Risk Scoring** - Severity-based prioritization (0-100)
- **CI/CD Integration** - Pre-commit hooks and GitHub Actions
- **Remediation** - Step-by-step rotation guides

## Usage

```bash
/secret-scanner scan ./src               # Scan directory
/secret-scanner scan-git .               # Scan git history
/secret-scanner audit ./project          # Full audit report
/secret-scanner verify "sk_live_xxx"     # Check specific string
```

## Supported Providers

| Category | Providers |
|----------|-----------|
| Cloud | AWS, GCP, Azure, DigitalOcean, Heroku |
| Code Platforms | GitHub, GitLab, Bitbucket, npm, PyPI |
| Payments | Stripe, PayPal, Square |
| Communication | Twilio, SendGrid, Slack, Discord |
| AI | OpenAI, Anthropic |
| Databases | MongoDB, PostgreSQL, MySQL, Redis |
| Other | Firebase, Cloudflare, Datadog, Auth0 |

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill instructions |
| `AGENTS.md` | Agent-specific guidance |
| `references/secret-patterns.md` | Detection patterns |
| `references/remediation.md` | Rotation guides |
| `scripts/detect-secrets.py` | Main scanner |
| `scripts/scan-git-history.py` | Git history scanner |
| `scripts/pre-commit-hook.sh` | CI/CD hook |

## Pre-Commit Hook

```bash
# Install
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Configure (optional)
export SECRET_SCANNER_SEVERITY=high
export SECRET_SCANNER_VERBOSE=true
```

## License

MIT
