# HIPAA Breach Notification Rule Reference

The HIPAA Breach Notification Rule (45 CFR Part 164, Subpart D) requires HIPAA covered entities and business associates to provide notification following a breach of unsecured protected health information.

## Overview

**Citation:** 45 CFR 164.400-414
**Effective Date:** September 23, 2009 (Interim Final Rule)
**HITECH Act:** Health Information Technology for Economic and Clinical Health Act

## Key Definitions

### Breach (164.402)
The acquisition, access, use, or disclosure of PHI in a manner not permitted by the Privacy Rule which compromises the security or privacy of the PHI.

### Unsecured PHI (164.402)
PHI that is not rendered unusable, unreadable, or indecipherable to unauthorized persons through:
- Encryption meeting NIST standards
- Destruction (paper: shredding, electronic: clearing, purging, destroying)

### Compromise
A breach is presumed to compromise PHI unless the covered entity demonstrates low probability that PHI was compromised based on risk assessment.

---

## Breach Exclusions (164.402(1))

A breach does NOT include:

### 1. Unintentional Acquisition
- By workforce member or business associate
- Acting under authority
- In good faith
- Within scope of authority
- No further unauthorized use/disclosure

### 2. Inadvertent Disclosure
- Between authorized persons
- At same entity or business associate
- Information not further used/disclosed impermissibly

### 3. Good Faith Belief
- Unauthorized person could not reasonably retain information
- Example: Misdirected fax immediately returned

---

## Risk Assessment (164.402(2))

### Four-Factor Risk Assessment

To determine if breach notification is required, assess:

| Factor | Assessment Questions |
|--------|---------------------|
| **1. Nature and Extent of PHI** | What types of identifiers? How sensitive? |
| **2. Unauthorized Person** | Who accessed? Known or unknown? |
| **3. PHI Actually Acquired/Viewed** | Was PHI actually seen or just potentially exposed? |
| **4. Extent of Risk Mitigation** | What steps were taken to reduce risk? |

### Risk Assessment Documentation
```yaml
breach_risk_assessment:
  incident_date: YYYY-MM-DD
  discovery_date: YYYY-MM-DD

  factor_1_phi_nature:
    identifiers_involved: [list types]
    clinical_info: [diagnosis, treatment, etc.]
    financial_info: [yes/no]
    sensitivity_level: [low/medium/high]

  factor_2_unauthorized_person:
    identity_known: [yes/no]
    relationship: [employee/vendor/unknown/etc.]
    obligations: [any confidentiality duties]

  factor_3_actual_acquisition:
    evidence_of_access: [yes/no/unknown]
    evidence_of_viewing: [yes/no/unknown]
    extent_of_access: [description]

  factor_4_mitigation:
    actions_taken: [list]
    confirmation_obtained: [yes/no]
    residual_risk: [low/medium/high]

  conclusion:
    notification_required: [yes/no]
    rationale: [explanation]
```

---

## Notification Requirements

### 164.404 - Individual Notification

#### Timing
- **Without unreasonable delay**
- **No later than 60 calendar days** from discovery
- Discovery = when breach is known or should have been known

#### Content Requirements
| Element | Description |
|---------|-------------|
| Description | Brief description of what happened |
| Types of Information | What PHI was involved |
| Steps to Take | What individuals should do to protect themselves |
| Entity Actions | What entity is doing to investigate, mitigate, prevent |
| Contact Procedures | How to contact entity for questions |

#### Delivery Methods
1. **First-class mail** to last known address
2. **Email** if individual has agreed to electronic notice
3. **Substitute notice** if contact info insufficient:
   - < 10 individuals: Alternative written/phone notice
   - ≥ 10 individuals: Conspicuous website posting (90 days) or major media

### 164.406 - Media Notification

#### When Required
- Breach affecting **500 or more residents** of a state/jurisdiction

#### Timing
- Without unreasonable delay
- No later than 60 days from discovery

#### Method
- Prominent media outlets in affected state/jurisdiction

### 164.408 - HHS Notification

#### For Breaches Affecting 500+ Individuals
- Contemporaneous with individual notification
- No later than 60 days from discovery
- Submit via HHS breach portal

#### For Breaches Affecting < 500 Individuals
- Annual submission to HHS
- Within 60 days of end of calendar year
- Maintain log of all breaches

### 164.410 - Business Associate Notification

#### Business Associate Responsibilities
- Notify covered entity without unreasonable delay
- No later than 60 days from discovery
- Provide information for covered entity to notify individuals

---

## Breach Notification Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    BREACH DISCOVERED                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Is PHI involved? Is it unsecured?                   │
│                                                                  │
│  Yes → Continue          No → Not a HIPAA breach                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Does exclusion apply?                               │
│                                                                  │
│  Yes → Document, no notification   No → Continue                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Conduct 4-factor risk assessment                    │
│                                                                  │
│  Low probability → Document    Not low → Notification required  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Determine notification scope                        │
│                                                                  │
│  < 500 affected: Individual + Annual HHS                        │
│  ≥ 500 affected: Individual + HHS + Media (if state-based)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              Send notifications within 60 days                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Breach Documentation Requirements

### Required Documentation
1. Risk assessment and determination
2. Notification content and timing
3. Evidence of notification delivery
4. Remediation actions taken

### Retention
- Six years from date of creation
- Or six years from last effective date

---

## Compliance Mapping for Findings

### Potential Breach Detection
```json
{
  "finding_type": "potential_breach",
  "rule_section": "164.402",
  "description": "PHI potentially exposed to unauthorized access",
  "assessment_required": true,
  "steps": [
    "Conduct 4-factor risk assessment",
    "Document assessment findings",
    "Determine notification requirements",
    "Implement remediation measures"
  ],
  "timeline": {
    "assessment": "Immediately upon discovery",
    "notification": "Within 60 days if required"
  }
}
```

### Unsecured PHI Finding
```json
{
  "finding_type": "unsecured_phi",
  "rule_section": "164.402",
  "description": "PHI stored without encryption",
  "risk": "If accessed, would constitute reportable breach",
  "remediation": [
    "Implement encryption (AES-128 minimum)",
    "Document encryption implementation",
    "Update risk assessment"
  ]
}
```

### Breach Notification Gap
```json
{
  "finding_type": "notification_gap",
  "rule_section": "164.404-410",
  "description": "Breach notification procedures incomplete",
  "gaps_identified": [
    "No documented notification templates",
    "No media notification procedure",
    "HHS portal access not configured"
  ],
  "remediation": [
    "Develop notification templates",
    "Establish media notification procedure",
    "Configure HHS breach portal access",
    "Train incident response team"
  ]
}
```

---

## Breach Notification Templates

### Individual Notification Letter
```markdown
[Date]

[Individual Name]
[Address]

RE: Notice of Data Breach

Dear [Name],

We are writing to inform you of a security incident that may have affected
your protected health information.

**What Happened:**
[Brief description of incident]

**What Information Was Involved:**
[Types of PHI involved - name, dates, medical information, etc.]

**What We Are Doing:**
[Steps taken to investigate, contain, and prevent future incidents]

**What You Can Do:**
[Recommended protective actions - credit monitoring, review statements, etc.]

**For More Information:**
[Contact information - phone, email, address]

We sincerely apologize for any inconvenience or concern this may cause.

Sincerely,
[Privacy Officer Name]
[Title]
```

### HHS Breach Report Content
Required fields for HHS submission:
- Covered entity name and contact
- Business associate involved (if applicable)
- Date of breach and discovery
- Type of breach (theft, loss, unauthorized access, etc.)
- Location of breached PHI
- Types of PHI involved
- Number of individuals affected
- Safeguards in place
- Actions taken

---

## Penalties

### HITECH Act Enhanced Penalties
| Violation Type | Minimum | Maximum |
|---------------|---------|---------|
| Unknown | $100 | $50,000 |
| Reasonable Cause | $1,000 | $50,000 |
| Willful Neglect - Corrected | $10,000 | $50,000 |
| Willful Neglect - Not Corrected | $50,000 | $1,500,000 |

### State Attorney General Enforcement
- States may bring civil actions
- $100 per violation, $25,000 maximum per calendar year
- Per identical provision violated

### Reputational Impact
- Required media notification for large breaches
- HHS public breach portal listing
- Potential class action lawsuits

---

## Safe Harbor - Encryption Standards

PHI is considered "secured" if encrypted using:

### Data at Rest
- NIST Special Publication 800-111
- AES-128, AES-192, or AES-256

### Data in Motion
- NIST Special Publications 800-52, 800-77, 800-113
- TLS 1.2 or higher
- IPsec VPN

### Key Management
- Keys stored separately from encrypted data
- Access to keys strictly controlled
- Key destruction documented

If properly encrypted data is lost/stolen, breach notification is NOT required.
