# HIPAA Guardian

**AI-powered HIPAA compliance, PHI/PII detection, and healthcare data security skills.**

This collection provides specialized tools for healthcare professionals, developers, and organizations building HIPAA-compliant systems using AI agents like Claude, Cursor, Windsurf, and others.

## Purpose

Automate detection of Protected Health Information (PHI), validate healthcare data formats, maintain compliance audit trails, and integrate with healthcare standards like HL7 FHIR and NIST Cybersecurity Framework 2.0.

## What's Included

- **PHI/PII Detection**: 18+ PHI identifiers per 45 CFR §164.103
- **Healthcare Format Support**: HL7 v2, FHIR R5, CDA, X12 EDI parsing
- **Compliance Features**: HIPAA audit logging, breach risk assessment, de-identification validation
- **Standards Alignment**: HL7 FHIR R5, NIST CSF 2.0, HITRUST CSF

## Usage

See [README.md](./README.md) for installation and detailed documentation.

See [COMPLIANCE.md](./COMPLIANCE.md) for regulatory compliance matrix.

See [SECURITY.md](./SECURITY.md) for technical safeguards and encryption specifications.

## Folder Structure

```
HIPAA Guardian/
├── skills/
│   └── hipaa-guardian/        # Main HIPAA compliance skill
├── references/                 # Healthcare standards and compliance docs
├── README.md                   # Quick start guide
├── SKILL.md                    # This file - skill collection overview
├── COMPLIANCE.md               # Regulatory mapping (45 CFR §164+)
├── SECURITY.md                 # Technical safeguards
└── CONTRIBUTING.md             # Development guidelines
```

## Legal Notice

This skill collection is designed to support HIPAA compliance but does not guarantee HIPAA compliance. For production environments:
- Consult with your legal and compliance team
- Execute a Business Associate Agreement (BAA) with any service provider
- Conduct your own security and compliance review

**License**: MIT
