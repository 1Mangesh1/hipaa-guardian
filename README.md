# HIPAA Guardian

A comprehensive Claude Code skill for detecting Protected Health Information (PHI) and Personally Identifiable Information (PII), mapping findings to HIPAA regulations, generating audit reports, and providing remediation guidance.

## Features

- **PHI/PII Detection** - Scans for all 18 HIPAA Safe Harbor identifiers
- **Code Scanning** - Detects PHI leakage in source code, comments, test fixtures, and configs
- **Classification** - Categorizes findings as PHI, PII, or sensitive_nonPHI
- **Risk Scoring** - Scores findings 0-100 based on sensitivity, exposure, volume, and identifiability
- **HIPAA Mapping** - Maps each finding to specific Privacy Rule, Security Rule, and Breach Notification Rule sections
- **Audit Reports** - Generates detailed compliance reports with executive summaries
- **Remediation Guidance** - Provides step-by-step remediation playbooks
- **Security Control Checks** - Validates .gitignore, pre-commit hooks, and secrets management

## Installation

The skill is installed at `~/.claude/skills/hipaa-guardian/`

## Usage

Invoke the skill using `/hipaa-guardian` followed by a command:

```bash
# Scan data files for PHI/PII
/hipaa-guardian scan ./data

# Scan source code for PHI leakage
/hipaa-guardian scan-code ./src

# Generate full HIPAA compliance audit report
/hipaa-guardian audit ./project

# Check security controls
/hipaa-guardian controls .
```

### Commands

| Command | Description |
|---------|-------------|
| `scan <path>` | Scan files for PHI/PII identifiers |
| `scan-code <path>` | Scan source code for hardcoded PHI |
| `audit <path>` | Generate comprehensive audit report |
| `controls <path>` | Validate security controls |

### Options

| Option | Description |
|--------|-------------|
| `--format <type>` | Output format: json, markdown, csv |
| `--output <file>` | Write results to file |
| `--severity <level>` | Minimum severity: low, medium, high, critical |
| `--synthetic` | Treat all data as synthetic (default for safety) |

## The 18 HIPAA Identifiers

The skill detects all Safe Harbor identifiers defined in 45 CFR 164.514(b)(2):

| # | Identifier | Risk Level |
|---|------------|------------|
| 1 | Names | High |
| 2 | Geographic subdivisions (smaller than state) | Medium |
| 3 | Dates (except year) - DOB, admission, discharge, death | Medium |
| 4 | Phone numbers | High |
| 5 | Fax numbers | High |
| 6 | Email addresses | High |
| 7 | Social Security numbers | Critical |
| 8 | Medical record numbers | High |
| 9 | Health plan beneficiary numbers | High |
| 10 | Account numbers | High |
| 11 | Certificate/license numbers | High |
| 12 | Vehicle identifiers and serial numbers | Medium |
| 13 | Device identifiers and serial numbers | Medium |
| 14 | Web URLs | Medium |
| 15 | IP addresses | Low-Medium |
| 16 | Biometric identifiers | Critical |
| 17 | Full-face photographs | High |
| 18 | Any other unique identifying number/code | Variable |

## Risk Scoring

Findings are scored 0-100 using four weighted factors:

```
Risk Score = (Sensitivity × 0.35) + (Exposure × 0.25) +
             (Volume × 0.20) + (Identifiability × 0.20)
```

### Severity Levels

| Score | Severity | Response Time |
|-------|----------|---------------|
| 90-100 | Critical | Immediate |
| 70-89 | High | 24 hours |
| 50-69 | Medium | 1 week |
| 25-49 | Low | 1 month |
| 0-24 | Informational | As needed |

## Code Scanning

The skill scans source code for PHI leakage in:

### Target File Types
- **Source Code**: `.py`, `.js`, `.ts`, `.tsx`, `.java`, `.go`, `.rb`, `.cs`
- **Configuration**: `.env`, `.yaml`, `.yml`, `.json`, `.xml`
- **Database**: `.sql`, migrations, seeds, fixtures
- **Tests**: `*_test.*`, `*_spec.*`, `test_*.*`

### Detection Scenarios
1. **Hardcoded PHI** - String literals containing SSN, MRN, names, dates
2. **PHI in Comments** - Example data in code comments, TODOs
3. **Test Data Leakage** - Test fixtures with real PHI
4. **Configuration Files** - `.env` files with sensitive data
5. **SQL Files** - INSERT/UPDATE statements with PHI

## Output Formats

### findings.json
Structured JSON with all findings, metadata, and summary statistics.

### audit_report.md
Human-readable Markdown report including:
- Executive summary
- Risk overview
- Detailed findings by severity
- HIPAA compliance status
- Remediation playbook

### Sample Finding

```json
{
  "id": "F-20260128-0001",
  "file": "data/patients.json",
  "line": 42,
  "identifier_type": "ssn",
  "classification": "PHI",
  "risk_score": 92,
  "severity": "critical",
  "hipaa_mapping": [
    {
      "rule": "Privacy Rule",
      "section": "164.514(b)(2)(i)(G)",
      "description": "SSN is a HIPAA identifier requiring protection"
    }
  ],
  "remediation_steps": [
    "Remove or hash the SSN value",
    "Implement access controls",
    "Add encryption at rest"
  ]
}
```

## Security Controls Validation

The `controls` command checks for:

- **Git Security**
  - `.gitignore` excludes `.env`, `*.pem`, `*.key`, credentials
  - Pre-commit hooks configured
  - No PHI in commit history

- **Secrets Management**
  - No hardcoded API keys or passwords
  - Environment variables used for secrets
  - `.env.example` with placeholder values

- **File Permissions**
  - Sensitive files not world-readable
  - Proper ownership on credential files

## Directory Structure

```
~/.claude/skills/hipaa-guardian/
├── SKILL.md                    # Main skill definition
├── references/
│   ├── hipaa-identifiers.md    # 18 HIPAA PHI identifiers
│   ├── detection-patterns.md   # Regex patterns for detection
│   ├── code-scanning.md        # Code-specific patterns
│   ├── privacy-rule.md         # Privacy Rule (45 CFR 164.500-534)
│   ├── security-rule.md        # Security Rule (45 CFR 164.302-318)
│   ├── breach-rule.md          # Breach Notification Rule
│   └── risk-scoring.md         # Risk scoring methodology
├── examples/
│   ├── sample-finding.json     # Example finding output
│   ├── sample-audit-report.md  # Example audit report
│   └── synthetic-phi-data.json # Test data for validation
└── scripts/
    ├── detect-phi.py           # PHI detection script
    ├── scan-code.py            # Code scanning script
    ├── generate-report.py      # Report generation script
    └── validate-controls.sh    # Control validation script
```

## HIPAA Reference

### Privacy Rule (45 CFR Part 164, Subpart E)
- Establishes standards for PHI protection
- Defines the 18 Safe Harbor identifiers
- Specifies permitted uses and disclosures

### Security Rule (45 CFR Part 164, Subpart C)
- Administrative safeguards (164.308)
- Physical safeguards (164.310)
- Technical safeguards (164.312)

### Breach Notification Rule (45 CFR Part 164, Subpart D)
- Notification requirements for PHI breaches
- Risk assessment criteria
- Reporting timelines (60-day requirement)

## Security Guardrails

The skill follows strict security practices:

1. **Never stores detected PHI values** - Only hashes for deduplication
2. **Redacts PHI in outputs** - Uses `[REDACTED]` in context snippets
3. **Default synthetic data mode** - Warns before processing real PHI
4. **No PHI in logs** - Sanitizes all console output
5. **Secure temporary files** - Uses scratchpad directory, cleans up after

## Compliance Disclaimer

This skill assists with PHI detection but does not guarantee HIPAA compliance. Organizations must:

- Conduct formal risk assessments
- Implement comprehensive policies and procedures
- Train workforce members
- Maintain Business Associate Agreements
- Engage qualified compliance professionals

The skill is a technical aid, not a substitute for professional compliance guidance.

## License

This skill is provided for educational and compliance assistance purposes.

## References

- [HHS HIPAA Information](https://www.hhs.gov/hipaa/)
- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/)
- [Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/)
- [De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/)
