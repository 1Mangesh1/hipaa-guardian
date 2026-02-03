# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HIPAA Guardian** is an AI agent skill for detecting Protected Health Information (PHI) and Personally Identifiable Information (PII) in code and data files. It maps findings to HIPAA regulations, generates audit reports, validates security controls, and provides remediation guidance.

This is a **multi-agent compatible skill package**, not a standalone application. It installs into AI coding agents (Claude Code, Cursor, Windsurf, Aider, etc.) via the Agent Skills standard.

## Available Commands

The skill is invoked via `/hipaa-guardian` or `/hipaa` or `/phi-scan`:

| Command | Description |
|---------|-------------|
| `scan <path>` | Scan files/directories for PHI/PII identifiers |
| `scan-code <path>` | Scan source code for PHI leakage |
| `scan-auth <path>` | Check API endpoints for missing authentication before PHI access |
| `scan-logs <path>` | Detect PHI patterns in logging statements |
| `scan-response <path>` | Check API responses for unmasked PHI exposure |
| `audit <path>` | Generate full HIPAA compliance audit report |
| `controls <path>` | Validate security controls in a project |
| `report` | Generate report from existing findings |

**Options:**
- `--format <type>` - Output format: json, markdown, csv (default: markdown)
- `--output <file>` - Write results to file
- `--severity <level>` - Minimum severity: low, medium, high, critical
- `--include <patterns>` - File patterns to include
- `--exclude <patterns>` - File patterns to exclude
- `--synthetic` - Treat all data as synthetic (default for safety)

## Running Scripts Directly

```bash
python scripts/detect-phi.py <path>        # Scan for PHI in data files (FHIR, HL7, CDA support)
python scripts/scan-code.py <path>         # Scan source code for PHI leakage
python scripts/scan-auth.py <path>         # Check API endpoints for auth gates
python scripts/scan-logs.py <path>         # Detect PHI in logging statements
python scripts/scan-response.py <path>     # Check API responses for PHI exposure
python scripts/generate-report.py          # Generate report from findings
bash scripts/validate-controls.sh <path>   # Validate security controls
```

## CI/CD Integration

Install the pre-commit hook:
```bash
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Environment variables:
- `HIPAA_BLOCK_ON_CRITICAL=true` - Block commits with critical findings
- `HIPAA_BLOCK_ON_HIGH=true` - Block commits with high severity findings

## Architecture

### Directory Structure

- `scripts/` - Executable Python and Shell scripts for PHI detection, code scanning, report generation, and controls validation
- `references/` - Knowledge base containing HIPAA identifiers, detection patterns, risk scoring methodology, and HIPAA rule mappings
- `examples/` - Sample findings, audit reports, and synthetic test data
- `skills/hipaa-guardian/` - Installable skill package (mirrors root structure for multi-agent compatibility)

### Detection Workflow

1. **File Discovery** - Glob for file pattern matching
2. **Content Scanning** - Grep with regex patterns from `references/detection-patterns.md`
3. **Pattern Matching** - Against 18 HIPAA Safe Harbor identifiers from `references/hipaa-identifiers.md`
4. **Risk Scoring** - Weighted formula (sensitivity 35%, exposure 25%, volume 20%, identifiability 20%) from `references/risk-scoring.md`
5. **HIPAA Mapping** - Regulatory sections from `references/privacy-rule.md`, `references/security-rule.md`, `references/breach-rule.md`
6. **Output Generation** - JSON, Markdown, or CSV format

### Finding Structure

Findings use this JSON structure:
```json
{
  "id": "F-YYYYMMDD-NNNN",
  "file": "path/to/file",
  "line": 123,
  "identifier_type": "ssn|mrn|dob|...",
  "classification": "PHI|PII|sensitive_nonPHI",
  "value_hash": "sha256:...",
  "confidence": 0.0-1.0,
  "risk_score": 0-100,
  "severity": "critical|high|medium|low|info",
  "hipaa_mapping": [...],
  "remediation_steps": [...]
}
```

### Security Guardrails (Critical)

- **Never output detected PHI values** - Use hashes or [REDACTED]
- **Default synthetic data mode** - Warn before processing potentially real PHI
- **Redact context snippets** containing PHI
- **No PHI in logs or temporary files**
- **Clean up temporary findings** after processing

## Healthcare Format Support

The skill detects PHI in standardized healthcare data formats:

| Format | Extensions | Detection |
|--------|------------|-----------|
| FHIR R4 | `.fhir.json`, `.fhir.xml` | Patient, Condition, Observation resources |
| HL7 v2.x | `.hl7` | MSH, PID, DG1, OBX segments |
| CDA/C-CDA | `.cda`, `.ccda` | ClinicalDocument, patientRole |
| Genetic | - | DNA sequences, SNP IDs |

## Key Reference Files

When implementing detection or extending functionality:

- `references/hipaa-identifiers.md` - All 18 Safe Harbor identifiers (45 CFR 164.514(b)(2))
- `references/detection-patterns.md` - Regex patterns for PHI detection
- `references/healthcare-formats.md` - FHIR, HL7, CDA detection patterns
- `references/code-scanning.md` - Code-specific detection patterns
- `references/auth-patterns.md` - Authentication gate patterns for PHI endpoints
- `references/logging-safety.md` - PHI-safe logging patterns
- `references/api-security.md` - API response masking patterns

## Severity Classification

- **Critical (90-100):** SSN, biometric data, unencrypted PHI in public repo
- **High (70-89):** Names, MRN, phone, email without protection
- **Medium (50-69):** Dates, device IDs, less sensitive combinations
- **Low (25-49):** IP addresses, non-identifiable data
- **Informational (0-24):** General findings

## Multi-Agent Installation

The skill follows the Agent Skills standard for distribution:

```bash
npx skills add 1Mangesh1/hipaa-guardian
```

Compatible with 40+ AI coding agents via respective installation paths:
- Claude Code: `~/.claude/skills/`
- Cursor: `.cursor/skills/`
- Aider: `~/.aider/skills/`
