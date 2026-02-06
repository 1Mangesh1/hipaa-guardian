# Healthcare Data Types & PHI Detection Patterns

## 18 PHI Identifiers - Detection Patterns

### 1. Names
**Pattern**: Full names, partial names (first/last only)

**Examples**:
- ✅ "John Smith"
- ✅ "Smith, John"
- ✅ "J.S."
- ✅ "Dr. Sarah Johnson"
- ✅ "Mr. Michael Chen"

**hipaa-guardian Detection**:
- Name dictionaries (first/last name databases)
- Title + surname (Mr., Dr., Ms., Mrs., Prof.)
- Name with suffix (Jr., Sr., III)

**Context**: Any name in medical context (patient, provider, family) = PHI

---

### 2-4. Dates (Birth, Service, Admission)

**Patterns**:
- Birth dates: YYYY-MM-DD, MM/DD/YYYY, "born in 1980", "age 45"
- Service dates: "admitted 02/07/2026", "procedure date Jan 15"
- Anniversary dates: "5 years post-op" (calculates to service date)

**Examples**:
- ✅ "DOB: 01/15/1980"
- ✅ "Patient is 45 years old, born 1980"
- ✅ "Admission: February 7, 2026"
- ✅ "5-year survival post-transplant (transplant 2021)"

**Safe Harbor**: Only YEAR allowed in de-identified data

**hipaa-guardian Detection**:
- Regex: `\b(19|20)\d{2}[\/-](0[1-9]|1[0-2])[\/-](0[1-9]|[12]\d|3[01])\b`
- Age + birth year calculation
- Relative dates "3 years ago" (infers service date)
- Season + year "winter 2023" (vulnerable individuals in small dataset)

---

### 5-7. Contact Information

#### Telephone Numbers
**Pattern**: (123) 456-7890, 123-456-7890, 1-800-555-1212

**Examples**:
- ✅ "555-0123"
- ✅ "(617) 555-9876"
- ✅ "Call +1-800-DOCTOR"

**Regex**: `(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})|(\d{10})`

#### Email Addresses
**Pattern**: user@domain.com

**Examples**:
- ✅ "john.smith@hospital.org"
- ✅ "patient-123@gmail.com"

**Regex**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`

#### Fax Numbers
**Pattern**: Similar to phone (healthcare context = fax)

---

### 8. Social Security Numbers (SSN)

**Pattern**: XXX-XX-XXXX (9 digits)

**Social Security Number Format Restrictions**:
- Area number (first 3 digits):
  - 000 = invalid
  - 666 = invalid
  - 778-899 = invalid (EIN - employer, not SSN)
- Group (middle 2 digits): 00 = invalid
- Serial (last 4 digits): 0000 = invalid

**Examples**:
- ✅ "123-45-6789"
- ✅ "123456789" (no dashes)
- ❌ "000-00-0000" (invalid - not PHI)
- ❌ "789-12-3456" (invalid - area > 899)

**Regex with validation**: `(?!000)(?!666)\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}`

---

### 9. Medical Record Numbers (MRN)

**Patterns** (institution-specific):
- Hospital MRN: "123456" (6-digit), "H123456789" (H + prefix)
- SSA: "SSA-123456" format
- Military: "N123456A" (military service number)

**Examples**:
- ✅ "MRN: 987654"
- ✅ "Chart #: 12345678"
- ✅ "REC ID: R-2024-001234"
- ✅ "HMS:0000123456"

**hipaa-guardian Detection**:
- Known MRN patterns per institution
- Contextual: "MRN:", "Chart #:", "Record ID:" labels
- Format validation: length, character types (alphanumeric typical)

---

### 10. Health Plan Numbers

**Examples**:
- ✅ "Member ID: 123456789ABC"
- ✅ "Group #: 54321"
- ✅ "Policy #: POL-2024-001234"
- ✅ "Medicaid #: 123456789"
- ✅ "Medicare #: 1ZZ1234567A"

**Patterns**: 
- Aetna: 17 alphanumeric
- United: 9-11 digits
- Medicaid: state-specific (varies 9-13+ characters)
- Medicare: "1" + SSN + letter (for Medicare beneficiaries)

**hipaa-guardian Detection**:
- Label detection ("Member ID:", "Policy Number:")
- Format patterns per common insurers
- State Medicaid format validation (if applicable)

---

### 11. Certificate & License Numbers

**Examples**:
- ✅ "MD License: License #12345"
- ✅ "DEA Registration: C123456789"
- ✅ "NPI: 1234567890"
- ✅ "Board Certification: #2024-001234"

**Common Identifiers**:
- **NPI** (National Provider ID): 10 digits, healthcare provider
- **DEA** (Drug Enforcement Admin): Letter + digits, prescriber license
- **MD License**: State + number
- **Nursing License**: State RN#, LPN#

---

### 12. Vehicle Identifiers

**Examples**:
- ✅ License plate: "ABC 1234" or "ABC1234"
- ✅ VIN: "1HGCM41JXFA110186"

**VIN Patterns**: 17 characters, specific structure

**hipaa-guardian Detection**:
- License plate formats (state-specific if mentioned)
- VIN format validation (checksum validation per ISO 3779)
- Context: "vehicle", "license plate", "VIN"

---

### 13. Device Serial Numbers

**Examples** (sensitive for implanted devices):
- ✅ "Pacemaker SN: PM-2024-123456"
- ✅ "Insulin Pump: 722G123456"
- ✅ "Prosthetic Valve: PV-XYZ-789"

**Security**: Implanted device serial number per device manufacturer

**hipaa-guardian Detection**:
- Known device prefixes (PM-, CGMS-, etc.)
- Context: "device", "serial", "implant"
- Length/format per device type

---

### 14. URLs & Websites

**Examples**:
- ✅ "www.johndoephotography.com" (personal website)
- ✅ "https://patient-portal.hospital.org/user/john-smith" (patient portal)

**hipaa-guardian Detection**:
- URLs containing personal names
- Patient portal URLs with identifiable parameters
- Social media URLs linking to individuals

---

### 15. IP Addresses

**Examples**:
- ✅ "192.168.1.100"
- ✅ "2606:4700:4700::1111" (IPv6)

**Note**: Institutional IPs (proxy/VPN) may be safe harbor if random assignment; static IPs = PHI

**hipaa-guardian Detection**:
- Static IP assignment (requires network knowledge)
- Unusual IPs in patient documentation context

---

### 16. Biometric Identifiers

**Examples**:
- ✅ Fingerprint scans (any digital representation)
- ✅ Retinal scan images
- ✅ Voice samples/voiceprints
- ✅ Genetic sequences (DNA, RNA)

**hipaa-guardian Detection**:
- File types: fingerprint image formats (.fp, proprietary scanners)
- DNA sequences (FASTA format, genomic coordinates)
- Voice samples (.wav, .mp3 containing person's voice)

---

### 17. Photographic Images

**Examples**:
- ✅ Patient photo in medical record
- ✅ Before/after surgical photos
- ✅ X-rays with visible identifying marks
- ✅ Screenshots of patient portal (contains name)

**Exception**: X-rays, pathology slides WITHOUT identifying marks = sometimes allowed in research

**hipaa-guardian Detection**:
- Image metadata (EXIF data with timestamps, location)
- OCR on images to detect text (name, MRN burned into image)
- Face detection (identifies individual)

---

### 18. Unique Identifiers

**Examples**:
- ✅ Passport number
- ✅ National ID number
- ✅ Driver's license number
- ✅ Student ID (if patient is student)
- ✅ Employee ID (healthcare worker = provider, not patient)

**hipaa-guardian Detection**:
- Known patterns per country (US, Canada, EU, etc.)
- Context: "passport", "national ID", "driver's license"

---

## Sensitive Healthcare Categories

### Level 1: Standard PHI
**Detection Trigger**: Name + date + service

### Level 2: Sensitive Categories (Enhanced Protection)
Conditions requiring EXTRA confidentiality:

| Category | Why | Extra Controls |
|---|---|---|
| **HIV/AIDS** | Stigma, discrimination | Require patient permission for disclosure |
| **Psychiatric** | Mental health privacy | Special authorization required |
| **Substance Abuse** | Legal protections (42 CFR Part 2) | Stricter than general HIPAA |
| **Reproductive Health** | Sensitive decisions | Require explicit authorization |
| **Genetic** | Family implications | Special consent requirements |
| **Genetic Testing** | Forensic use possible | Enhanced security |

**hipaa-guardian Flags**:
- ⚠️ "HIV" mention (any form: "HIV status", "ARV therapy")
- ⚠️ "Psychiatric" diagnosis (depression, schizophrenia, etc.)
- ⚠️ "Substance abuse treatment" mention
- ⚠️ "Abortion", "miscarriage" in context
- ⚠️ Genetic test results (DNA, ancestry)

---

## Entropy-Based Detection

**Concept**: Some PHI is encoded/hashed but can be detected by entropy patterns.

**Examples**:
- ✅ UUID format: "550e8400-e29b-41d4-a716-446655440000" (potentially hashed MRN)
- ✅ Base64 encoded: "MTIzNDU2Nzg5" = likely number (base64)
- ✅ Hash: "5d41402abc4b2a76b9719d911017c592" = MD5 of "hello"

**hipaa-guardian Detection**:
- Entropy calculation: High-entropy strings in healthcare context
- Known hash patterns (MD5, SHA-1, SHA-256)
- Base64/hex detection + decode

**Warning**: Encryption looks like random data, so context matters!

---

## Pattern Detection Examples

### Example 1: Clinical Note with Multiple PHI
```
Patient Name: John Smith
DOB: 01/15/1980
MRN: H0123456
Insurance: BCBS, Member ID: 987654321
Contact: (617) 555-9876
Email: j.smith@gmail.com

Chief Complaint: Patient presents with chest pain. 
Vital Signs: BP 128/76, HR 82
Diagnosis: Angina pectoris, Type 2 Diabetes

Plan: Refer to cardiology (Boston Medical Center, 555-0100)
```

**PHI Detected**:
1. ✅ Name: "John Smith"
2. ✅ DOB: "01/15/1980"
3. ✅ MRN: "H0123456"
4. ✅ Health Plan Number: "987654321"
5. ✅ Phone: "(617) 555-9876"
6. ✅ Email: "j.smith@gmail.com"
7. ✅ Facility: "Boston Medical Center"

**Risk Assessment**: HIGH (7/18 identifiers present)

---

### Example 2: De-identified Research Dataset
```
Patient ID: RES-00001
Age: 45
Gender: M
Diagnosis: Type 2 Diabetes, Hypertension
Lab: Glucose 118, Creatinine 0.9
Treatment: Metformin 1000mg BID
```

**PHI Check**:
1. ❌ No name
2. ❌ No DOB (only age, allowed)
3. ❌ No MRN (research ID instead)
4. ❌ No contact info
5. ❌ No sensitive dates (no admit, service dates)

**Risk Assessment**: LOW - Likely safe harbor de-identified

---

**Last Updated**: February 2026  
**Detection Patterns Version**: 2.0
