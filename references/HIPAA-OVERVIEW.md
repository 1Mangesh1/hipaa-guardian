# HIPAA Rules Overview

## What is HIPAA?

**HIPAA** = Health Insurance Portability and Accountability Act (1996)

A federal law mandating administrative, physical, and technical safeguards for Protected Health Information (PHI) in the United States. HIPAA applies to **Covered Entities** (healthcare providers, health plans, healthcare clearinghouses) and **Business Associates** (vendors processing PHI).

---

## PHI Definition

**Protected Health Information (PHI)** = Any information in medical records or health plans that can identify an individual (45 CFR §164.103).

### 18 PHI Identifiers (Safe Harbor Standard)
1. **Names** - Full or partial patient/provider names
2. **Geographic subdivisions** - Address (street level+), city, county, latitude/longitude
3. **All dates** - Birth date, admission date, discharge date, service dates (except year)
4. **Telephone numbers** - Patient, provider, facility phone numbers
5. **Fax numbers** - Patient, provider, facility fax numbers
6. **Email addresses** - Patient, provider, facility email
7. **Social Security numbers (SSN)** - Unique identifier
8. **Medical Record Numbers (MRN)** - Patient hospital record ID
9. **Health plan beneficiary numbers** - Insurance member IDs
10. **Account numbers** - Patient financial account numbers
11. **Certificate/license numbers** - Professional license, credential numbers
12. **Vehicle identifiers** - License plate, VIN numbers
13. **Device identifiers & serial numbers** - Implant serials, pacemaker IDs
14. **URLs** - Patient's or provider's URLs (web addresses)
15. **IP addresses** - Device IP addresses, system identifiers
16. **Biometric identifiers** - Fingerprints, retinal patterns, voice recordings
17. **Full photographic images** - Patient photos, images that identify individuals
18. **Any unique population-based identifier** - Passport, national ID, census information

**Note**: Year of birth IS allowed in limited contexts if aggregate data (not individual records).

---

## Three Rules: Privacy, Security, Breach Notification

### Rule 1: Privacy Rule (45 CFR §164.500-534)

**Purpose**: Protect the privacy of PHI

**Key Concepts**:

| Concept | Definition |
|---------|-----------|
| **PHI** | Any health information that identifies an individual |
| **Covered Entity** | Provider, health plan, clearinghouse |
| **Business Associate** | Vendor processing PHI on behalf of covered entity |
| **Minimum Necessary** | Only use/disclose the minimum amount needed for the purpose |
| **Authorization** | Written patient permission required for non-standard uses |
| **Use** | Internal application of PHI (within organization) |
| **Disclosure** | Sharing PHI outside the organization |

**Patient Rights**:
- ✅ Access to their medical records payable(§164.524)
- ✅ Amend/correct errors (§164.526)
- ✅ Request restriction on uses/disclosures (§164.522)
- ✅ Request confidential communications (§164.522)
- ✅ Accounting of disclosures (§164.528)
- ✅ Copy of privacy notice (§164.520)

**Permitted Uses/Disclosures** (without authorization):
- Treatment (clinical care)
- Payment (processing claims, billing)
- Healthcare Operations (administration, compliance, quality improvement)
- Public Health Activities (disease reporting, vital statistics)
- Law Enforcement (with proper authorization, court order)

**Prohibited Uses/Disclosures** (without authorization):
- ❌ Marketing (with exceptions)
- ❌ Sale of PHI
- ❌ Genetic testing/research
- ❌ Substance abuse treatment info (special rules)
- ❌ Mental health records (sensitive category)
- ❌ HIV/AIDS status (special protections)

---

### Rule 2: Security Rule (45 CFR §164.300-320)

**Purpose**: Implement safeguards for electronic PHI (ePHI)

**Three Categories of Safeguards**:

#### Administrative Safeguards (§164.308)
**Management processes & responsibilities**:

| Safeguard | Requirement | Example |
|-----------|-------------|---------|
| Security Management | Risk analysis & mitigation | Annual risk assessment |
| Workforce Security | User access control | ID badges, access provisioning |
| Information Access | RBAC, segregation of duties | Data analyst ≠ Data destroyer |
| Security Awareness | Training & documentation | Annual training, signed acknowledgment |
| Sanctions | Penalties for violations | Termination, legal action |
| Contingency Planning | Disaster recovery, backups | Tested backup restoration |
| Evaluation | Periodic security reviews | Annual security audit |

#### Physical Safeguards (§164.310)
**Environmental controls**:

| Safeguard | Requirement | Example |
|-----------|-------------|---------|
| Facility Access | Lock doors, key cards, guards | Swipe card access logs |
| Workstation Security | Screen locks, VPN, encryption | Auto-lock after 15 min |
| Workstation Use | Acceptable use policy | No personal USB, no screenshots |
| Device/Media | Secure disposal, inventory tracking | Shred old hard drives |

#### Technical Safeguards (§164.312)
**Technology & encryption**:

| Safeguard | Requirement |  Example |
|-----------|-------------|---------|
| Access Control | Authentication, encryption keys | Multi-factor auth, role-based access |
| Audit Controls | Log all access & changes | Immutable audit trail 6+ years |
| Integrity Controls | Detect alterations | Digital signatures, cryptographic hashing |
| Transmission Security | Encrypt data moving | TLS 1.3 for all PHI transmission |

**Minimum Encryption Standards**:
- **At Rest**: AES-256-GCM
- **In Transit**: TLS 1.3 minimum
- **In Use**: Protected from display (screen locks, etc.)

---

### Rule 3: Breach Notification Rule (45 CFR §164.400-414)

**Purpose**: Notify individuals & HHS if unsecured PHI is exposed

**Definition of Breach** (§164.404):
> "Unauthorized acquisition, access, use, or disclosure of PHI that compromises the security or privacy of the information."

**Breach vs. Not a Breach**:

| Incident | Determination | Example |
|----------|---|---|
| Lost unencrypted USB drive | BREACH | Contains patient records in plaintext |
| Lost encrypted USB drive | MAYBE | If robust encryption, different risk level |
| Deleted backup tapes secured | NOT BREACH | No "acquisition" or "access" by unauthorized party |
| Insider views 1-2 records (authorized access) | NOT BREACH | Not "unauthorized" - person has access |
| Malware exfiltrates 10,000 records | BREACH | Unauthorized access confirmed |

**Risk Assessment Per §164.164.404(b)(2)**:

Factors determining "reasonable cause to believe there is a low probability that PHI has been compromised":
1. Nature & extent of PHI involved
2. Who accessed/disclosed it
3. What they did with it
4. Evidence of actual misuse received
5. Extent of risk mitigation

**Example - USB Drive Lost**:
```
PHI Involved: 500 patient records (demographics only, no diagnosis)
Who: Unknown person found on street
Evidence: Encryption password protected device, no plaintext recovery possible
Assessment: Low probability of compromise (encryption + small dataset)
Action: No notification needed
```

---

## Notification Requirements (§164.404-410)

### Timing: "In the most expedient time possible and in no case later than 60 calendar days"

### To Whom:
- ✅ **Individuals**: Each person whose PHI was breached
- ✅ **HHS Secretary**: For all breaches (OCR.Compliance@hhs.gov)
- ✅ **Media**: If 500+ individuals in same jurisdiction (wire services, newspapers)

### What to Say (Notification Template):
```
[HEALTHCARE ORGANIZATION NAME]
NOTICE OF PRIVACY BREACH

Dear [Patient Name],

We are writing to inform you that we have discovered a  
data breach that may have involved your protected health information.

WHAT HAPPENED:
[Describe the breach in plain language]
- Date/time range of breach
- What information was involved (not too specific)
- How breach was discovered
- Current status/containment

WHAT WE'RE DOING NOW:
- Investigation underway or completed
- Individuals notified of breach
- Cooperation with law enforcement (if applicable)
- Steps to secure systems

WHAT YOU CAN DO:
- Monitor your medical records for errors
- Watch for medical identity theft
- Contact [phone number] with questions
- Free credit monitoring offered [if applicable]

CONTACT INFORMATION:
[Office contact, hours, languages available]

For more information:
- HIPAA Breach Notification Rule: www.hhs.gov/hipaa
- FTC Identity Theft: www.identitytheft.gov
```

---

## De-Identification (§164.514)

Two methods to remove PHI from data:

### Method 1: Safe Harbor (§164.514(b))

**Remove all 18 identifiers** to create de-identified data:

✅ After removal: Dataset is "de-identified" & NOT PHI (no HIPAA protections required)

Example:

```
BEFORE (PHI):
Patient Smith, DOB 1/15/1980, MRN 123456
Diagnosis: Type 2 Diabetes
Insurance: Aetna, ID# 987654321

AFTER (De-identified):
Patient [REMOVED], DOB [REMOVED], MRN [REMOVED]
Diagnosis: Type 2 Diabetes
Insurance: [REMOVED]

Analysis: Diagnosis allowed! All 18 identifiers removed = Safe Harbor
```

### Method 2: Expert Determination (§164.514(b)(1)(ii))

**Statistician/expert reviews** the data to confirm re-identification is more than theoretical possibility.

More flexible than Safe Harbor but requires:
- Written certification by expert (statistician, epidemiologist)
- Expert analysis of remaining identifiers
- Population size considerations
- Availability of external identifiers

---

## Limited Data Sets (§164.514(e))

**Hybrid approach**: Allows certain identifiers, but only for approved research.

**Data you CAN include**:
- Birth/death dates (year only)
- Geographic regions (state/country only, not street address)
- Medical record numbers
- Health plan numbers
- Device identifiers
- Admission/discharge/service dates (year/month only)

**Data you MUST remove**:
- Names, street addresses, email, phone numbers
- SSN, MRN specific patient identifiers
- Any other identifying information

**Requirements**:
- **Use Agreement**: Data recipient signs agreement limiting use to listed purposes
- **Purpose**: Only for research, public health, healthcare operations
- **Minimum Necessary**: Only identifiers needed for stated purpose

---

## Business Associate Agreement (BAA)

**Requirement**: If vendor handles PHI on your behalf, must have a written BAA.

**BAA Must Include**:
- ✅ Permitted uses/disclosures of PHI
- ✅ Confidentiality obligations
- ✅ Standards for safeguarding PHI
- ✅ Breach notification obligations
- ✅ Subcontractor arrangements (if vendor uses another vendor)
- ✅ Access/amendment/accounting rights
- ✅ Termination procedures
- ✅ Return/destruction of PHI upon termination

**Example Vendors Requiring BAAs**:
- Cloud storage providers (AWS, Azure, Google Cloud)
- EHR/practice management systems
- Billing/revenue cycle companies
- Data analytics platforms
- Legal/consulting firms with access to PHI
- IT consultants (if they see PHI)

---

## Penalties for Violations

| Violation Tier | Per Violation | Annual Max |
|---|---|---|
| Unknowing violation | $100-$50K | $1.5M |
| Reasonable cause | $1K-$100K | $1.5M |
| Willful neglect (corrected <30 days) | $10K-$50K | $1.5M |
| Willful neglect (not corrected) | $50K | $1.5M+ |

**Criminal Penalties**:
- Individual obtaining/disclosing PHI knowingly: **$250K fine + 10 years prison**
- For commercial advantage/malicious harm: **$250K fine +15 years prison**

---

## State Privacy Laws

**Note**: Many states have stronger privacy laws than HIPAA:

| State | Law | Key Feature |
|-------|-----|-------------|
| California | CCPA (2020) | Individual right to delete, broader scope |
| Virginia | VCDPA (2023) | Data broker registration, consumer rights |
| New York | GenISIS (2023) | Genetic privacy, specific protections |
| Texas | TDPSA (2023) | Consumer data protection rights |

**Compliance Strategy**: Often must comply with **strictest rule** (usually CCPA or state law + HIPAA).

---

## Compliance Checklist

Use this checklist annually to verify HIPAA compliance:

- [ ] Privacy Notice posted & distributed to patients
- [ ] Workforce trained on HIPAA annually (documented)
- [ ] Business Associate Agreements signed with all vendors
- [ ] Risk Assessment completed & documented
- [ ] Security safeguards implemented per risk assessment
- [ ] Encryption enabled (at rest & in transit)
- [ ] Access controls configured (authentication, RBAC)
- [ ] Audit logging enabled & monitored (6-year retention)
- [ ] Breach Response Plan documented & tested
- [ ] Disaster Recovery Plan documented & tested (annual test)
- [ ] De-identification procedures documented (if applicable)
- [ ] Sanctions policy documented & communicated
- [ ] Contingency plan reviewed & tested
- [ ] Evaluation/audit scheduled (annually)
- [ ] Corrective actions from prior audits tracked & closed

---

**Last Updated**: February 2026  
**Version**: 1.0
