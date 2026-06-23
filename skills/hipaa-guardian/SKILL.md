---
name: hipaa-guardian
description: This skill should be used when the user asks to "scan for PHI", "detect PII", "HIPAA compliance check", "audit for protected health information", "find sensitive healthcare data", "generate HIPAA audit report", "check code for PHI leakage", "scan logs for PHI", "check authentication on PHI endpoints", "scan FHIR resources", "check HL7 messages", or mentions PHI detection, HIPAA compliance, healthcare data privacy, medical record security, logging PHI violations, authentication checks for health data, or healthcare data formats (FHIR, HL7, CDA).
license: MIT
metadata:
  author: 1mangesh1
  version: "1.2.0"
  tags:
    - hipaa
    - phi
    - pii
    - healthcare
    - compliance
    - security
    - authentication
    - logging
    - api-security
    - fhir
    - hl7
    - pre-commit
---

# HIPAA Guardian

A comprehensive PHI/PII detection and HIPAA compliance skill for AI agents, with a strong focus on developer code security patterns. Detects all 18 HIPAA Safe Harbor identifiers in data files and source code, provides risk scoring, maps findings to HIPAA regulations, and generates audit reports with remediation guidance.

## Capabilities

1. **PHI/PII Detection** - Scan data files for the 18 HIPAA Safe Harbor identifiers
2. **Code Scanning** - Detect PHI in source code, comments, test fixtures, configs
3. **Auth Gate Detection** - Find API endpoints exposing PHI without authentication
4. **Log Safety Audit** - Detect PHI leaking into log statements
5. **Classification** - Classify findings as PHI, PII, or sensitive_nonPHI
6. **Risk Scoring** - Score findings 0-100 based on sensitivity and exposure
7. **HIPAA Mapping** - Map each finding to specific HIPAA rules
8. **Audit Reports** - Generate findings.json, audit reports, and playbooks
9. **Remediation** - Provide step-by-step remediation with code examples
10. **Control Checks** - Validate security controls are in place

## Usage

This skill activates from natural-language requests ("scan this repo for PHI",
"check our logs for patient data", "audit for HIPAA compliance"). Map the
request to the script that handles it and run it directly. There is no single
`hipaa-guardian` dispatcher; each task is its own script.

| Task | Script |
|------|--------|
| Scan data files for PHI/PII | `scripts/detect-phi.py <path>` |
| Scan source code for PHI leakage | `scripts/scan-code.py <path>` |
| Find PHI endpoints with no auth gate | `scripts/scan-auth.py <path>` |
| Find PHI in log statements | `scripts/scan-logs.py <path>` |
| Find unmasked PHI in API responses | `scripts/scan-response.py <path>` |
| Build an audit report from findings | `scripts/generate-report.py <findings.json>` |
| Check project security controls | `scripts/validate-controls.sh <path>` |

Each script writes to stdout (or a file with `-o`) and exits `0` (clean),
`1` (high findings), or `2` (critical findings), so CI can gate on the exit code.

### Options (detect-phi.py)

- `-f, --format <json|markdown|csv>` - Output format (default: markdown)
- `-o, --output <file>` - Write results to a file
- `-s, --severity <low|medium|high|critical>` - Minimum severity to report
- `--include <patterns>` / `--exclude <patterns>` - File patterns to scan
- `--synthetic` - Mark all findings as synthetic/test data
- `-v, --verbose` - Verbose output

`scan-code.py`, `scan-auth.py`, `scan-logs.py`, and `scan-response.py` take
`<path>` plus `-f/--format` (json or markdown), `-o/--output`, and `-v/--verbose`.

## Workflow

When invoked, follow this workflow:

### Step 1: Determine Scan Scope

Ask the user to specify:
- Target path (file, directory, or glob pattern)
- Scan type (data files, source code, or both)
- Whether data is synthetic/test data or potentially real PHI

### Step 2: File Discovery

Use Glob to find relevant files:

```
# For data files
Glob: **/*.{json,csv,txt,log,xml,hl7,fhir}

# For source code
Glob: **/*.{py,js,ts,tsx,java,cs,go,rb,sql,sh}

# For config files
Glob: **/*.{env,yaml,yml,json,xml,ini,conf}
```

### Step 3: PHI Detection

For each file, scan for the 18 HIPAA identifiers using patterns from `references/detection-patterns.md`:

1. **Names** - Patient, provider, relative names
2. **Geographic** - Addresses, cities, ZIP codes
3. **Dates** - DOB, admission, discharge, death dates
4. **Phone Numbers** - All formats
5. **Fax Numbers** - All formats
6. **Email Addresses** - All formats
7. **SSN** - Social Security Numbers
8. **MRN** - Medical Record Numbers
9. **Health Plan IDs** - Insurance identifiers
10. **Account Numbers** - Financial accounts
11. **License Numbers** - Driver's license, professional
12. **Vehicle IDs** - VIN, license plates
13. **Device IDs** - Serial numbers, UDI
14. **URLs** - Web addresses
15. **IP Addresses** - Network identifiers
16. **Biometric** - Fingerprints, retinal, voice
17. **Photos** - Full-face images
18. **Other Unique IDs** - Any other identifying numbers

### Step 4: Classification

Classify each finding:
- **PHI** - Health information linkable to individual
- **PII** - Personally identifiable but not health-related
- **sensitive_nonPHI** - Sensitive but not individually identifiable

### Step 5: Risk Scoring

The scanners score each finding `risk = min(100, sensitivity × confidence)`,
where sensitivity is the identifier's base weight (an SSN outweighs a ZIP) and
confidence is how strongly the value matched its pattern. Scores map to severity:
90+ critical, 70+ high, 50+ medium, 25+ low, otherwise informational.

`references/risk-scoring.md` documents a fuller multi-factor model (sensitivity,
exposure, volume, identifiability) for scoring a finding by hand or justifying a
rating in a report. The scanner uses the simpler proxy above.

### Step 6: HIPAA Mapping

Map findings to HIPAA rules from references:
- `references/privacy-rule.md` - 45 CFR 164.500-534
- `references/security-rule.md` - 45 CFR 164.302-318
- `references/breach-rule.md` - 45 CFR 164.400-414

### Step 7: Generate Output

Create structured output following `examples/sample-finding.json` format:

```json
{
  "id": "F-YYYYMMDD-NNNN",
  "timestamp": "ISO-8601",
  "file": "path/to/file",
  "line": 123,
  "field": "field.path",
  "value_hash": "sha256:...",
  "classification": "PHI|PII|sensitive_nonPHI",
  "identifier_type": "ssn|mrn|dob|...",
  "confidence": 0.95,
  "risk_score": 85,
  "hipaa_rules": [...],
  "remediation": [...],
  "status": "open"
}
```

## Code Scanning

When scanning source code, look for:

### 1. Hardcoded PHI in Source
- String literals containing SSN, MRN, names, dates
- Variable assignments with sensitive values
- Database seed/fixture data

### 2. PHI in Comments
- Example data in code comments
- TODO comments with patient info
- Documentation strings with real data

### 3. Test Data Leakage
- Test fixtures with real PHI
- Mock data files with actual patient info
- Integration test data

### 4. Configuration Files
- `.env` files with PHI
- Connection strings with embedded credentials
- API responses cached with PHI

### 5. SQL Files
- INSERT statements with PHI
- Sample queries with real patient data
- Database dumps

See `references/code-scanning.md` for detailed patterns.

## Security Control Checks

Verify these controls are in place:

### Access Controls
- [ ] Role-based access control (RBAC) implemented
- [ ] Minimum necessary access principle applied
- [ ] Access logging enabled

### Encryption
- [ ] Data encrypted at rest (AES-256)
- [ ] Data encrypted in transit (TLS 1.2+)
- [ ] Encryption keys properly managed

### Audit Controls
- [ ] Audit logging implemented
- [ ] Log integrity protected
- [ ] Retention policies defined

### Code Security
- [ ] `.gitignore` excludes sensitive files
- [ ] Pre-commit hooks scan for PHI
- [ ] Secrets management in place
- [ ] Data masking in logs

## Output Formats

### findings.json
Structured array of all findings with full metadata.

### audit_report.md
Human-readable report with:
- Executive summary
- Findings by severity
- HIPAA compliance status
- Risk assessment
- Recommendations

### playbook.md
Step-by-step remediation guide:
- Prioritized actions
- Code examples
- Verification steps

## Security Guardrails

1. **Default Synthetic Mode** - Assumes data is synthetic unless confirmed otherwise
2. **No PHI Storage** - Never stores detected PHI values, only hashes
3. **Redaction** - All example outputs redact actual values
4. **Warning Prompts** - Warns before processing potentially real PHI
5. **Audit Trail** - Logs all scans (without PHI values)

## References

- `references/hipaa-identifiers.md` - All 18 HIPAA Safe Harbor identifiers
- `references/detection-patterns.md` - Regex patterns for PHI detection
- `references/code-scanning.md` - Code scanning patterns and rules
- `references/healthcare-formats.md` - FHIR, HL7, CDA detection patterns
- `references/privacy-rule.md` - HIPAA Privacy Rule (45 CFR 164.500-534)
- `references/security-rule.md` - HIPAA Security Rule (45 CFR 164.302-318)
- `references/breach-rule.md` - Breach Notification Rule (45 CFR 164.400-414)
- `references/risk-scoring.md` - Risk scoring methodology
- `references/auth-patterns.md` - Authentication gate patterns for PHI endpoints
- `references/logging-safety.md` - PHI-safe logging patterns and filters
- `references/api-security.md` - API response masking and field-level auth

## CI/CD Integration

### Pre-Commit Hook Installation

```bash
# Install the pre-commit hook
cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Or using pre-commit framework
# Add to .pre-commit-config.yaml:
repos:
  - repo: local
    hooks:
      - id: hipaa-guardian
        name: HIPAA Guardian PHI Scan
        entry: python scripts/detect-phi.py
        language: python
        types: [file]
        pass_filenames: true
```

### Environment Variables

```bash
# Configure pre-commit behavior
export HIPAA_BLOCK_ON_CRITICAL=true   # Block commits with critical findings
export HIPAA_BLOCK_ON_HIGH=true       # Block commits with high severity findings
export HIPAA_SCAN_DATA=true           # Scan data files
export HIPAA_SCAN_CODE=true           # Scan source code
export HIPAA_VERBOSE=false            # Enable verbose output
```

### GitHub Actions Integration

```yaml
# .github/workflows/hipaa-scan.yml
name: HIPAA PHI Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run PHI Scan
        run: |
          python scripts/detect-phi.py . --format markdown --output phi-report.md
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: phi-scan-report
          path: phi-report.md
```

## Healthcare Data Format Support

### Supported Formats

| Format | Extensions | Detection |
|--------|------------|-----------|
| FHIR R4 | `.fhir.json`, `.fhir.xml` | Resource type, identifiers |
| HL7 v2.x | `.hl7`, `.hl7v2` | MSH, PID, DG1 segments |
| CDA/C-CDA | `.cda`, `.ccda`, `.ccd` | ClinicalDocument, patientRole |
| X12 EDI | `.x12`, `.edi`, `.837` | Transaction set headers |

### High-Risk FHIR Resources

- `Patient` - Demographics, identifiers, contacts
- `Condition` - Diagnoses, health conditions
- `Observation` - Lab results, vitals
- `MedicationRequest` - Prescriptions
- `DiagnosticReport` - Test results

### HL7 v2 PHI Segments

- `PID` - Patient Identification (SSN in PID-19)
- `DG1` - Diagnosis Information
- `OBX` - Observation/Result Values
- `IN1` - Insurance Information

## Examples

- `examples/sample-finding.json` - Example finding output format
- `examples/sample-audit-report.md` - Example audit report
- `examples/synthetic-phi-data.json` - Test data for validation

## Scripts

- `scripts/detect-phi.py` - PHI/PII detection in data files (supports FHIR, HL7, CDA formats)
- `scripts/scan-code.py` - Code scanning for PHI leakage
- `scripts/scan-auth.py` - Authentication gate detection for PHI endpoints
- `scripts/scan-logs.py` - PHI detection in logging statements
- `scripts/scan-response.py` - API response PHI exposure detection
- `scripts/generate-report.py` - Report generation script
- `scripts/validate-controls.sh` - Control validation script
- `scripts/pre-commit-hook.sh` - Git pre-commit hook for CI/CD integration
