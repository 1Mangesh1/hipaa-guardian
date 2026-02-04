# HIPAA Guardian

**Version 1.2.0**
1mangesh1
February 2026

> **Note:**
> This document is for AI agents and LLMs to follow when scanning for PHI/PII,
> auditing HIPAA compliance, or generating remediation guidance. Humans may
> also find it useful, but instructions are optimized for AI-assisted workflows.

---

## Abstract

Comprehensive HIPAA compliance skill for AI agents with a strong focus on developer code security patterns. Detects all 18 HIPAA Safe Harbor identifiers (SSN, MRN, DOB, phone, email, address, etc.) in data files and source code. Provides risk scoring (0-100), maps findings to Privacy Rule, Security Rule, and Breach Notification Rule sections, generates audit reports, and offers step-by-step remediation guidance.

**Developer-Focused Capabilities:**
- Auth Gate Detection: Find API endpoints exposing PHI without authentication
- Log Safety Audit: Detect PHI leaking into log statements
- API Response Checks: Identify unmasked PHI in API responses
- Frontend PHI Protection: Detect client-side PHI storage vulnerabilities
- Healthcare Format Support: FHIR R4, HL7 v2.x, CDA/C-CDA

---

## Table of Contents

1. [When to Activate](#1-when-to-activate)
2. [Detection Workflow](#2-detection-workflow)
3. [The 18 HIPAA Identifiers](#3-the-18-hipaa-identifiers)
4. [Code Scanning Rules](#4-code-scanning-rules)
5. [Developer Code Compliance](#5-developer-code-compliance)
6. [Risk Scoring](#6-risk-scoring)
7. [HIPAA Rule Mapping](#7-hipaa-rule-mapping)
8. [Output Formats](#8-output-formats)
9. [Security Guardrails](#9-security-guardrails)

---

## 1. When to Activate

Activate this skill when the user:
- Asks to "scan for PHI" or "detect PII"
- Mentions "HIPAA compliance" or "HIPAA audit"
- Wants to "find sensitive healthcare data"
- Asks to "check for protected health information"
- Mentions "medical record security" or "patient data privacy"
- Wants to scan code for "hardcoded PHI" or "test data leakage"
- Asks to "check authentication on PHI endpoints"
- Wants to "scan logs for PHI" or "check logging safety"
- Mentions "API response masking" or "field-level authorization"
- Asks about "PHI in error messages" or "client-side PHI storage"
- Wants to review code for "authentication gates" or "audit logging"
- Mentions "FHIR", "HL7", "CDA", or healthcare data formats

---

## 2. Detection Workflow

### Step 1: Identify Target Files

Use Glob to find files based on scan type:

**Data Scanning:**
```
*.json, *.csv, *.xml, *.txt, *.log, *.hl7, *.fhir
```

**Code Scanning:**
```
*.py, *.js, *.ts, *.tsx, *.java, *.go, *.rb, *.cs, *.sql
*.env, *.yaml, *.yml, *.json, *.xml
*_test.*, *_spec.*, test_*.*
```

### Step 2: Apply Detection Patterns

Use Grep with patterns from `references/detection-patterns.md`:

```python
# Priority patterns
SSN:   \b\d{3}-\d{2}-\d{4}\b
Phone: \b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b
Email: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
Date:  \b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b
MRN:   (?i)\b(MRN|MR#?|Medical\s*Record)\s*[:#]?\s*[A-Z]?\d{5,12}\b
```

### Step 3: Validate and Classify

For each match:
1. Check exclusion patterns (test SSNs, localhost IPs, etc.)
2. Extract context (surrounding lines)
3. Classify: **PHI** (with health context), **PII** (personal only), **sensitive_nonPHI**
4. Calculate confidence score (0.0-1.0)

### Step 4: Calculate Risk Score

Apply formula from `references/risk-scoring.md`:

```
Risk = (Sensitivity × 0.35) + (Exposure × 0.25) +
       (Volume × 0.20) + (Identifiability × 0.20)
```

### Step 5: Map to HIPAA Rules

Reference the appropriate rule for each finding:
- Privacy Rule: `references/privacy-rule.md`
- Security Rule: `references/security-rule.md`
- Breach Rule: `references/breach-rule.md`

### Step 6: Generate Output

Format findings as JSON and/or Markdown report.

---

## 3. The 18 HIPAA Identifiers

| # | Identifier | Risk | Pattern Reference |
|---|------------|------|-------------------|
| 1 | Names | High | Context-dependent |
| 2 | Geographic (< state) | Medium | Address, ZIP patterns |
| 3 | Dates (except year) | Medium | DOB, admit/discharge |
| 4 | Phone numbers | High | Multiple formats |
| 5 | Fax numbers | High | Same as phone |
| 6 | Email addresses | High | Standard email regex |
| 7 | SSN | **Critical** | XXX-XX-XXXX |
| 8 | Medical Record # | High | MRN patterns |
| 9 | Health Plan ID | High | Member/policy IDs |
| 10 | Account numbers | High | Financial accounts |
| 11 | License numbers | High | DL, DEA, NPI |
| 12 | Vehicle IDs | Medium | VIN, plates |
| 13 | Device IDs | Medium | Serial, UDI |
| 14 | URLs | Medium | With patient IDs |
| 15 | IP addresses | Low-Med | IPv4/IPv6 |
| 16 | Biometrics | **Critical** | Fingerprint, DNA |
| 17 | Photos | High | Face images |
| 18 | Other unique IDs | Variable | Custom identifiers |

Full details: `references/hipaa-identifiers.md`

---

## 4. Code Scanning Rules

### 4.1 Hardcoded PHI in Source

**Detect:**
```python
# Bad - hardcoded SSN
patient_ssn = "123-45-6789"
```

**Remediate:** Use environment variables or synthetic data.

### 4.2 PHI in Comments

**Detect:**
```python
# Patient John Doe SSN: 123-45-6789
# TODO: Remove test data for MRN 12345678
```

**Remediate:** Remove PHI, use placeholder format (XXX-XX-XXXX).

### 4.3 Test Data Leakage

**Detect:**
```python
TEST_PATIENT = {
    "ssn": "123-45-6789",  # Real SSN in test!
    "dob": "1985-03-15"
}
```

**Remediate:** Use Faker library for synthetic data.

### 4.4 Configuration Files

**Detect:**
```bash
# .env file
TEST_SSN=123-45-6789
```

**Remediate:** Remove, add to .gitignore, use secrets manager.

### 4.5 SQL Statements

**Detect:**
```sql
INSERT INTO patients VALUES ('123-45-6789');
```

**Remediate:** Use parameterized queries, synthetic seed data.

Full patterns: `references/code-scanning.md`

---

## 5. Developer Code Compliance

### 5.1 Authentication Gates

**CRITICAL:** Any code exposing PHI MUST have authentication before access.

**Detection Patterns:**
```regex
# Python - Unprotected routes
@app\.route\([^)]*patient[^)]*\)(?!.*@require_auth)

# JavaScript - Missing middleware
(app|router)\.(get|post)\s*\([^)]*patient[^)]*,\s*(?!.*authenticate)

# Java - Missing @PreAuthorize
@(GetMapping|PostMapping)\([^)]*patient[^)]*\)(?!\s*@PreAuthorize)
```

**Compliant Pattern:**
```python
@app.route('/api/patient/<patient_id>')
@require_auth                        # Authentication required
@require_role(['doctor', 'nurse'])   # Role-based access
@audit_log('patient_access')         # Audit trail
def get_patient(patient_id):
    # Safe to access
    pass
```

Full patterns: `references/auth-patterns.md`

### 5.2 PHI in Logging

**Detection Patterns:**
```regex
# Python logging with PHI
(logger|logging)\.(info|debug|error).*patient\.(ssn|name|dob)
print\(.*patient\.

# JavaScript
console\.(log|error).*patient
```

**Compliant Pattern:**
```python
# Use IDs only, never PHI values
logger.info(f"Processing patient_id={patient.id}")

# Apply PHI filter
logging.getLogger().addFilter(PHIRedactionFilter())
```

Full patterns: `references/logging-safety.md`

### 5.3 API Response Masking

**Detection Patterns:**
```regex
# Returning full objects
return\s+jsonify\s*\(\s*patient\s*\)
res\.json\s*\(\s*patient\s*\)
SELECT\s+\*\s+FROM\s+patient
```

**Compliant Pattern:**
```python
# Filter based on role
filtered = PatientResponseFilter.filter_response(
    patient_data,
    user_role=Role(user.role),
)
return jsonify(filtered)
```

Full patterns: `references/api-security.md`

### 5.4 Code Scanning Checklist

| Check | Detection Target | Severity |
|-------|-----------------|----------|
| Missing Auth Gates | API endpoints without @require_auth | Critical |
| PHI in Logs | logger.* with patient.ssn, dob, name | High |
| Unmasked API Response | res.json(patient), jsonify(patient) | High |
| PHI in Error Messages | raise.*{ssn, throw.*patient | High |
| Client-Side PHI Storage | localStorage.setItem.*patient | High |
| Missing Audit Logging | PHI access without audit.log | Medium |

---

## 6. Risk Scoring

### Severity Levels

| Score | Severity | Response |
|-------|----------|----------|
| 90-100 | **Critical** | Immediate action |
| 70-89 | **High** | Within 24 hours |
| 50-69 | **Medium** | Within 1 week |
| 25-49 | **Low** | Within 1 month |
| 0-24 | **Info** | As needed |

### Factor Weights

- **Sensitivity (35%)**: SSN=100, MRN=80, DOB=85, Email=55
- **Exposure (25%)**: Public repo=95, Internal=40, Encrypted=15
- **Volume (20%)**: 500+=100, 100-499=85, 1=25
- **Identifiability (20%)**: Direct ID=100, Quasi-combo=85

Full methodology: `references/risk-scoring.md`

---

## 7. HIPAA Rule Mapping

### Privacy Rule (45 CFR 164.500-534)

| Finding | Section | Description |
|---------|---------|-------------|
| Any PHI exposure | §164.502 | Impermissible use/disclosure |
| Identifiers present | §164.514 | De-identification required |
| Excess data shared | §164.502(b) | Minimum necessary violation |

### Security Rule (45 CFR 164.302-318)

| Finding | Section | Description |
|---------|---------|-------------|
| No encryption | §164.312(a)(2)(iv) | Encryption required |
| Missing audit logs | §164.312(b) | Audit controls required |
| No access control | §164.312(a)(1) | Access control required |
| PHI in logs | §164.312(b) | Improper audit implementation |

### Breach Notification (45 CFR 164.400-414)

| Finding | Section | Description |
|---------|---------|-------------|
| PHI in public repo | §164.402 | Likely breach, assess notification |
| Unencrypted PHI exposed | §164.402 | Breach unless encrypted |

---

## 8. Output Formats

### Finding Object

```json
{
  "id": "F-20260128-0001",
  "file": "data/patients.json",
  "line": 42,
  "identifier_type": "ssn",
  "classification": "PHI",
  "value_hash": "sha256:abc123...",
  "context": "...SSN [REDACTED] on file...",
  "confidence": 0.95,
  "risk_score": 92,
  "severity": "critical",
  "hipaa_mapping": [...],
  "remediation_steps": [...]
}
```

### Audit Report Sections

1. Executive Summary
2. Risk Overview (by severity)
3. Detailed Findings
4. HIPAA Compliance Status
5. Remediation Playbook

---

## 9. Security Guardrails

**CRITICAL - Always follow these rules:**

1. **Never output detected PHI values** - Use hashes or [REDACTED]
2. **Never store PHI** - Only store hashes for deduplication
3. **Redact in context** - Replace values with [REDACTED-SSN], etc.
4. **Default synthetic mode** - Assume test data unless confirmed otherwise
5. **Warn on real PHI** - Alert user before processing production data
6. **Clean up** - Remove any temporary files containing findings

---

## References

- `references/hipaa-identifiers.md` - All 18 identifiers
- `references/detection-patterns.md` - Regex patterns
- `references/code-scanning.md` - Code-specific rules
- `references/healthcare-formats.md` - FHIR, HL7, CDA patterns
- `references/privacy-rule.md` - Privacy Rule mapping
- `references/security-rule.md` - Security Rule mapping
- `references/breach-rule.md` - Breach Notification mapping
- `references/risk-scoring.md` - Scoring methodology
- `references/auth-patterns.md` - Authentication gate patterns for PHI endpoints
- `references/logging-safety.md` - PHI-safe logging patterns and filters
- `references/api-security.md` - API response masking and field-level auth
