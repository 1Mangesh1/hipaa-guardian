# PHI Detection Patterns

Comprehensive regex patterns and detection rules for identifying the 18 HIPAA identifiers.

## Pattern Categories

### High Precision Patterns
These patterns have low false positive rates and can be used with high confidence:
- SSN format
- Email addresses
- Phone numbers
- IP addresses
- Credit card numbers

### Context-Dependent Patterns
These patterns require contextual validation:
- Names (need NLP/dictionary validation)
- Dates (common format, need health context)
- Generic numbers (need field/label context)

---

## 1. Social Security Number (SSN)

```python
SSN_PATTERNS = [
    # Standard format: XXX-XX-XXXX
    r'\b\d{3}-\d{2}-\d{4}\b',

    # No dashes: XXXXXXXXX (9 consecutive digits, validate not phone)
    r'\b(?<!\d)\d{9}(?!\d)\b',

    # Spaces: XXX XX XXXX
    r'\b\d{3}\s\d{2}\s\d{4}\b',

    # With label (highest confidence)
    r'(?i)\b(SSN|Social\s*Security(\s*Number)?)\s*[:#]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',

    # Partial/masked: XXX-XX-####
    r'\b[Xx]{3}-[Xx]{2}-\d{4}\b',
]

# Validation rules
SSN_VALIDATION = {
    'area_number': 'First 3 digits not 000, 666, or 900-999',
    'group_number': 'Middle 2 digits not 00',
    'serial_number': 'Last 4 digits not 0000',
}
```

**Confidence Levels:**
- With "SSN" label: 99%
- Standard format (XXX-XX-XXXX): 95%
- 9 digits without context: 60% (validate not phone/zip)

---

## 2. Medical Record Number (MRN)

```python
MRN_PATTERNS = [
    # Explicit MRN label
    r'(?i)\b(MRN|MR#?|Medical\s*Record(\s*Number)?)\s*[:#]?\s*([A-Z]{0,2}\d{5,12})\b',

    # Patient ID variations
    r'(?i)\b(Patient\s*ID|PID|PAT#?|PT#?)\s*[:#]?\s*([A-Z]{0,2}\d{5,12})\b',

    # Encounter/Visit numbers
    r'(?i)\b(Encounter|Visit|Admission)\s*(ID|#|Number)\s*[:#]?\s*([A-Z]{0,2}\d{6,12})\b',

    # Chart numbers
    r'(?i)\b(Chart)\s*(#|Number)\s*[:#]?\s*\d{5,10}\b',
]

# Common MRN prefixes by system
MRN_PREFIXES = ['MR', 'PT', 'PAT', 'ENC', 'A', 'P', 'E']
```

**Confidence Levels:**
- With explicit label: 98%
- With healthcare context: 85%
- Numeric only in medical file: 70%

---

## 3. Dates

```python
DATE_PATTERNS = [
    # MM/DD/YYYY or MM-DD-YYYY
    r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b',

    # DD/MM/YYYY (international)
    r'\b(0?[1-9]|[12]\d|3[01])[-/](0?[1-9]|1[0-2])[-/](19|20)\d{2}\b',

    # YYYY-MM-DD (ISO 8601)
    r'\b(19|20)\d{2}-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])\b',

    # Written month format
    r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+(19|20)\d{2}\b',

    # Abbreviated month
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[.\s]+\d{1,2},?\s+(19|20)\d{2}\b',

    # DOB-specific patterns
    r'(?i)\b(DOB|Date\s*of\s*Birth|Birth\s*Date|Born)\s*[:#]?\s*[\d/\-]+\b',

    # Admission/Discharge dates
    r'(?i)\b(Admit|Admission|Discharge|DOS|Date\s*of\s*Service)\s*(Date)?\s*[:#]?\s*[\d/\-]+\b',
]

# Age detection (over 89 is PHI)
AGE_PATTERNS = [
    r'(?i)\bage[d]?\s*[:#]?\s*(\d{1,3})\b',
    r'\b(9[0-9]|1[0-9]{2})\s*(years?\s*old|y/?o|yo)\b',
]
```

**Context Keywords:**
- DOB, birth, born, birthday
- Admission, discharge, visit
- Death, deceased, expired
- Service date, DOS

---

## 4. Phone Numbers

```python
PHONE_PATTERNS = [
    # (XXX) XXX-XXXX
    r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',

    # XXX-XXX-XXXX
    r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',

    # XXXXXXXXXX (10 digits)
    r'\b(?<![.\d])\d{10}(?![.\d])\b',

    # +1-XXX-XXX-XXXX (US with country code)
    r'\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',

    # With label
    r'(?i)\b(Phone|Tel|Telephone|Mobile|Cell|Contact)\s*[:#]?\s*[\d\s\-().+]{10,}\b',
]

# Fax-specific
FAX_PATTERNS = [
    r'(?i)\b(Fax|Facsimile)\s*[:#]?\s*[\d\s\-().+]{10,}\b',
]
```

---

## 5. Email Addresses

```python
EMAIL_PATTERNS = [
    # Standard email
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',

    # With label
    r'(?i)\b(Email|E-mail)\s*[:#]?\s*[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
]

# Healthcare portal domains (higher risk)
HEALTHCARE_DOMAINS = [
    'mychart', 'myhealth', 'patientportal', 'healthvault',
    'followmyhealth', 'patient', 'careportal'
]
```

---

## 6. Geographic/Address

```python
ADDRESS_PATTERNS = [
    # Street address
    r'\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Drive|Dr\.?|Lane|Ln\.?|Way|Court|Ct\.?|Place|Pl\.?|Circle|Cir\.?|Trail|Tr\.?|Parkway|Pkwy\.?)\b',

    # PO Box
    r'(?i)\b(P\.?\s*O\.?\s*Box|Post\s*Office\s*Box)\s*\d+\b',

    # Apartment/Suite
    r'(?i)\b(Apt\.?|Apartment|Suite|Ste\.?|Unit|#)\s*[A-Z0-9]+\b',
]

# ZIP Code patterns
ZIP_PATTERNS = [
    # 5-digit ZIP
    r'\b\d{5}\b',

    # ZIP+4
    r'\b\d{5}-\d{4}\b',

    # With label
    r'(?i)\b(ZIP|Zip\s*Code|Postal\s*Code)\s*[:#]?\s*\d{5}(-\d{4})?\b',
]

# ZIP codes requiring removal (population < 20,000)
# First 3 digits that must be removed or generalized
RESTRICTED_ZIP_PREFIXES = [
    '036', '059', '063', '102', '203', '556', '692', '790', '821', '823', '830', '831', '878', '879', '884', '893'
]
```

---

## 7. Health Plan Identifiers

```python
HEALTH_PLAN_PATTERNS = [
    # Member/Subscriber ID
    r'(?i)\b(Member|Subscriber|Insurance|Policy)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{6,15}\b',

    # Group number
    r'(?i)\b(Group)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{5,12}\b',

    # Medicare Beneficiary Identifier (MBI)
    r'\b\d[A-Z][A-Z0-9]\d[A-Z][A-Z0-9]\d[A-Z]{2}\d{2}\b',

    # Medicaid ID (varies by state)
    r'(?i)\b(Medicaid)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{8,12}\b',

    # Plan/Payer ID
    r'(?i)\b(Plan|Payer)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{5,10}\b',
]
```

---

## 8. Account/Financial Numbers

```python
ACCOUNT_PATTERNS = [
    # Bank account
    r'(?i)\b(Bank|Checking|Savings|Account)\s*(Account|Acct\.?)?\s*(#|Number)\s*[:#]?\s*\d{8,17}\b',

    # Billing account
    r'(?i)\b(Billing|Invoice)\s*(Account|Acct\.?|#|Number)\s*[:#]?\s*\d{6,12}\b',

    # Routing number
    r'(?i)\b(Routing|ABA)\s*(#|Number)\s*[:#]?\s*\d{9}\b',
]

# Credit card patterns
CREDIT_CARD_PATTERNS = [
    # Visa
    r'\b4[0-9]{12}(?:[0-9]{3})?\b',

    # Mastercard
    r'\b5[1-5][0-9]{14}\b',

    # American Express
    r'\b3[47][0-9]{13}\b',

    # Discover
    r'\b6(?:011|5[0-9]{2})[0-9]{12}\b',

    # Generic (with dashes/spaces)
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
]

# Luhn algorithm validation function
def validate_luhn(number):
    """Validate credit card number using Luhn algorithm."""
    digits = [int(d) for d in str(number) if d.isdigit()]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d * 2, 10))
    return checksum % 10 == 0
```

---

## 9. License/Certificate Numbers

```python
LICENSE_PATTERNS = [
    # Driver's license
    r"(?i)\b(Driver'?s?\s*License|DL|DLN)\s*[:#]?\s*[A-Z0-9]{5,15}\b",

    # DEA number
    r'\b[A-Z]{2}\d{7}\b',
    r'(?i)\b(DEA)\s*[:#]?\s*[A-Z]{2}\d{7}\b',

    # NPI (National Provider Identifier)
    r'\b\d{10}\b',  # Context: must be labeled or in provider context
    r'(?i)\b(NPI)\s*[:#]?\s*\d{10}\b',

    # Professional licenses
    r'(?i)\b(License|Lic\.?|Certification|Cert\.?)\s*(#|Number|No\.?)\s*[:#]?\s*[A-Z0-9]{5,15}\b',

    # State medical license
    r'(?i)\b(Medical|Nursing|Pharmacy|RN|MD|DO)\s*(License|Lic\.?)\s*[:#]?\s*[A-Z0-9]{5,12}\b',
]
```

---

## 10. Device/Vehicle Identifiers

```python
DEVICE_PATTERNS = [
    # Serial number
    r'(?i)\b(Serial|SN|S/N)\s*[:#]?\s*[A-Z0-9]{6,20}\b',

    # UDI (Unique Device Identifier)
    r'\(\d{2}\)\d{14}',
    r'(?i)\b(UDI)\s*[:#]?\s*.+\b',

    # MAC address
    r'\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b',

    # IMEI
    r'\b\d{15}\b',
    r'(?i)\b(IMEI)\s*[:#]?\s*\d{15}\b',
]

VEHICLE_PATTERNS = [
    # VIN (17 characters, excludes I, O, Q)
    r'\b[A-HJ-NPR-Z0-9]{17}\b',
    r'(?i)\b(VIN|Vehicle\s*ID)\s*[:#]?\s*[A-HJ-NPR-Z0-9]{17}\b',

    # License plate (generic US format)
    r'\b[A-Z0-9]{1,4}[-\s]?[A-Z0-9]{2,4}\b',
]
```

---

## 11. Network Identifiers

```python
IP_PATTERNS = [
    # IPv4
    r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',

    # IPv6 (full)
    r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b',

    # IPv6 (compressed)
    r'\b(?:[A-Fa-f0-9]{1,4}:)*:(?:[A-Fa-f0-9]{1,4}:)*[A-Fa-f0-9]{1,4}\b',
]

URL_PATTERNS = [
    # HTTP/HTTPS URLs
    r'\bhttps?://[A-Za-z0-9.-]+(?:/[A-Za-z0-9./_~:?#\[\]@!$&\'()*+,;=-]*)?\b',

    # URLs with potential PHI in path
    r'\bhttps?://[A-Za-z0-9.-]+/(?:patient|member|user|account)/[A-Za-z0-9]+\b',
]
```

---

## 12. Biometric/Genetic

```python
BIOMETRIC_PATTERNS = [
    # Biometric identifiers
    r'(?i)\b(Fingerprint|Retinal|Iris|Voice\s*print|Facial|Biometric)\s*(ID|Scan|Template|Data|Sample)\b',

    # DNA sequences
    r'\b[ACGT]{20,}\b',

    # Genetic markers
    r'(?i)\b(DNA|Genetic|Genomic)\s*(ID|Sample|Sequence|Marker)\b',
]
```

---

## 13. Names (Context-Required)

```python
NAME_PATTERNS = [
    # Title + Name
    r'\b(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)?\b',

    # Patient name label
    r'(?i)\b(Patient|Pt\.?|Member|Subscriber)\s*(Name)?\s*[:#]?\s*[A-Z][a-z]+(\s+[A-Z]\.?\s*)?[A-Z][a-z]+\b',

    # Provider name label
    r'(?i)\b(Provider|Physician|Doctor|Dr\.?|Attending|Referring)\s*(Name)?\s*[:#]?\s*[A-Z][a-z]+(\s+[A-Z]\.?\s*)?[A-Z][a-z]+\b',
]

# Name validation using context
NAME_CONTEXT_KEYWORDS = [
    'patient', 'member', 'subscriber', 'beneficiary',
    'provider', 'physician', 'doctor', 'nurse',
    'name', 'contact', 'emergency', 'next of kin',
    'mother', 'father', 'spouse', 'guardian'
]
```

---

## Confidence Scoring

```python
def calculate_confidence(pattern_type, context_matches, label_present):
    """
    Calculate confidence score for a detection.

    Returns value between 0.0 and 1.0
    """
    base_scores = {
        'ssn': 0.95,
        'email': 0.95,
        'phone': 0.90,
        'credit_card': 0.95,
        'ip_address': 0.90,
        'mrn': 0.85,
        'date': 0.70,
        'name': 0.60,
        'address': 0.75,
        'generic_id': 0.50,
    }

    score = base_scores.get(pattern_type, 0.50)

    # Boost for explicit label
    if label_present:
        score = min(0.99, score + 0.15)

    # Boost for healthcare context
    if context_matches > 0:
        score = min(0.99, score + (0.05 * context_matches))

    return score
```

---

## Context Keywords

Healthcare context terms that increase PHI likelihood:

```python
HEALTHCARE_CONTEXT = [
    # Medical terms
    'patient', 'diagnosis', 'treatment', 'medication', 'prescription',
    'admission', 'discharge', 'visit', 'appointment', 'referral',

    # Facility terms
    'hospital', 'clinic', 'medical center', 'healthcare', 'provider',
    'physician', 'doctor', 'nurse', 'pharmacy',

    # Record terms
    'medical record', 'chart', 'history', 'notes', 'report',
    'lab', 'radiology', 'imaging', 'results',

    # Insurance terms
    'insurance', 'coverage', 'claim', 'billing', 'copay',
    'deductible', 'authorization', 'pre-auth',

    # HIPAA terms
    'PHI', 'protected health information', 'confidential',
    'HIPAA', 'privacy', 'consent', 'authorization',
]
```

---

## False Positive Reduction

### Exclusion Patterns

```python
# Known non-PHI patterns to exclude
EXCLUSIONS = {
    'phone': [
        r'555-\d{4}',  # Fictional phone numbers
        r'1-800-',     # Toll-free (usually business)
        r'1-888-',
        r'1-877-',
    ],
    'ssn': [
        r'000-\d{2}-\d{4}',  # Invalid area
        r'666-\d{2}-\d{4}',  # Invalid area
        r'9\d{2}-\d{2}-\d{4}', # Invalid area (900-999)
        r'\d{3}-00-\d{4}',  # Invalid group
        r'\d{3}-\d{2}-0000', # Invalid serial
    ],
    'date': [
        r'version',    # Version numbers
        r'v\d+\.\d+',
        r'release',
        r'build',
    ],
    'email': [
        r'example\.com$',
        r'test\.com$',
        r'localhost$',
        r'noreply@',
        r'no-reply@',
    ],
}
```

### Validation Functions

```python
def validate_ssn(ssn):
    """Validate SSN is structurally valid."""
    digits = re.sub(r'\D', '', ssn)
    if len(digits) != 9:
        return False
    area = int(digits[:3])
    group = int(digits[3:5])
    serial = int(digits[5:])

    # Invalid areas
    if area == 0 or area == 666 or area >= 900:
        return False
    # Invalid group
    if group == 0:
        return False
    # Invalid serial
    if serial == 0:
        return False
    return True

def validate_phone(phone):
    """Validate phone number is not obviously fake."""
    digits = re.sub(r'\D', '', phone)
    # Exclude 555 exchange (fictional)
    if len(digits) >= 10 and digits[3:6] == '555':
        return False
    return True
```
