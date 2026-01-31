# HIPAA Safe Harbor Identifiers

The HIPAA Privacy Rule identifies 18 types of identifiers that must be removed or protected to de-identify Protected Health Information (PHI) under the Safe Harbor method (45 CFR 164.514(b)(2)).

## The 18 HIPAA Identifiers

### 1. Names
**Description:** All names including patient, provider, relative, employer, or household member names.

**Examples:**
- Full names: "John Smith", "Mary Jane Watson"
- Partial names: First name + last initial
- Maiden names, aliases, nicknames

**Detection Patterns:**
```regex
# Name patterns (use with NLP/dictionary validation)
\b[A-Z][a-z]+\s+[A-Z][a-z]+\b
```

**Classification:** PHI when combined with health information

---

### 2. Geographic Data (smaller than state)
**Description:** All geographic subdivisions smaller than a state, including street address, city, county, precinct, ZIP code.

**Special Rule:** First 3 digits of ZIP may be retained if population > 20,000

**Examples:**
- Street addresses: "123 Main Street"
- Cities: "Boston", "Los Angeles"
- ZIP codes: "02134" (must generalize to "021XX" or remove)
- Counties, precincts, geocodes

**Detection Patterns:**
```regex
# Street addresses
\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)\b

# ZIP codes (5 or 9 digit)
\b\d{5}(-\d{4})?\b
```

**Classification:** PHI - geographic identifiers

---

### 3. Dates (except year)
**Description:** All elements of dates (except year) directly related to an individual, including birth date, admission date, discharge date, death date, and all ages over 89.

**Examples:**
- Birth dates: "03/15/1985", "March 15, 1985"
- Admission dates: "Admitted 01/20/2024"
- Ages over 89: Must be aggregated to "90+"

**Detection Patterns:**
```regex
# MM/DD/YYYY or MM-DD-YYYY
\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](\d{2}|\d{4})\b

# YYYY-MM-DD (ISO format)
\b\d{4}-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])\b

# Written dates
\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b

# DOB/Date of Birth markers
\b(DOB|Date\s+of\s+Birth|Birth\s*date|Born)\s*[:\-]?\s*\d
```

**Classification:** PHI when linked to individual

---

### 4. Telephone Numbers
**Description:** All telephone numbers including home, work, cell, pager.

**Examples:**
- Standard: "(617) 555-1234"
- Without area code: "555-1234"
- International: "+1-617-555-1234"

**Detection Patterns:**
```regex
# US phone formats
\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b

# International format
\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}
```

**Classification:** PII - direct contact identifier

---

### 5. Fax Numbers
**Description:** All fax numbers.

**Examples:**
- Same formats as telephone numbers
- Often prefixed with "Fax:" or "F:"

**Detection Patterns:**
```regex
# Fax with label
\b[Ff]ax\s*[:#]?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b
```

**Classification:** PII - direct contact identifier

---

### 6. Email Addresses
**Description:** All electronic mail addresses.

**Examples:**
- Personal: "john.smith@gmail.com"
- Work: "jsmith@hospital.org"
- Healthcare portals: "patient123@mychart.com"

**Detection Patterns:**
```regex
\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b
```

**Classification:** PII - direct contact identifier

---

### 7. Social Security Numbers
**Description:** Social Security Numbers in any format.

**Examples:**
- Standard: "123-45-6789"
- Without dashes: "123456789"
- Partial: "XXX-XX-6789"

**Detection Patterns:**
```regex
# SSN with dashes
\b\d{3}-\d{2}-\d{4}\b

# SSN without dashes (9 consecutive digits)
\b\d{9}\b

# SSN with label
\b(SSN|Social\s*Security)\s*[:#]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b
```

**Classification:** PHI - unique national identifier

**Risk Level:** CRITICAL - highest sensitivity

---

### 8. Medical Record Numbers
**Description:** Medical record numbers assigned by healthcare providers.

**Examples:**
- "MRN: 12345678"
- "Medical Record #: A-123456"
- "Patient ID: P00123456"

**Detection Patterns:**
```regex
# MRN patterns
\b(MRN|MR#?|Medical\s*Record(\s*Number)?|Patient\s*ID)\s*[:#]?\s*[A-Z]?\d{5,12}\b

# Generic patient identifiers
\b(PID|PAT|PT)\s*[:#]?\s*\d{6,10}\b
```

**Classification:** PHI - healthcare-specific identifier

---

### 9. Health Plan Beneficiary Numbers
**Description:** Health insurance policy numbers and member IDs.

**Examples:**
- "Member ID: XYZ123456789"
- "Policy #: 987654321"
- "Subscriber ID: ABC12345"

**Detection Patterns:**
```regex
# Health plan identifiers
\b(Member\s*ID|Policy\s*(Number|#|No)|Subscriber\s*ID|Insurance\s*ID|Group\s*Number)\s*[:#]?\s*[A-Z0-9]{6,15}\b

# Medicare/Medicaid
\b(Medicare|Medicaid)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{9,12}\b
```

**Classification:** PHI - insurance identifier

---

### 10. Account Numbers
**Description:** Financial account numbers including bank accounts, billing accounts.

**Examples:**
- Bank accounts: "Account: 1234567890"
- Billing accounts: "Billing #: 98765432"
- Credit cards: "4111-1111-1111-1111"

**Detection Patterns:**
```regex
# Account numbers
\b(Account|Acct)\s*(Number|#|No)?\s*[:#]?\s*\d{8,17}\b

# Credit card patterns (Luhn-validatable)
\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b
```

**Classification:** PII - financial identifier

---

### 11. Certificate/License Numbers
**Description:** Driver's licenses, professional licenses, certificates.

**Examples:**
- Driver's license: "DL: S12345678"
- Medical license: "DEA: AB1234567"
- Nursing license: "RN License: 123456"

**Detection Patterns:**
```regex
# Driver's license
\b(Driver'?s?\s*License|DL|DLN)\s*[:#]?\s*[A-Z]?\d{5,12}\b

# DEA numbers
\b(DEA)\s*[:#]?\s*[A-Z]{2}\d{7}\b

# Professional licenses
\b(License|Lic)\s*(Number|#|No)\s*[:#]?\s*[A-Z0-9]{5,12}\b
```

**Classification:** PII - government-issued identifier

---

### 12. Vehicle Identifiers
**Description:** Vehicle identification numbers (VIN), license plates.

**Examples:**
- VIN: "1HGBH41JXMN109186"
- License plate: "ABC-1234"

**Detection Patterns:**
```regex
# VIN (17 characters, no I, O, Q)
\b[A-HJ-NPR-Z0-9]{17}\b

# License plates (varies by jurisdiction)
\b[A-Z0-9]{1,4}[-\s]?[A-Z0-9]{1,4}\b
```

**Classification:** PII - property identifier

---

### 13. Device Identifiers and Serial Numbers
**Description:** Medical device identifiers, serial numbers, UDI.

**Examples:**
- Device serial: "SN: ABC123456789"
- UDI: "(01)00888888888888(17)221231(10)ABC123"
- Implant IDs: "Implant #: 12345"

**Detection Patterns:**
```regex
# Serial numbers
\b(Serial|SN|S/N)\s*[:#]?\s*[A-Z0-9]{6,20}\b

# UDI format
\(\d{2}\)\d{14}

# Device identifiers
\b(Device|Implant|Equipment)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{5,15}\b
```

**Classification:** PHI when linked to patient

---

### 14. Web URLs
**Description:** Web Universal Resource Locators.

**Examples:**
- Patient portals: "https://mychart.hospital.org/patient/12345"
- Personal websites: "http://johnsmith.com"

**Detection Patterns:**
```regex
\bhttps?://[A-Za-z0-9.-]+(/[A-Za-z0-9./_-]*)?\b
```

**Classification:** PII if contains identifying info

---

### 15. IP Addresses
**Description:** Internet Protocol addresses (IPv4 and IPv6).

**Examples:**
- IPv4: "192.168.1.100"
- IPv6: "2001:0db8:85a3:0000:0000:8a2e:0370:7334"

**Detection Patterns:**
```regex
# IPv4
\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b

# IPv6 (simplified)
\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b
```

**Classification:** PII - network identifier

---

### 16. Biometric Identifiers
**Description:** Fingerprints, retinal/iris scans, voiceprints, DNA.

**Examples:**
- "Fingerprint ID: FP-12345"
- "Biometric template stored"
- DNA sequences or identifiers

**Detection Patterns:**
```regex
# Biometric references
\b(Fingerprint|Retinal|Iris|Voice\s*print|DNA|Biometric)\s*(ID|Scan|Template|Sample)\b

# Genetic markers
\b[ACGT]{10,}\b
```

**Classification:** PHI - biometric data

**Risk Level:** CRITICAL - immutable identifier

---

### 17. Full-Face Photographs
**Description:** Full-face photographic images and comparable images.

**Examples:**
- Patient photos
- ID badges with photos
- Medical imaging showing face

**Detection Notes:**
- Cannot detect via regex
- Requires image analysis/OCR
- Look for image file references in healthcare contexts

**Classification:** PHI - visual identifier

---

### 18. Any Other Unique Identifying Number
**Description:** Any other unique identifying number, characteristic, or code.

**Examples:**
- Unique study IDs
- Research subject numbers
- Custom facility identifiers
- Barcode/QR code data

**Detection Patterns:**
```regex
# Generic unique identifiers
\b(ID|Identifier|Code|Number)\s*[:#]?\s*[A-Z0-9]{6,15}\b

# UUID format
\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b
```

**Classification:** Context-dependent

---

## Classification Guidelines

### PHI (Protected Health Information)
Information that:
1. Relates to health condition, treatment, or payment
2. Identifies or could identify an individual
3. Is held by a covered entity or business associate

### PII (Personally Identifiable Information)
Information that can identify an individual but is not necessarily health-related.

### Sensitive Non-PHI
Information that is sensitive but cannot identify an individual (e.g., aggregate statistics, de-identified data).

## Combination Risk

**IMPORTANT:** Risk increases significantly when multiple identifiers appear together:
- Single identifier: Moderate risk
- Two identifiers: High risk
- Three or more identifiers: Critical risk

Example combinations requiring immediate attention:
- Name + DOB
- Name + SSN
- MRN + any other identifier
- Address + any medical information

## De-identification Requirements

To achieve Safe Harbor de-identification:
1. Remove or generalize all 18 identifiers
2. Have no actual knowledge that remaining info could identify individual
3. Document the de-identification process
