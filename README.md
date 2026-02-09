# HIPAA Guardian

**AI-powered HIPAA compliance, PHI/PII detection, and healthcare data security skills for Claude, Cursor, Windsurf, and AI agents.**

HIPAA Guardian is a specialized skills collection designed for healthcare professionals, developers, and organizations building HIPAA-compliant systems. It provides automated tools for:
- 🔍 **Detecting Protected Health Information (PHI)** - All 18 HIPAA identifiers
- ✅ **Validating Healthcare Formats** - HL7 FHIR, HL7 v2, CDA, X12 EDI
- 📋 **Audit Logging** - Immutable compliance audit trails per 45 CFR §164.312(b)
- 🛡️ **Risk Assessment** - Breach risk scoring and remediation guidance
- 🔐 **Compliance Mapping** - HIPAA, NIST CSF 2.0, HITRUST alignment

## ⚠️ Compliance Statement

- ✅ **HIPAA-Ready**: Designed for HIPAA BAA (Business Associate Agreement) environments
- ✅ **Audit Trail**: Supports immutable logging per 45 CFR §164.312(b)
- ✅ **Standards Integration**: HL7 FHIR R5, NIST CSF 2.0, HITRUST CSF alignment
- ✅ **Open Source**: MIT License, security-first code review process

> **Note**: This skill collection is designed to support HIPAA compliance but does not guarantee HIPAA compliance. For production environments, consult with your legal and compliance team and execute a Business Associate Agreement (BAA) with any service provider.

## How It Works

### PHI Detection Workflow

```
Input File/Code
    ↓
Pattern Matching (18 HIPAA Identifiers)
    ↓
Confidence Scoring (0-100%)
    ↓
Risk Assessment
    ↓
HIPAA Rule Mapping
    ↓
Report Generation + Remediation
```

### What Gets Detected

| Identifier | Examples | Risk |
|------------|----------|------|
| **Names** | Patient, provider, relatives | HIGH |
| **SSN** | Social Security Numbers | CRITICAL |
| **MRN** | Medical Record Numbers | CRITICAL |
| **DOB** | Date of birth, admission date | HIGH |
| **Phone/Fax** | All formats detected | MEDIUM |
| **Email** | Healthcare email addresses | MEDIUM |
| **Address** | Streets, cities, ZIP codes | MEDIUM |
| **Health Plan ID** | Insurance, policy numbers | HIGH |
| **Biometric** | Photos, fingerprints, voice | CRITICAL |
| **Device IDs** | Serial numbers, UDI codes | MEDIUM |

## Installation

```bash
# Install all HIPAA Guardian skills
npx skills add 1Mangesh1/hipaa-guardian

# Install specific skill
npx skills add 1Mangesh1/hipaa-guardian --skill hipaa-guardian
```

## Quick Start

### 1. Scan Code for PHI Leakage

```bash
# Ask Claude/Copilot to scan your codebase
"Scan our backend code for hardcoded PHI like patient names, SSNs, or MRNs"

# Output: Detailed finding report with:
# - File locations
# - Line numbers  
# - Risk scores
# - Remediation steps
```

**Example Finding:**
```json
{
  "file": "database/seeders/PatientSeeder.js",
  "line": 42,
  "finding": "SSN detected: 123-45-6789",
  "identifier_type": "ssn",
  "risk_score": 95,
  "severity": "CRITICAL",
  "remediation": [
    "Remove hardcoded SSN from seeder",
    "Use faker.js or test data library",
    "Use environment variables for test credentials"
  ]
}
```

### 2. Validate Healthcare Data

```bash
# Validate FHIR Patient resource
"Check this FHIR resource for PHI exposure and compliance issues"

{
  "resourceType": "Patient",
  "id": "pat-123",
  "identifier": [{"value": "MRN-2024-001"}],
  "name": [{"given": ["John"], "family": "Doe"}],
  "birthDate": "1985-01-15"
}

# Returns: ✓ Valid FHIR R5 structure, ✓ All PHI properly identified
```

### 3. Generate Audit Logs

```bash
# Log healthcare data access for HIPAA compliance
"Create an audit log for a user viewing patient medical records"

# Generates compliant entry with:
# - Unique audit ID
# - Exact timestamp
# - User identification
# - Action taken
# - Resource accessed
# - Success/failure status
```

### 4. Generate Compliance Report

```bash
# Full HIPAA compliance assessment
"Audit our codebase for HIPAA compliance and generate a report"

# Creates comprehensive report:
# - Executive summary
# - Findings breakdown by severity
# - HIPAA rule mappings
# - Risk assessment
# - Remediation playbook
```

## Available Skills

| Skill | Purpose | Activation Triggers | Version |
|-------|---------|-------------------|---------|
| [hipaa-guardian](./skills/hipaa-guardian/) | PHI/PII detection, healthcare format validation, audit logging | "scan for PHI", "HIPAA compliance", "detect PII", "healthcare data security" | 1.2.0 |
| [fhir-hl7-validator](./skills/fhir-hl7-validator/) | HL7 FHIR R5 & HL7 v2 validation | "validate FHIR", "check HL7 message", "healthcare format" | 1.0.0 |
| [healthcare-audit-logger](./skills/healthcare-audit-logger/) | HIPAA-compliant audit trail logging | "audit log", "compliance logging", "track healthcare access" | 1.0.0 |

### [hipaa-guardian](./skills/hipaa-guardian/) Skill - Core Features

#### PHI Detection Engine
- **18 HIPAA Safe Harbor Identifiers**: Names, SSN, MRN, DOB, phone, email, address, IP, biometric, etc.
- **Confidence Scoring**: 0-100% match confidence with pattern analysis
- **Risk Assessment**: Automated risk scoring based on sensitivity & exposure
- **File Type Support**: JSON, CSV, XML, SQL, Python, JavaScript, YAML, FHIR, HL7, CDA
- **Smart Patterns**: Entropy detection, format validation, cross-field analysis

#### Healthcare Format Support
```
HL7 FHIR R5        → Patient, Condition, Observation, MedicationRequest
HL7 v2.x           → MSH, PID, DG1, OBX, RXO segments  
CDA/C-CDA          → Clinical documents, patientRole elements
X12 EDI            → Healthcare claims (837, 835 formats)
```

#### Code Security Scanning
```
✓ Source code (all languages)
✓ Comments and documentation
✓ Test fixtures and mock data
✓ Configuration files (.env, secrets)
✓ Database seeds and migrations
✓ API response samples
```

#### Compliance Features
- **HIPAA Rule Mapping**: Each finding linked to specific regulatory sections
- **Breach Risk Scoring**: 0-100 risk score with severity levels (CRITICAL→LOW)
- **De-identification Validation**: Verify data removal meets HIPAA standards
- **Audit Trail Generation**: 45 CFR §164.312(b) compliant logging
- **Remediation Guidance**: Step-by-step fix instructions with code examples

#### Integration Ready
- **Claude/Copilot/Windsurf**: Prompt activation with skill triggers
- **GitHub Actions**: CI/CD pipeline integration
- **Pre-commit Hooks**: Automatic scanning before code commits
- **VS Code Extension**: Real-time PHI detection while coding
- **OpenAPI 3.1**: REST API for third-party integration

### [fhir-hl7-validator](./skills/fhir-hl7-validator/)

Validates healthcare data against HL7 standards:
- **FHIR R5 Schema Validation** - Patient, Condition, Observation resources
- **HL7 v2 Message Parsing** - Complete v2.x segment validation
- **CDA Document Structure** - Clinical Document Architecture compliance
- **Custom Validation Rules** - Domain-specific constraints

### [healthcare-audit-logger](./skills/healthcare-audit-logger/)

HIPAA-compliant audit trail logging:
- **Immutable Logs** - Tamper-evident audit trail
- **Complete Context** - User, action, resource, timestamp, outcome
- **Access Control Logging** - Who accessed what and when
- **Event Classification** - CREATE, READ, UPDATE, DELETE, EXPORT events
- **Retention Management** - Configurable log retention policies

## Real-World Use Cases

### 1. Code Review - Detecting Hardcoded Patient Data

**Scenario**: Healthcare startup building patient portal backend

```bash
# During PR review, scan code for accidental PHI commits
"Review this PR for any hardcoded patient data"

# Findings:
// ❌ CRITICAL: database/seeders/PatientSeeder.js:42
const mockPatient = {
  name: "John Doe",           // HIGH: Patient name
  ssn: "123-45-6789",         // CRITICAL: SSN
  mrn: "MRN-2024-001",        // CRITICAL: MRN
  dob: "01/15/1985",          // HIGH: Date of birth
};

// ✅ Remediation: Use faker.js instead
const faker = require('faker');
const mockPatient = {
  name: faker.name.fullName(),
  ssn: faker.datatype.string(11),
  mrn: `MRN-${faker.datatype.uuid()}`,
  dob: faker.date.past(),
};
```

### 2. Database Security Audit - Exposed Patient Records

**Scenario**: Hospital discovering potential data leak through logs

```bash
# Scan application logs for PHI exposure
"Check our logs for patient data that shouldn't be there"

# Findings:
❌ application.log:2024-02-07T10:15:33Z
ERROR: Query failed for patient John Doe (SSN: 123-45-6789)

✅ Remediation:
1. Remove specific identifiers from logs
2. Hash or mask sensitive data
3. Use patient ID instead of names
4. Implement log filtering policy

// Good logging pattern:
logger.error(`Query failed for patient: ${patient.id}`);
// Never log: name, SSN, DOB, MRN
```

### 3. FHIR API Validation - Healthcare Data Exchange

**Scenario**: Building HL7 FHIR-compliant patient API

```bash
# Validate FHIR resources before returning to clients
"Check this patient response for PHI safety and FHIR compliance"

// API response - auto-checked:
{
  "resourceType": "Patient",
  "id": "pat-12345",           // ✓ Safe ID only
  "identifier": [...],          // ✓ Medical Record Numbers
  "name": [{"given": [...]}],  // ✓ Patient names (expected)
  "telecom": [...],            // ✓ Phone/email
  "birthDate": "1985-01-15",  // ✓ DOB (expected in healthcare)
  "address": [...]             // ✓ Address data
}

✓ Valid FHIR R5 Patient
✓ All fields appropriate for healthcare context
✓ PHI is expected and necessary
✓ Safe to transmit to authorized clients
```

### 4. Compliance Audit - Meeting HIPAA Requirements

**Scenario**: Annual HIPAA audit for healthcare SaaS company

```bash
# Generate full compliance report
"Run a comprehensive HIPAA compliance check on our entire codebase"

# Generates Report:
├── Executive Summary
│   ├── Overall Risk: MEDIUM
│   ├── Critical Findings: 3
│   ├── High Findings: 12
│   └── Remediation Time: ~16 hours
├── Findings by Category
│   ├── Code Security (12 issues)
│   ├── Configuration (5 issues)
│   ├── Test Data (8 issues)
│   └── Documentation (3 issues)
├── HIPAA Rule Mappings
│   ├── 45 CFR §164.308 (Admin safeguards)
│   ├── 45 CFR §164.312 (Technical safeguards)
│   └── 45 CFR §164.504 (BA requirements)
└── Remediation Playbook
    ├── Priority 1: Critical fixes (3 items)
    ├── Priority 2: High-risk items (12 items)
    └── Timeline and owner assignment
```

## Regulatory References

### HIPAA Rules (45 CFR)
- **Privacy Rule (§164.500+)**: Patient rights, use & disclosure, PHI protections
- **Security Rule (§164.300+)**: Administrative, physical, and technical safeguards
- **Breach Notification Rule (§164.400+)**: Notification requirements & documentation

### Healthcare Standards
- **[HL7 FHIR R5](https://www.hl7.org/fhir/R5/)**: International healthcare data exchange standard
- **[NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework)**: Governance, risk management, detect/respond functions
- **[NIST SP 800-66](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-66r1.pdf)**: HIPAA security implementations
- **[NIST SP 800-188](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-188.pdf)**: De-identification of personal information

### External Resources
- **[HHS HIPAA Guidance](https://www.hhs.gov/hipaa)**: Official HIPAA compliance portal
- **[OCR Enforcement](https://www.hhs.gov/hipaa/for-professionals/special-topics/enforcement)**: HIPAA violations, corrective action plans
- **[HITRUST CSF](https://hitrustalliance.net/csf/)**: Certified HIPAA compliance framework

## Contributing

We welcome contributions! Areas for improvement:
- New healthcare data format support
- Additional HIPAA rule mappings
- Pre-commit hook enhancements
- Language-specific pattern improvements

See skill-specific documentation in `./skills/*/` directories for contribution guidelines.

## Documentation

### Core References
- **[references/HIPAA-OVERVIEW.md](./references/HIPAA-OVERVIEW.md)** - Complete HIPAA rule reference
- **[references/HL7-FHIR-R5.md](./references/HL7-FHIR-R5.md)** - FHIR resource specifications
- **[references/NIST-CSF-2.0.md](./references/NIST-CSF-2.0.md)** - Cybersecurity framework
- **[references/HEALTHCARE-DATA-TYPES.md](./references/HEALTHCARE-DATA-TYPES.md)** - Healthcare formats

### Skill Documentation
- **[skills/hipaa-guardian/](./skills/hipaa-guardian/)** - Core PHI detection skill
- **[skills/fhir-hl7-validator/](./skills/fhir-hl7-validator/)** - Healthcare format validation
- **[skills/healthcare-audit-logger/](./skills/healthcare-audit-logger/)** - Audit logging

## Quick Reference - Activation Phrases

Use these phrases to activate HIPAA Guardian skills in Claude, Cursor, or Windsurf:

### hipaa-guardian Skill
- "Scan for PHI" / "Detect PII"
- "HIPAA compliance check" / "HIPAA audit"
- "Healthcare data security" / "Check code for PHI leakage"
- "Scan logs for PHI" / "Check authentication on PHI endpoints"
- "Generate HIPAA audit report" / "Find sensitive healthcare data"

### fhir-hl7-validator Skill
- "Validate FHIR resource" / "Check HL7 message"
- "Healthcare format validation"
- "Validate FHIR R5" / "Check HL7 v2"

### healthcare-audit-logger Skill
- "Create audit log" / "Compliance logging"
- "Track healthcare access" / "Audit trail"

## FAQ

**Q: Can I use this in production?**
A: These skills are designed to support compliance efforts. Always conduct your own security review, consult your legal/compliance team, and execute a Business Associate Agreement (BAA) with any external providers.

**Q: Does it detect all PHI?**
A: It detects the 18 HIPAA Safe Harbor identifiers with high confidence. However, some context-dependent PHI may require manual review. Always combine automated detection with human review.

**Q: What about false positives?**
A: Confidence scores (0-100%) are provided for each finding. Low-confidence findings may be false positives. Always review findings in context.

**Q: Can I integrate with my CI/CD?**
A: Yes! Check [skills/hipaa-guardian/](./skills/hipaa-guardian/) for GitHub Actions, pre-commit hook, and custom integration examples.

**Q: How do I report security issues?**
A: Please email security vulnerabilities privately (do not create public GitHub issues for security problems).

## Troubleshooting

### Detection Not Finding Expected PHI

1. **Check confidence threshold** - May be filtering low-confidence matches
2. **Verify pattern matches** - Some formats vary (e.g., SSN: 123-45-6789 vs 123456789)
3. **Context matters** - Test data may be intentionally de-identified

### Large Codebase Scanning Slow

1. **Exclude unnecessary directories** - `.git`, `node_modules`, `dist`, `build`
2. **Filter by file type** - Focus on relevant files (code, config, not binaries)
3. **Use batch scanning** - Process directories in smaller chunks

### Remediation Guidance Unclear

1. **Review concrete examples** - Check the skill examples for best practices
2. **Consult references** - [references/](./references/) has detailed guidance
3. **Reach out** - Create an issue with specific use case

## Support

- 📖 **Documentation**: [./references/](./references/) - Detailed guides
- 🐛 **Issues/Features**: [GitHub Issues](https://github.com/1Mangesh1/hipaa-guardian/issues)
- 🔒 **Security Reports**: Report vulnerabilities responsibly (do not create public issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/1Mangesh1/hipaa-guardian/discussions)

## License

MIT License - See [LICENSE.txt](./LICENSE.txt)

**Permissions**: ✓ Commercial use | ✓ Modification | ✓ Distribution | ✓ Private use  
**Conditions**: ⚠️ License and copyright notice required  
**Limitations**: ✗ No warranty | ✗ No liability

---

**Repository**: [1Mangesh1/hipaa-guardian](https://github.com/1Mangesh1/hipaa-guardian)  
**Last Updated**: February 2026  
**Status**: ✅ Active Development  
**Latest Version**: 1.2.0  
**License**: MIT
