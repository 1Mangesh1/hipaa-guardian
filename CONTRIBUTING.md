# Contributing to HIPAA Guardian

Thank you for helping improve HIPAA compliance tooling! This guide covers contribution standards.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hipaa-guardian.git
   cd hipaa-guardian
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feat/phi-detection-improvement
   ```

## Code & Documentation Standards

### HIPAA Compliance

All contributions must:

- ✅ Follow 45 CFR §164 regulatory requirements
- ✅ Document any PHI/PII handling
- ✅ Include audit logging considerations
- ✅ Be compatible with NIST CSF 2.0
- ✅ Reference official regulatory guidance

### PHI Detection Rules

When adding PHI detection patterns:

1. **Document the PHI type** (e.g., MRN, SSN, date of birth)
2. **Reference HIPAA regulation** (e.g., 45 CFR §164.103)
3. **Include test cases**:
   ```
   - Valid: 123-45-6789
   - Invalid: 000-00-0000 (excluded per NIST SP 800-188)
   ```
4. **Validate entropy** for UUID/hash detection
5. **Test false positive rates**

### Documentation Updates

When modifying compliance files:

**COMPLIANCE.md**:
- Update regulatory matrix if CFR changes
- Link to HHS OCR guidance
- Include implementation checklist

**SECURITY.md**:
- Document technical safeguards
- Reference NIST SP 800-52, 800-66, 800-188
- Include encryption/authentication specs
- Add incident response procedures

**references/**:
- **HIPAA-OVERVIEW.md**: 18 PHI identifiers, Privacy/Security/Breach rules
- **NIST-CSF-2.0.md**: Framework functions and maturity tiers
- **HL7-FHIR-R5.md**: Healthcare data standards and validation
- **HEALTHCARE-DATA-TYPES.md**: PHI patterns, sensitivity levels, detection
- **AUDIT-STANDARDS.md**: Logging requirements, cryptographic integrity, retention

## Skill Development

### hipaa-guardian Skill

The core skill provides:

1. **PHI Detection** - Scan for 18 protected identifiers
2. **Validation** - Check FHIR resource compliance
3. **Audit Logging** - 45 CFR §164.312(b) compliant
4. **Remediation** - Guidance for found violations

### Code Requirements

```python
# Example PHI detection function
def detect_phi(content: str, sensitivity: str = "medium") -> List[Finding]:
    """
    Detect PHI in content.
    
    Args:
        content: Text to scan
        sensitivity: "low" (names only) | "medium" (standard) | "high" (all)
        
    Returns:
        List of findings with:
        - type: PHI identifier type (SSN, MRN, date, etc.)
        - pattern: Matched pattern
        - risk_level: CRITICAL | HIGH | MEDIUM | LOW
        - remediation: Recommended fix
    """
```

## Regulatory Compliance Checklist

Before submitting contributions:

- [ ] References 45 CFR §164 sections (Privacy, Security, Breach)
- [ ] Complies with NIST CSF 2.0 (Govern, Detect, Protect, Respond, Recover, Inform)
- [ ] Includes HL7 FHIR R5 or CDA validation where applicable
- [ ] Audit logging follows §164.312(b) specifications
- [ ] Documentation cites HHS OCR guidelines
- [ ] No unintended PHI logging in error messages

## Testing Requirements

1. **Unit Tests**: PHI detection accuracy
   ```bash
   # Example test cases
   - SSN validation: 123-45-6789 ✓, 000-00-0000 ✗, 666-00-0001 ✗
   - MRN patterns: institution-specific formats
   - Date handling: YYYY-MM-DD, MM/DD/YYYY, relative dates
   - Risk scoring: entropy-based detection
   ```

2. **Integration Tests**: FHIR validation, audit log formatting

3. **Compliance Tests**: Verify against regulatory checklist

## Commit Message Conventions

Use semantic commits:

```
feat(phi-detection): add medical record number validation
fix(audit-logging): ensure timestamp in UTC per §164.312(b)
docs(compliance): update NIST CSF 2.0 mapping
chore(references): add HITRUST CSF alignment
test(detection): improve SSN validation test coverage
```

## Pull Request Process

1. **Reference a regulatory requirement** in PR description
2. **Link to HHS guidance** or official standards
3. **Include test results** showing PHI detection accuracy
4. **Validate against checklist** (see above)
5. **Update COMPLIANCE.md** if policies affected

### PR Template

```markdown
## Regulatory Reference
Addresses 45 CFR §164.[section] - [regulation name]

## NIST CSF Function
Maps to: [Govern|Detect|Protect|Respond|Recover|Inform]

## Changes
- [] PHI detection improvement
- [ ] Compliance documentation
- [ ] Audit logging enhancement
- [ ] FHIR validation

## Testing
- [ ] Unit tests pass
- [ ] Compliance checklist verified
- [ ] Documentation updated

## References
- HHS OCR Guidance: [link]
- NIST SP 800-66: [reference]
```

## Skill Quality Checklist

Before submitting:

- [ ] All PHI handling documented
- [ ] Audit logging compliant with §164.312(b)
- [ ] FHIR validation tested
- [ ] Encryption specs match NIST SP 800-52
- [ ] Error messages don't leak PHI
- [ ] References link to official HHS/NIST docs
- [ ] Regulatory citations accurate
- [ ] Code follows Python best practices

## License & Legal

By contributing, you agree:

1. **MIT License**: Contributions licensed under MIT
2. **HIPAA Disclaimer**: Not a substitute for legal compliance review
3. **BAA**: Users must establish Business Associate Agreements as applicable

## How to Get Help

- **Regulatory Questions**: Review HHS OCR guidance
- **NIST CSF**: Check NIST SP 800-66 implementation guidance
- **HL7 FHIR**: See HL7.org official specifications
- **Issues**: Open GitHub issue with regulatory reference

## Code of Conduct

- Treat all contributors with respect
- Assume good intent
- Focus on regulatory accuracy, not politics
- Cite authoritative standards

---

Thank you for strengthening HIPAA compliance tooling! 🛡️
