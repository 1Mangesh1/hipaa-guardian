# HIPAA Privacy Rule Reference

The HIPAA Privacy Rule (45 CFR Part 164, Subpart E) establishes national standards for the protection of individually identifiable health information.

## Overview

**Citation:** 45 CFR 164.500-534
**Effective Date:** April 14, 2003
**Applies To:** Covered entities and business associates

## Key Definitions

### Protected Health Information (PHI)
Individually identifiable health information transmitted or maintained in any form or medium that:
- Is created or received by a covered entity
- Relates to past, present, or future physical or mental health condition
- Relates to provision of health care
- Relates to payment for health care
- Identifies the individual or provides reasonable basis for identification

### Covered Entities
1. **Health Plans** - Health insurance companies, HMOs, government programs (Medicare, Medicaid)
2. **Health Care Clearinghouses** - Entities that process health information
3. **Health Care Providers** - Who transmit health information electronically

### Business Associates
Persons or organizations that perform functions involving PHI on behalf of covered entities.

---

## Core Privacy Requirements

### 164.502 - Uses and Disclosures

#### Permitted Uses Without Authorization
| Use/Disclosure | Description | Citation |
|---------------|-------------|----------|
| Treatment | Providing care | 164.506(c)(1) |
| Payment | Billing, claims | 164.506(c)(2) |
| Healthcare Operations | Quality, training | 164.506(c)(3) |
| Public Health | Reporting, surveillance | 164.512(b) |
| Health Oversight | Audits, investigations | 164.512(d) |
| Judicial Proceedings | Court orders, subpoenas | 164.512(e) |
| Law Enforcement | Specific circumstances | 164.512(f) |
| Research | With IRB/Privacy Board approval | 164.512(i) |

#### Required Authorizations
Written authorization required for:
- Marketing communications
- Sale of PHI
- Psychotherapy notes
- Uses not described in Notice of Privacy Practices

### 164.508 - Authorization Requirements

Valid authorization must contain:
- [ ] Description of information to be used/disclosed
- [ ] Name of person authorized to make disclosure
- [ ] Name of person to whom disclosure may be made
- [ ] Purpose of use/disclosure
- [ ] Expiration date or event
- [ ] Signature of individual and date
- [ ] If signed by representative, authority statement

---

## Minimum Necessary Standard (164.502(b))

### Requirement
Covered entities must make reasonable efforts to limit PHI to the minimum necessary to accomplish the intended purpose.

### Exceptions (Minimum Necessary Does Not Apply)
- Disclosures to the individual
- Treatment purposes
- Uses authorized by individual
- Disclosures to HHS for compliance
- Required by law
- Required by HIPAA

### Implementation Requirements
| Role | Requirement |
|------|-------------|
| Workforce | Identify who needs access, limit accordingly |
| Routine Disclosures | Develop standard protocols |
| Non-routine Disclosures | Develop criteria for review |
| Requests | Request only minimum necessary |

---

## Individual Rights

### 164.524 - Right of Access
- Individuals have right to inspect and obtain copy of PHI
- Must be provided within 30 days (one 30-day extension permitted)
- Reasonable, cost-based fees allowed
- Limited exceptions (psychotherapy notes, legal proceedings)

### 164.526 - Right to Amend
- Individuals may request amendment of PHI
- Must respond within 60 days
- May deny if PHI is accurate and complete
- Must append denial if requested

### 164.528 - Right to Accounting of Disclosures
- Individuals may request list of disclosures
- Covers 6 years prior to request
- Exceptions: treatment, payment, operations, certain others
- Must be provided within 60 days

### 164.522 - Right to Request Restrictions
- Individuals may request restrictions on uses/disclosures
- Covered entity not required to agree (with exceptions)
- Must comply with agreed restrictions

### 164.522(b) - Confidential Communications
- Individuals may request alternative means/locations for communication
- Must accommodate reasonable requests

---

## De-identification Standards (164.514)

### Safe Harbor Method (164.514(b))
Remove all 18 identifiers:
1. Names
2. Geographic data (smaller than state)
3. Dates (except year)
4. Phone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. Web URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photographs
18. Any other unique identifying number

**AND** No actual knowledge that remaining info could identify individual.

### Expert Determination (164.514(b)(1))
Statistical/scientific expert determines risk of identification is very small.

---

## Limited Data Set (164.514(e))

PHI with direct identifiers removed but may include:
- Dates (admission, discharge, service, birth, death)
- Geographic data (city, state, ZIP)
- Ages

**Requirements:**
- Data use agreement required
- Can be used for research, public health, healthcare operations

---

## Notice of Privacy Practices (164.520)

### Required Content
- [ ] Uses and disclosures of PHI
- [ ] Individual rights
- [ ] Covered entity duties
- [ ] Contact information for complaints
- [ ] Effective date

### Distribution Requirements
| Entity Type | Requirement |
|-------------|-------------|
| Health Plans | Provide at enrollment, every 3 years |
| Providers | Provide at first service, post in facility |
| Electronic Notice | Available upon request |

---

## Administrative Requirements

### 164.530(a) - Personnel Designations
- **Privacy Officer** - Responsible for policies and compliance
- **Contact Person** - Receives complaints

### 164.530(b) - Training
- Train all workforce members
- Document training
- Retrain when functions change

### 164.530(c) - Safeguards
- Appropriate administrative, technical, physical safeguards
- Protect against intentional or unintentional violations

### 164.530(d) - Complaints
- Process for receiving and handling complaints
- Cannot retaliate against complainants

### 164.530(e) - Sanctions
- Sanctions for workforce members who violate policies
- Document sanctions applied

### 164.530(f) - Mitigation
- Mitigate harmful effects of violations
- To the extent practicable

### 164.530(j) - Documentation
- Maintain policies and procedures
- Six-year retention requirement

---

## Compliance Mapping for Findings

When PHI is detected, map to relevant Privacy Rule sections:

### Unauthorized Disclosure
```json
{
  "violation_type": "unauthorized_disclosure",
  "rule_section": "164.502(a)",
  "description": "PHI disclosed without authorization or permitted use",
  "remediation": [
    "Determine scope of disclosure",
    "Assess if breach notification required",
    "Document incident",
    "Implement additional safeguards"
  ]
}
```

### Minimum Necessary Violation
```json
{
  "violation_type": "minimum_necessary",
  "rule_section": "164.502(b)",
  "description": "More PHI disclosed than necessary for purpose",
  "remediation": [
    "Review disclosure policies",
    "Implement role-based access",
    "Train workforce on minimum necessary",
    "Audit access patterns"
  ]
}
```

### Missing De-identification
```json
{
  "violation_type": "insufficient_deidentification",
  "rule_section": "164.514(b)",
  "description": "Data contains identifiers that should be removed",
  "remediation": [
    "Apply Safe Harbor de-identification",
    "Remove all 18 identifiers",
    "Document de-identification process",
    "Verify no re-identification risk"
  ]
}
```

---

## Penalties

| Violation Category | Minimum | Maximum |
|-------------------|---------|---------|
| Unknown | $100 | $50,000 |
| Reasonable Cause | $1,000 | $50,000 |
| Willful Neglect (Corrected) | $10,000 | $50,000 |
| Willful Neglect (Not Corrected) | $50,000 | $1,500,000 |

**Annual Cap:** $1,500,000 per violation category
**Criminal Penalties:** Up to $250,000 and 10 years imprisonment
