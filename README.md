# HIPAA Guardian

**AI-powered HIPAA compliance, PHI/PII detection, and healthcare data security skills for Claude, Cursor, Windsurf, and AI agents.**

HIPAA Guardian is a specialized skills collection designed for healthcare professionals, developers, and organizations building HIPAA-compliant systems. It provides automated tools for detecting Protected Health Information (PHI), validating healthcare data formats, maintaining compliance audit trails, and integrating with healthcare standards like HL7 FHIR and NIST Cybersecurity Framework 2.0.

## ⚠️ Compliance Statement

- ✅ **HIPAA-Ready**: Designed for HIPAA BAA (Business Associate Agreement) environments
- ✅ **Audit Trail**: Supports immutable logging per 45 CFR §164.312(b)
- ✅ **Standards Integration**: HL7 FHIR R5, NIST CSF 2.0, HITRUST CSF alignment
- ✅ **Open Source**: MIT License, security-first code review process

> **Note**: This skill collection is designed to support HIPAA compliance but does not guarantee HIPAA compliance. For production environments, consult with your legal and compliance team and execute a Business Associate Agreement (BAA) with any service provider.

## Installation

```bash
# Install all HIPAA Guardian skills
npx skills add @1mangesh1/hipaa-guardian

# Install specific skill
npx skills add @1mangesh1/hipaa-guardian --skill hipaa-guardian
```

## Available Skills (1)

| Skill | Purpose | Standards | Version |
|-------|---------|-----------|---------|
| [hipaa-guardian](./skills/hipaa-guardian/) | PHI/PII detection, healthcare format validation, compliance audit logging | HIPAA §164.500+, NIST SP 800-188, HL7 FHIR R5 | 1.2.0 |

### hipaa-guardian Skill Features

**PHI Detection**:
- 18 PHI identifiers per 45 CFR §164.103
- MRN (Medical Record Number), SSN, patient names, DOB patterns
- Health plan beneficiary numbers, facility identification
- Entropy-based detection for encoded/hashed PHI

**Healthcare Format Support**:
- HL7 v2 message validation (OBX, RXO, ADT segments)
- FHIR R5 resource schemas (Patient, Observation, MedicationRequest)
- CDA (Clinical Document Architecture) document parsing
- X12 EDI healthcare claims format

**Compliance Features**:
- HIPAA audit trail logging (§164.312(b))
- Breach risk assessment
- De-identification validation
- NIST CSF 2.0 alignment (Detect, Respond functions)

**Integration Ready**:
- Claude Code, Cursor, and AI agent prompt activation triggers
- OpenAPI 3.1 specification for plugin-based deployment
- Works with MCP servers for extended functionality

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

## Getting Started

### Activation Triggers

The hipaa-guardian skill is automatically recommended when you mention:
- "scan for PHI", "detect PII", "protected health information"
- "HIPAA compliance", "HIPAA audit", "healthcare data security"
- "FHIR validation", "HL7 support", "health insurance portability"
- "audit trail", "compliance logging", "breach assessment"

## Contributing

Contributions are welcome! Please review:
1. [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
2. [COMPLIANCE.md](./COMPLIANCE.md) - Regulatory mapping for new skills
3. [SECURITY.md](./SECURITY.md) - Security guidelines for healthcare data handling

## Documentation

- **[COMPLIANCE.md](./COMPLIANCE.md)** - HIPAA compliance matrix with regulatory mappings
- **[SECURITY.md](./SECURITY.md)** - Security architecture and data handling practices
- **[references/](./references/)** - Detailed guides on HIPAA rules, HL7 FHIR, NIST CSF

## Support

- **Documentation**: [./references/](./references/) directory for detailed guides
- **Issues**: Report bugs or feature requests on GitHub
- **Security**: Report security vulnerabilities privately to security@example.com

## License

MIT License - See [LICENSE.txt](./LICENSE.txt)

---

**Last Updated**: February 2026  
**Repository**: [1Mangesh1/hipaa-guardian](https://github.com/1Mangesh1/hipaa-guardian)  
**Status**: Active Development
