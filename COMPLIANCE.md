# HIPAA Compliance Matrix

This document maps HIPAA regulations to specific safeguards and controls implemented in HIPAA Guardian skills.

## Regulatory Framework

### HIPAA Privacy Rule (45 CFR §164.500-534)

| Regulation | Requirement | Safeguard | HIPAA Guardian Skill |
|-----------|-------------|-----------|----------------------|
| §164.500 | Applicability | Organizational policies | hipaa-guardian |
| §164.502 | Uses & disclosures | Minimum necessary standard | hipaa-guardian |
| §164.503 | Notice of privacy practices | Transparency | hipaa-guardian |
| §164.506 | Authorization | Explicit patient consent | hipaa-guardian |
| §164.508 | Uses & disclosures authorization | Written authorization | hipaa-guardian |
| §164.512 | Use & disclosure for permitted purposes | Business associates, law enforcement | hipaa-guardian |
| §164.514(b) | De-identification | Safe harbor method | hipaa-guardian |
| §164.514(e)(1) | Limited data sets | File restricted identifiers | hipaa-guardian |

**Skill Controls**:
- PHI identifier detection (18 standards from §164.103)
- De-identification validation & safe harbor checking
- Limited data set file formatting
- Use & disclosure auditing

---

### HIPAA Security Rule (45 CFR §164.300-320)

#### Administrative Safeguards (§164.308)

| Requirement | Control | Implementation |
|------------|---------|-----------------|
| §164.308(a)(1) | Security management process | Risk assessment, mitigation |
| §164.308(a)(3) | Workforce security | Access provisioning & termination |
| §164.308(a)(4) | Information access management | Role-based access control (RBAC) |
| §164.308(a)(5) | Security awareness & training | Staff training logs, documentation |
| §164.308(a)(7) | Contingency planning | Backup, recovery, disaster plans |
| §164.308(a)(8) | Evaluation | Annual security reviews |

**hipaa-guardian Support**:
- Audit logging for access tracking (§164.312(b))
- Training documentation templates
- Risk assessment frameworks

#### Physical Safeguards (§164.310)

| Requirement | Control | Implementation |
|------------|---------|-----------------|
| §164.310(a)(1) | Facility access controls | Key cards, biometric access |
| §164.310(a)(2) | Visitor logs | Physical access tracking |
| §164.310(b) | Workstation security | Screen locks, VPN requirements |
| §164.310(c) | Workstation access log | Activity logging, monitoring |
| §164.310(d) | Device & media controls | Secure disposal, tracking |

**hipaa-guardian Support**:
- Session access auditing  
- Configuration templates for environment setup
- Compliance checklists

#### Technical Safeguards (§164.312)

| Requirement | Control | Implementation |
|------------|---------|-----------------|
| §164.312(a)(1) | Access controls | User authentication, encryption keys |
| §164.312(a)(2) | Encryption & decryption | AES-256, TLS 1.3 minimum |
| **§164.312(b)** | **Audit controls** | **Immutable audit logs** |
| §164.312(c) | Integrity controls | Digital signatures, checksums |
| §164.312(d) | Transmission security | End-to-end encryption, VPN tunnels |

**hipaa-guardian Support**:
- ✅ Audit trail creation & management (§164.312(b))
- ✅ PHI detection feeding audit events
- ✅ Compliance-ready event logging formats
- ✅ Immutability validation

#### Organizational Requirements (§164.314)

| Requirement | Control | Implementation |
|------------|---------|-----------------|
| §164.314(a) | Business associate contracts | Required BAA clauses |
| §164.314(b) | Other arrangements | Written agreements |

**hipaa-guardian Support**:
- Documentation of third-party integrations
- Data flow diagrams for risk assessment

---

### HIPAA Breach Notification Rule (45 CFR §164.400-414)

| Regulation | Requirement | hipaa-guardian Support |
|-----------|-------------|----------------------|
| §164.400 | Notification requirements | Breach detection, risk assessment |
| §164.401 | Notification of unsecured PHI | Triggering conditions |
| §164.402 | Notification to individuals | Notification templates |
| §164.403 | Notification to media | Media notification templates |
| §164.404 | Notification to Secretary | Administrative notice |
| §164.406 | Timeliness | Timeline tracking |
| §164.408 | Implementation specifications | Notification language |
| §164.410 | Delay of notification | Law enforcement notification |

**Skill Features**:
- Rapid PHI breach detection
- Risk assessment (likelihood of compromise)
- Notification threshold evaluation
- Regulatory timeline tracking

---

## Standards & Frameworks Integration

### HL7 FHIR R5 Compliance

**Data standards for healthcare data exchange**:

| FHIR Resource | HIPAA Mapping | Safeguards |
|---|---|---|
| Patient | Master patient index | MRN, SSN, DOB detection |
| Observation | Clinical measurements | Result privacy controls |
| MedicationRequest | Medication orders | Sensitive medication safeguards |
| Condition | Problem list | Sensitive diagnosis protection |
| Encounter | Visit data | Access & use controls |
| Appointment | Scheduling | Date/location privacy |
| Device | Implanted devices | Sensitive device tracking |
| CarePlan | Treatment plans | Sensitive treatment protection |

**hipaa-guardian Support**:
- FHIR resource schema validation
- Patient identifier extraction from FHIR bundles
- Compliance-ready FHIR data export

---

### NIST Cybersecurity Framework 2.0 Mapping

| CSF Function | HIPAA Alignment | hipaa-guardian Action |
|---|---|---|
| **Govern (GV)** | Risk management, policies | Documentation, assessment |
| **Detect (DE)** | §164.312(b) Audit controls | PHI detection, anomaly detection |
| **Respond (RS)** | Breach response | Incident tracking, notification |
| **Protect (PR)** | Technical safeguards | Encryption, access controls |
| **Recover (RC)** | Contingency planning | Backup validation, disaster recovery |

---

## Audit Trail Requirements (§164.312(b))

### Mandatory Fields

Per HIPAA Security Rule §164.312(b), audit trail logs MUST include:

```json
{
  "timestamp": "ISO 8601 UTC",
  "user_id": "system account identifier",
  "action_type": "CREATE|READ|UPDATE|DELETE|LOGIN|LOGOUT|EXPORT",
  "resource_type": "PHI|FHIR_Resource|Audit_Record",
  "resource_id": "unique identifier",
  "success": true,
  "ip_address": "source IP",
  "status_code": "HTTP status or custom code",
  "details": "additional context",
  "immutable": true
}
```

### hipaa-guardian Audit Format

```
{
  "event_id": "unique UUID",
  "timestamp": "2026-02-07T14:30:00.000Z",
  "action": "PHI_SCAN|FHIR_VALIDATE|DECRYPT_REQUEST",
  "operator": "system|user_identifier",
  "patient_id": "[redacted or MRN]",
  "phi_detected": ["name", "dob", "mrn"],
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "compliance_checked": true,
  "outcome": "COMPLIANT|NON_COMPLIANT|REVIEW_REQUIRED",
  "immutable_hash": "SHA-256 previous entry hash"
}
```

---

## De-Identification Safe Harbor (§164.514(b))

### 18 Identifiers to Remove (Safe Harbor Method)

Per 45 CFR §164.514(b)(2), hipaa-guardian detects and flags:

1. Names (patient, provider)
2. Geographic subdivisions (city, county, latitude/longitude)
3. All dates (birth, service, admission)
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers & serial numbers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full photographic images
18. Any unique identifier (MRN, patient ID)

**hipaa-guardian Coverage**: 18/18 (100%)

---

## Compliance Checklist

Use this checklist with hipaa-guardian for HIPAA compliance assessment:

- [ ] Privacy Policy documented & distributed
- [ ] Security Awareness Training completed (annual)
- [ ] Access Controls configured (usernames, passwords, multi-factor auth)
- [ ] Audit Controls enabled & monitored (§164.312(b))
- [ ] Encryption implemented (data at rest & in transit)
- [ ] Business Associate Agreements signed
- [ ] De-identification procedures documented
- [ ] Breach Response Plan developed & tested
- [ ] Disaster Recovery Plan documented
- [ ] Annual Risk Assessment completed
- [ ] Sanctions for non-compliance defined
- [ ] Workforce security procedures implemented
- [ ] Information access management configured
- [ ] Contingency planning & testing completed
- [ ] Evaluation procedures scheduled (annual)

---

## Related Documentation

- [SECURITY.md](./SECURITY.md) - Technical safeguards & architecture
- [references/HIPAA-OVERVIEW.md](./references/HIPAA-OVERVIEW.md) - HIPAA rules summary
- [references/NIST-CSF-2.0.md](./references/NIST-CSF-2.0.md) - NIST framework mapping
- [references/HL7-FHIR-R5.md](./references/HL7-FHIR-R5.md) - FHIR standards guide
- [references/AUDIT-STANDARDS.md](./references/AUDIT-STANDARDS.md) -  Audit trail implementation

---

**Last Updated**: February 2026  
**Compliance Version**: 1.0  
**Next Review**: February 2027
