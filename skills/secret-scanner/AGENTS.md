# Secret Scanner

**Version 1.0.0**
1mangesh1
February 2026

> **Note:**
> This document is for AI agents and LLMs to follow when scanning for secrets,
> API keys, tokens, and credentials. Humans may also find it useful, but
> instructions are optimized for AI-assisted workflows.

---

## Abstract

Comprehensive secret detection skill for AI agents. Detects API keys, tokens, passwords, private keys, and credentials across 50+ providers including AWS, GCP, Azure, GitHub, Stripe, Slack, OpenAI, and more. Features entropy-based detection, git history scanning, pre-commit hooks, and CI/CD integration.

**Key Capabilities:**
- Pattern-based detection: 200+ regex patterns for known secret formats
- Entropy analysis: Detect high-entropy strings that may be unknown secrets
- Git history scanning: Find secrets in commit history
- Multi-provider support: AWS, GCP, Azure, GitHub, Stripe, Slack, OpenAI, and 50+ more
- Risk scoring: Severity-based prioritization
- CI/CD ready: Pre-commit hooks and GitHub Actions

---

## Table of Contents

1. [When to Activate](#1-when-to-activate)
2. [Detection Workflow](#2-detection-workflow)
3. [Secret Patterns](#3-secret-patterns)
4. [Risk Scoring](#4-risk-scoring)
5. [Output Formats](#5-output-formats)
6. [Security Guardrails](#6-security-guardrails)

---

## 1. When to Activate

Activate this skill when the user:
- Asks to "scan for secrets" or "find API keys"
- Mentions "credential detection" or "token scanning"
- Wants to "check for hardcoded passwords"
- Asks to "scan git history for secrets"
- Mentions "pre-commit hook for secrets"
- Wants to "audit repository for credentials"
- Asks about "secret leakage" or "exposed keys"
- Mentions specific providers: AWS keys, GitHub tokens, Stripe keys, etc.

---

## 2. Detection Workflow

### Step 1: Identify Target

Determine scan scope:
- **Files/directories**: Current codebase
- **Git history**: Commit history for leaked secrets
- **Specific files**: `.env`, config files, etc.

### Step 2: File Discovery

Use Glob to find relevant files:

```
# Configuration files (highest priority)
**/*.env, **/*.env.*, **/secrets.*, **/credentials.*

# Source code
**/*.{py,js,ts,tsx,java,go,rb,php,cs}

# Config files
**/*.{json,yaml,yml,xml,toml,ini,conf}

# Infrastructure
**/*.{tf,tfvars,hcl,dockerfile}

# Shell scripts
**/*.{sh,bash,zsh}
```

### Step 3: Apply Detection Patterns

Use patterns from `references/secret-patterns.md`:

**Critical Patterns (always flag):**
```python
# AWS Access Key
(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}

# GitHub Token
ghp_[A-Za-z0-9_]{36,255}

# Private Key
-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----

# Stripe Live Key
sk_live_[A-Za-z0-9]{24,}
```

### Step 4: Entropy Analysis

For unmatched strings, calculate Shannon entropy:

```python
def entropy(s):
    from collections import Counter
    import math
    counts = Counter(s)
    length = len(s)
    return -sum((c/length) * math.log2(c/length) for c in counts.values())

# Flag if: entropy > 4.5 AND length >= 20 AND mixed char classes
```

### Step 5: Context Validation

For each match:
1. Check against known false positives (EXAMPLE, test_, placeholder)
2. Analyze surrounding context (variable names, comments)
3. Determine file exposure level (public, .env, test file)
4. Calculate confidence score

### Step 6: Risk Scoring

Apply formula:
```
Risk = (Sensitivity × 0.40) + (Exposure × 0.30) +
       (Verifiability × 0.15) + (Scope × 0.15)
```

### Step 7: Generate Output

Format findings with masked values and remediation guidance.

---

## 3. Secret Patterns

### Critical Severity (Immediate Action)

| Provider | Pattern | Example |
|----------|---------|---------|
| AWS Access Key | `AKIA[A-Z0-9]{16}` | `AKIAIOSFODNN7...` |
| GitHub PAT | `ghp_[A-Za-z0-9_]{36,}` | `ghp_xxxx...` |
| Private Key | `-----BEGIN RSA PRIVATE KEY-----` | PEM format |
| Stripe Live | `sk_live_[A-Za-z0-9]{24,}` | `sk_live_xxxx...` |
| Slack Bot Token | `xoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{24}` | `xoxb-xxx-xxx-xxx` |
| OpenAI API Key | `sk-proj-[A-Za-z0-9_-]{48,}` | `sk-proj-xxxx...` |
| Database URI | `postgres://user:pass@host` | With credentials |

### High Severity (Within 4 hours)

| Provider | Pattern | Example |
|----------|---------|---------|
| Generic Password | `password=['"][^'"]{8,}['"]` | Hardcoded |
| GCP API Key | `AIza[0-9A-Za-z_-]{35}` | `AIzaxxxx...` |
| Twilio API Key | `SK[a-f0-9]{32}` | `SKxxxx...` |
| SendGrid | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | `SG.xxx.xxx` |

### Medium Severity (Within 24 hours)

| Provider | Pattern | Example |
|----------|---------|---------|
| Stripe Test | `sk_test_[A-Za-z0-9]{24,}` | Test mode |
| Generic API Key | `api_key=['"][A-Za-z0-9_-]{20,}['"]` | Context-dependent |
| JWT Token | `eyJ[...].eyJ[...].xxx` | May be valid |

Full patterns: `references/secret-patterns.md`

---

## 4. Risk Scoring

### Severity Levels

| Score | Severity | Response Time |
|-------|----------|---------------|
| 90-100 | **Critical** | Immediate |
| 70-89 | **High** | 4 hours |
| 50-69 | **Medium** | 24 hours |
| 25-49 | **Low** | 1 week |
| 0-24 | **Info** | Review |

### Factor Weights

- **Sensitivity (40%)**: Type of secret
  - Private keys, production API keys: 100
  - Database credentials: 90
  - Test keys: 40

- **Exposure (30%)**: Where found
  - Public repository: 95
  - `.env` file committed: 85
  - Test file: 30

- **Verifiability (15%)**: Pattern confidence
  - Exact pattern match: 95
  - Entropy-based: 60

- **Scope (15%)**: Potential blast radius
  - Full account access: 100
  - Limited scope: 50

---

## 5. Output Formats

### Finding Object

```json
{
  "id": "S-20260204-0001",
  "file": "config/settings.py",
  "line": 42,
  "column": 15,
  "secret_type": "aws_access_key",
  "provider": "AWS",
  "value_preview": "AKIA...XXXX",
  "value_hash": "sha256:abc123...",
  "confidence": 0.98,
  "risk_score": 95,
  "severity": "critical",
  "context": ">>> 42: AWS_KEY = 'AKIA[REDACTED]'",
  "remediation": [
    "1. Revoke key in AWS Console",
    "2. Generate new access key",
    "3. Update environment variables"
  ]
}
```

### Report Sections

1. Executive Summary
2. Findings by Severity
3. Provider Breakdown
4. Remediation Checklist

---

## 6. Security Guardrails

**CRITICAL - Always follow these rules:**

1. **Never output full secret values** - Show only masked preview (first/last 4 chars)
2. **Use hashes for tracking** - SHA256 for deduplication
3. **Redact in context** - Replace values with [REDACTED] in code snippets
4. **Don't auto-verify** - Never test secrets against live APIs
5. **Respect allowlists** - Honor user-configured exclusions
6. **Secure temp files** - Clean up after scanning
7. **Warn on production data** - Confirm before scanning live systems

---

## References

- `references/secret-patterns.md` - All detection patterns
- `references/remediation.md` - Secret rotation guides

## Scripts

- `scripts/detect-secrets.py` - Main detection script
- `scripts/scan-git-history.py` - Git history scanner
- `scripts/pre-commit-hook.sh` - Pre-commit hook
