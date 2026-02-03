# Healthcare Data Format Detection Patterns

Detection patterns for FHIR, HL7, and other healthcare data formats that commonly contain PHI.

---

## FHIR (Fast Healthcare Interoperability Resources)

FHIR is the modern standard for healthcare data exchange. FHIR resources frequently contain PHI.

### High-Risk FHIR Resources

```python
FHIR_PHI_RESOURCES = [
    'Patient',           # Demographics, identifiers
    'Person',            # Personal information
    'RelatedPerson',     # Family/contacts
    'Practitioner',      # Provider info
    'Condition',         # Diagnoses
    'Observation',       # Lab results, vitals
    'DiagnosticReport',  # Test results
    'MedicationRequest', # Prescriptions
    'MedicationStatement', # Medication history
    'AllergyIntolerance', # Allergies
    'Immunization',      # Vaccination records
    'Procedure',         # Surgical/medical procedures
    'Encounter',         # Visit information
    'Claim',             # Billing with diagnosis
    'ExplanationOfBenefit', # Insurance claims
    'Coverage',          # Insurance info
    'DocumentReference', # Clinical documents
]
```

### FHIR Detection Patterns

```python
FHIR_PATTERNS = {
    # Resource type detection
    'resource_type': [
        r'"resourceType"\s*:\s*"(Patient|Person|Condition|Observation|MedicationRequest)"',
        r'<resourceType value="(Patient|Condition|Observation)"/>',
    ],

    # Patient identifiers
    'patient_identifier': [
        r'"identifier"\s*:\s*\[\s*\{[^}]*"system"\s*:\s*"[^"]*ssn[^"]*"',
        r'"identifier"\s*:\s*\[\s*\{[^}]*"system"\s*:\s*"[^"]*mrn[^"]*"',
        r'"identifier"\s*:\s*\[\s*\{[^}]*"system"\s*:\s*"http://hl7\.org/fhir/sid/us-ssn"',
    ],

    # Name fields
    'patient_name': [
        r'"name"\s*:\s*\[\s*\{[^}]*"family"\s*:\s*"[^"]+"',
        r'"name"\s*:\s*\[\s*\{[^}]*"given"\s*:\s*\["[^"]+"\]',
    ],

    # Contact information
    'contact_info': [
        r'"telecom"\s*:\s*\[\s*\{[^}]*"value"\s*:\s*"[^"]+"',
        r'"address"\s*:\s*\[\s*\{[^}]*"line"\s*:\s*\["[^"]+"\]',
    ],

    # Date of Birth
    'birth_date': [
        r'"birthDate"\s*:\s*"\d{4}-\d{2}-\d{2}"',
    ],

    # Medical data
    'diagnosis': [
        r'"code"\s*:\s*\{[^}]*"coding"\s*:\s*\[[^]]*"system"\s*:\s*"http://snomed\.info/sct"',
        r'"code"\s*:\s*\{[^}]*"coding"\s*:\s*\[[^]]*"system"\s*:\s*"http://hl7\.org/fhir/sid/icd-10"',
    ],

    # Reference to patient
    'patient_reference': [
        r'"subject"\s*:\s*\{\s*"reference"\s*:\s*"Patient/[^"]+"',
        r'"patient"\s*:\s*\{\s*"reference"\s*:\s*"Patient/[^"]+"',
    ],
}
```

### FHIR File Detection

```python
FHIR_FILE_PATTERNS = [
    r'\.fhir\.json$',
    r'\.fhir\.xml$',
    r'fhir[-_]?bundle',
    r'fhir[-_]?resource',
]

# Bundle detection
FHIR_BUNDLE_PATTERN = r'"resourceType"\s*:\s*"Bundle"[^}]*"entry"\s*:\s*\['
```

---

## HL7 v2.x (Legacy Healthcare Messages)

HL7 v2 uses pipe-delimited segments and is still widely used in healthcare IT.

### HL7 v2 Segment Types with PHI

```python
HL7_PHI_SEGMENTS = {
    'PID': 'Patient Identification',      # SSN, DOB, Name, Address
    'NK1': 'Next of Kin',                 # Emergency contacts
    'PV1': 'Patient Visit',               # Visit info, attending physician
    'DG1': 'Diagnosis',                   # Diagnosis codes
    'OBX': 'Observation/Result',          # Lab results
    'OBR': 'Observation Request',         # Test orders
    'RXA': 'Pharmacy Administration',     # Medication given
    'RXE': 'Pharmacy Encoded Order',      # Medication orders
    'IN1': 'Insurance',                   # Insurance info
    'GT1': 'Guarantor',                   # Billing/guarantor info
    'AL1': 'Allergy',                     # Allergy information
    'PRB': 'Problem',                     # Problem list
}
```

### HL7 v2 Detection Patterns

```python
HL7_V2_PATTERNS = {
    # Message header
    'msh_segment': r'^MSH\|',

    # Patient Identification segment
    'pid_segment': r'^PID\|([^|]*\|){2}([^|]+)\|',  # PID-3: Patient ID
    'pid_ssn': r'^PID\|([^|]*\|){18}(\d{3}-\d{2}-\d{4})',  # PID-19: SSN
    'pid_name': r'^PID\|([^|]*\|){4}([^^]+)',  # PID-5: Patient Name
    'pid_dob': r'^PID\|([^|]*\|){6}(\d{8})',  # PID-7: DOB

    # Diagnosis
    'dg1_segment': r'^DG1\|([^|]*\|){2}([^|]+)',  # DG1-3: Diagnosis Code

    # Results
    'obx_segment': r'^OBX\|([^|]*\|){4}([^|]+)',  # OBX-5: Observation Value

    # Insurance
    'in1_segment': r'^IN1\|([^|]*\|){1}([^|]+)',  # IN1-2: Insurance Plan ID
}

# Full HL7 message detection
HL7_MESSAGE_PATTERN = r'^MSH\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|(ADT|ORU|ORM|RDE|SIU)'
```

### HL7 Field Positions for PHI

```python
HL7_PHI_FIELDS = {
    'PID': {
        3: ('patient_id', 'MRN/Patient Identifier'),
        5: ('patient_name', 'Patient Name'),
        7: ('dob', 'Date of Birth'),
        8: ('sex', 'Administrative Sex'),
        11: ('address', 'Patient Address'),
        13: ('phone_home', 'Home Phone'),
        14: ('phone_work', 'Work Phone'),
        19: ('ssn', 'Social Security Number'),
    },
    'NK1': {
        2: ('nok_name', 'Next of Kin Name'),
        4: ('nok_address', 'NOK Address'),
        5: ('nok_phone', 'NOK Phone'),
    },
    'IN1': {
        2: ('insurance_id', 'Insurance Plan ID'),
        3: ('insurance_company', 'Insurance Company ID'),
        16: ('insured_name', 'Insured Name'),
        19: ('group_number', 'Group Number'),
    },
}
```

---

## CDA (Clinical Document Architecture)

CDA is an XML-based standard for clinical documents.

### CDA Detection Patterns

```python
CDA_PATTERNS = {
    # Document type
    'cda_document': r'<ClinicalDocument[^>]*xmlns="urn:hl7-org:v3"',

    # Patient role
    'patient_role': r'<patientRole>',

    # Patient identifiers
    'patient_id': r'<id[^>]*root="[^"]*"[^>]*extension="([^"]+)"',

    # Patient name
    'patient_name': r'<patient>.*?<name>.*?<given>([^<]+)</given>.*?<family>([^<]+)</family>',

    # Birth time
    'birth_time': r'<birthTime[^>]*value="(\d{8})"',

    # Address
    'address': r'<addr>.*?<streetAddressLine>([^<]+)</streetAddressLine>',

    # SSN (in id element)
    'ssn_id': r'<id[^>]*root="2\.16\.840\.1\.113883\.4\.1"[^>]*extension="(\d{3}-\d{2}-\d{4})"',
}
```

---

## X12 (EDI Healthcare Transactions)

X12 is used for healthcare billing and eligibility.

### X12 Transaction Types with PHI

```python
X12_PHI_TRANSACTIONS = {
    '270': 'Eligibility Inquiry',
    '271': 'Eligibility Response',
    '276': 'Claim Status Inquiry',
    '277': 'Claim Status Response',
    '278': 'Prior Authorization',
    '834': 'Enrollment',
    '835': 'Payment/Remittance',
    '837': 'Healthcare Claim',
}
```

### X12 Detection Patterns

```python
X12_PATTERNS = {
    # Transaction set header
    'transaction_header': r'ST\*(270|271|276|277|278|834|835|837)',

    # Subscriber/Patient loops
    'subscriber_loop': r'NM1\*(IL|QC)\*',  # Insured/Patient
    'patient_name': r'NM1\*[^*]*\*[^*]*\*([^*]+)\*([^*]*)\*',

    # Identification
    'ssn_qualifier': r'REF\*SY\*(\d{9})',  # SSN reference
    'member_id': r'REF\*(1L|IG)\*([^~]+)',  # Member/Group ID

    # Diagnosis codes
    'diagnosis': r'HI\*(BK|BF):([^:~]+)',

    # Date elements
    'service_date': r'DTP\*(472|096)\*D8\*(\d{8})',
}
```

---

## NCPDP (Pharmacy Transactions)

NCPDP is used for pharmacy claim transactions.

### NCPDP Detection Patterns

```python
NCPDP_PATTERNS = {
    # Header segment
    'header': r'\x02.{2}B1',  # NCPDP version D.0

    # Patient segment
    'patient_name': r'CA([^/]+)',  # Patient Last Name
    'patient_dob': r'C4(\d{8})',   # Patient DOB
    'patient_gender': r'C5([12])', # Patient Gender

    # Prescriber segment
    'prescriber_id': r'DB([A-Z0-9]+)',  # Prescriber ID (NPI/DEA)

    # Drug segment
    'ndc': r'D7(\d{11})',  # NDC code
    'quantity': r'E7(\d+)',  # Quantity dispensed
}
```

---

## File Extension Mapping

```python
HEALTHCARE_FILE_EXTENSIONS = {
    # FHIR
    '.fhir.json': 'FHIR JSON',
    '.fhir.xml': 'FHIR XML',

    # HL7
    '.hl7': 'HL7 v2.x',
    '.hl7v2': 'HL7 v2.x',

    # CDA
    '.cda': 'CDA Document',
    '.ccda': 'C-CDA Document',
    '.ccd': 'Continuity of Care Document',

    # X12
    '.x12': 'X12 EDI',
    '.edi': 'EDI Transaction',
    '.837': 'Healthcare Claim',
    '.835': 'Remittance Advice',

    # General
    '.xml': 'Check for CDA/FHIR',
    '.json': 'Check for FHIR',
}
```

---

## Scanning Recommendations

### High Priority Files

1. Any file with `.hl7`, `.fhir`, `.cda`, `.x12` extensions
2. Files containing `resourceType` (FHIR)
3. Files starting with `MSH|` (HL7 v2)
4. Files containing `ClinicalDocument` (CDA)
5. Files containing `ST*837` or `ST*835` (X12)

### Context-Based Scanning

```python
def detect_healthcare_format(content: str, filename: str) -> str:
    """Detect healthcare data format from content and filename."""

    # Check extension first
    for ext, format_name in HEALTHCARE_FILE_EXTENSIONS.items():
        if filename.lower().endswith(ext):
            return format_name

    # Check content patterns
    if re.search(r'"resourceType"\s*:', content):
        return 'FHIR JSON'
    if re.search(r'^MSH\|', content, re.M):
        return 'HL7 v2.x'
    if re.search(r'<ClinicalDocument', content):
        return 'CDA'
    if re.search(r'^ISA\*|^ST\*(837|835|270|271)', content, re.M):
        return 'X12 EDI'

    return 'Unknown'
```

---

## Risk Scoring for Healthcare Formats

| Format | Base Risk | PHI Density | Typical Severity |
|--------|-----------|-------------|------------------|
| FHIR Patient Resource | 95 | Very High | Critical |
| HL7 ADT Message | 95 | Very High | Critical |
| CDA Document | 90 | High | Critical |
| X12 837 Claim | 85 | High | High |
| FHIR Observation | 75 | Medium | High |
| HL7 ORU Result | 80 | High | High |

---

## HIPAA Mapping for Healthcare Formats

All healthcare format files containing patient data map to:

- **Privacy Rule §164.502**: Uses and disclosures of PHI
- **Privacy Rule §164.514**: De-identification requirements
- **Security Rule §164.312**: Technical safeguards for ePHI
- **Breach Rule §164.402**: Breach notification requirements

Healthcare data files should NEVER be:
- Committed to source control with real data
- Logged to application logs
- Stored without encryption
- Transmitted without TLS
