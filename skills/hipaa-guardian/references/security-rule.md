# HIPAA Security Rule Reference

The HIPAA Security Rule (45 CFR Part 164, Subpart C) establishes national standards for protecting electronic protected health information (ePHI).

## Overview

**Citation:** 45 CFR 164.302-318
**Effective Date:** April 20, 2005
**Applies To:** Covered entities and business associates

## General Requirements (164.306)

### Security Standards
Covered entities and business associates must:
1. Ensure confidentiality, integrity, and availability of ePHI
2. Protect against reasonably anticipated threats
3. Protect against reasonably anticipated unauthorized uses/disclosures
4. Ensure workforce compliance

### Flexibility of Approach
Consider when implementing safeguards:
- Size, complexity, and capabilities
- Technical infrastructure, hardware, software
- Cost of security measures
- Probability and criticality of potential risks

---

## Administrative Safeguards (164.308)

### 164.308(a)(1) - Security Management Process

| Specification | Type | Description |
|--------------|------|-------------|
| Risk Analysis | Required | Accurate assessment of risks to ePHI |
| Risk Management | Required | Implement measures to reduce risks |
| Sanction Policy | Required | Sanctions for workforce violations |
| Information System Activity Review | Required | Regular review of audit logs |

#### Risk Analysis Requirements
```yaml
risk_analysis:
  scope: All ePHI created, received, maintained, transmitted
  identify:
    - Where ePHI is stored
    - How ePHI flows
    - Potential threats and vulnerabilities
  assess:
    - Likelihood of threat occurrence
    - Impact of threat exploitation
  document:
    - Risk assessment methodology
    - Risk ratings and rationale
    - Remediation priorities
```

### 164.308(a)(2) - Assigned Security Responsibility
- **Required:** Identify security official responsible for policies and procedures
- Document assignment
- Ensure authority to implement security program

### 164.308(a)(3) - Workforce Security

| Specification | Type | Description |
|--------------|------|-------------|
| Authorization/Supervision | Addressable | Procedures for workforce access |
| Workforce Clearance | Addressable | Procedures for access determination |
| Termination Procedures | Addressable | Procedures for access termination |

### 164.308(a)(4) - Information Access Management

| Specification | Type | Description |
|--------------|------|-------------|
| Isolating Healthcare Clearinghouse | Required | If clearinghouse part of larger org |
| Access Authorization | Addressable | Policies for granting access |
| Access Establishment/Modification | Addressable | Procedures for access changes |

### 164.308(a)(5) - Security Awareness and Training

| Specification | Type | Description |
|--------------|------|-------------|
| Security Reminders | Addressable | Periodic security updates |
| Protection from Malware | Addressable | Procedures for guarding/detecting malware |
| Log-in Monitoring | Addressable | Procedures for monitoring log-in attempts |
| Password Management | Addressable | Procedures for creating/changing passwords |

### 164.308(a)(6) - Security Incident Procedures
- **Required:** Policies to identify and respond to security incidents
- Document incidents and outcomes
- Mitigate harmful effects

### 164.308(a)(7) - Contingency Plan

| Specification | Type | Description |
|--------------|------|-------------|
| Data Backup Plan | Required | Procedures to create/maintain copies |
| Disaster Recovery Plan | Required | Procedures to restore lost data |
| Emergency Mode Operations Plan | Required | Procedures to enable critical functions |
| Testing and Revision | Addressable | Periodic testing of plans |
| Applications and Data Criticality Analysis | Addressable | Assess relative criticality |

### 164.308(a)(8) - Evaluation
- **Required:** Periodic technical and non-technical evaluation
- In response to environmental/operational changes
- Document evaluation results

### 164.308(b)(1) - Business Associate Contracts
- **Required:** Contracts with business associates
- Must include security requirements
- Must establish permitted uses/disclosures

---

## Physical Safeguards (164.310)

### 164.310(a)(1) - Facility Access Controls

| Specification | Type | Description |
|--------------|------|-------------|
| Contingency Operations | Addressable | Procedures for facility access during emergency |
| Facility Security Plan | Addressable | Safeguard facility and equipment |
| Access Control/Validation | Addressable | Procedures to validate access |
| Maintenance Records | Addressable | Document repairs and modifications |

### 164.310(b) - Workstation Use
- **Required:** Policies for proper workstation use
- Specify functions, access methods, physical attributes
- Consider physical surroundings

### 164.310(c) - Workstation Security
- **Required:** Physical safeguards for workstations
- Restrict access to authorized users
- Consider portable devices

### 164.310(d)(1) - Device and Media Controls

| Specification | Type | Description |
|--------------|------|-------------|
| Disposal | Required | Policies for final disposition |
| Media Re-use | Required | Procedures for removing ePHI before reuse |
| Accountability | Addressable | Record of hardware/media movements |
| Data Backup and Storage | Addressable | Retrievable exact copy before movement |

---

## Technical Safeguards (164.312)

### 164.312(a)(1) - Access Control

| Specification | Type | Description |
|--------------|------|-------------|
| Unique User Identification | Required | Assign unique identifier to each user |
| Emergency Access Procedure | Required | Procedures for obtaining ePHI during emergency |
| Automatic Logoff | Addressable | Terminate session after inactivity |
| Encryption and Decryption | Addressable | Mechanism to encrypt/decrypt ePHI |

#### Access Control Implementation Checklist
```markdown
- [ ] Unique user IDs assigned
- [ ] Role-based access control implemented
- [ ] Access levels documented
- [ ] Emergency access procedures documented
- [ ] Automatic session timeout configured (recommended: 15 minutes)
- [ ] Encryption implemented for ePHI at rest
- [ ] Encryption implemented for ePHI in transit
```

### 164.312(b) - Audit Controls
- **Required:** Hardware, software, and/or procedural mechanisms
- Record and examine system activity
- Implement in information systems containing ePHI

#### Audit Log Requirements
```yaml
audit_logs:
  events_to_log:
    - User login/logout
    - PHI access (read, create, modify, delete)
    - Failed access attempts
    - Security events
    - Administrative actions
  content:
    - User ID
    - Timestamp
    - Action performed
    - Resource accessed
    - Success/failure
  retention: 6 years minimum
  protection:
    - Integrity verification
    - Access restricted
    - Regular review
```

### 164.312(c)(1) - Integrity

| Specification | Type | Description |
|--------------|------|-------------|
| Mechanism to Authenticate ePHI | Addressable | Corroborate ePHI not altered/destroyed |

#### Integrity Controls
- Digital signatures
- Checksums/hash values
- Database integrity constraints
- Version control
- Change detection

### 164.312(d) - Person or Entity Authentication
- **Required:** Procedures to verify identity
- Before granting access to ePHI
- Something you know/have/are

#### Authentication Methods
| Method | Examples | Strength |
|--------|----------|----------|
| Knowledge | Password, PIN, security questions | Basic |
| Possession | Token, smart card, phone | Medium |
| Inherence | Biometrics (fingerprint, face) | Strong |
| Multi-factor | Combination of above | Strongest |

### 164.312(e)(1) - Transmission Security

| Specification | Type | Description |
|--------------|------|-------------|
| Integrity Controls | Addressable | Ensure ePHI not improperly modified |
| Encryption | Addressable | Mechanism to encrypt ePHI in transmission |

#### Encryption Standards
```yaml
encryption:
  at_rest:
    recommended: AES-256
    minimum: AES-128
    key_management: Required
  in_transit:
    recommended: TLS 1.3
    minimum: TLS 1.2
    certificate: Valid, trusted CA
  key_management:
    storage: Hardware security module or equivalent
    rotation: Annual minimum
    access: Strictly controlled
```

---

## Organizational Requirements (164.314)

### 164.314(a) - Business Associate Contracts
Requirements for contracts with business associates:
- Implement appropriate safeguards
- Report security incidents
- Ensure subcontractor compliance
- Authorize termination for material breach

### 164.314(b) - Group Health Plans
Requirements for group health plan documents:
- Implement safeguards
- Ensure separation from plan sponsor
- Report security incidents

---

## Documentation Requirements (164.316)

### 164.316(a) - Policies and Procedures
- Implement reasonable and appropriate policies
- Written form (electronic allowed)
- Make available to workforce

### 164.316(b)(1) - Documentation

| Specification | Type | Description |
|--------------|------|-------------|
| Time Limit | Required | Retain for 6 years from creation or last effective date |
| Availability | Required | Make available to responsible persons |
| Updates | Required | Review and update as necessary |

---

## Security Rule Compliance Mapping

### Access Control Violations
```json
{
  "violation_type": "access_control",
  "rule_section": "164.312(a)(1)",
  "description": "Inadequate access controls for ePHI",
  "findings": [
    "Shared user accounts",
    "No automatic session timeout",
    "Missing encryption"
  ],
  "remediation": [
    "Implement unique user identification",
    "Configure automatic logoff",
    "Implement encryption for ePHI at rest",
    "Document access control procedures"
  ]
}
```

### Audit Control Violations
```json
{
  "violation_type": "audit_controls",
  "rule_section": "164.312(b)",
  "description": "Insufficient audit logging",
  "findings": [
    "PHI access not logged",
    "No log review process",
    "Logs not retained"
  ],
  "remediation": [
    "Implement comprehensive audit logging",
    "Establish log review procedures",
    "Configure 6-year log retention",
    "Protect log integrity"
  ]
}
```

### Transmission Security Violations
```json
{
  "violation_type": "transmission_security",
  "rule_section": "164.312(e)(1)",
  "description": "ePHI transmitted without encryption",
  "findings": [
    "HTTP used instead of HTTPS",
    "Unencrypted email with PHI",
    "FTP used for PHI transfer"
  ],
  "remediation": [
    "Implement TLS 1.2+ for all transmissions",
    "Configure email encryption",
    "Use SFTP instead of FTP",
    "Document transmission security controls"
  ]
}
```

### Risk Analysis Violations
```json
{
  "violation_type": "risk_analysis",
  "rule_section": "164.308(a)(1)(ii)(A)",
  "description": "Inadequate or missing risk analysis",
  "findings": [
    "No documented risk assessment",
    "Incomplete scope",
    "Outdated analysis"
  ],
  "remediation": [
    "Conduct comprehensive risk analysis",
    "Document all ePHI locations",
    "Assess threats and vulnerabilities",
    "Update annually or when changes occur"
  ]
}
```

---

## Control Validation Checklist

```markdown
## Administrative Safeguards
- [ ] Security official designated
- [ ] Risk analysis completed and documented
- [ ] Risk management plan implemented
- [ ] Sanction policy in place
- [ ] Security awareness training conducted
- [ ] Incident response procedures documented
- [ ] Contingency plan established
- [ ] Business associate agreements current

## Physical Safeguards
- [ ] Facility access controls implemented
- [ ] Workstation use policies documented
- [ ] Workstation security measures in place
- [ ] Device and media disposal procedures documented

## Technical Safeguards
- [ ] Unique user IDs assigned
- [ ] Access control mechanisms implemented
- [ ] Audit logging enabled
- [ ] Integrity controls in place
- [ ] Authentication procedures documented
- [ ] Transmission encryption implemented
```

---

## Penalties

Same as Privacy Rule penalties:
| Violation Category | Minimum | Maximum |
|-------------------|---------|---------|
| Unknown | $100 | $50,000 |
| Reasonable Cause | $1,000 | $50,000 |
| Willful Neglect (Corrected) | $10,000 | $50,000 |
| Willful Neglect (Not Corrected) | $50,000 | $1,500,000 |

**Annual Cap:** $1,500,000 per violation category
