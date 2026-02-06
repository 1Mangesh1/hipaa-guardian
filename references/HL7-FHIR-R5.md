# HL7 FHIR R5 Healthcare Data Standards

## What is HL7 FHIR?

**HL7 FHIR** = Fast Healthcare Interoperability Resources

An open standard for exchanging healthcare data between systems using modern web technologies (RESTful APIs, JSON/XML).

- **R5** = Release 5 (latest, current as of 2024)
- **Interoperability**: Systems can exchange data without custom integrations
- **Modular**: "Resources" = reusable data building blocks
- **REST-first**: API-native, works with modern architectures

---

## FHIR Resources (simplified)

### Patient Resource
```json
{
  "resourceType": "Patient",
  "id": "patient-123",
  "identifier": [{
    "system": "http://hospital.example/mrn",
    "value": "[REDACTED_MRN]"
  }],
  "name": [{
    "family": "[REDACTED_NAME]",
    "given": ["[REDACTED]"]
  }],
  "telecom": [{
    "system": "phone",
    "value": "[REDACTED_PHONE]"
  }],
  "birthDate": "[REDACTED_DOB]",
  "gender": "female",
  "address": [{
    "city": "[REDACTED]",
    "state": "[REDACTED]"
  }]
}
```

**PHI Elements**: 
- ✅ identifier (MRN)
- ✅ name
- ✅ telecom (phone, email)
- ✅ birthDate
- ✅ address

**hipaa-guardian detects**: All 6 PHI elements in Patient resource

---

### Observation Resource (Lab Results)
```json
{
  "resourceType": "Observation",
  "id": "obs-456",
  "status": "final",
  "subject": {
    "reference": "Patient/patient-123"
  },
  "performer": [{
    "reference": "Practitioner/pract-789"
  }],
  "effectiveDateTime": "2026-02-07",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "2345-7",
      "display": "Glucose [Mass/Volume] in Serum or Plasma"
    }]
  },
  "value": {
    "Quantity": {
      "value": 118,
      "unit": "mg/dL"
    }
  }
}
```

**PHI Elements**: 
- ✅ subject (patient reference)
- ✅ performer (practitioner identity)
- ✅ effectiveDateTime (service date)

---

### MedicationRequest Resource (Prescriptions)
```json
{
  "resourceType": "MedicationRequest",
  "id": "medreq-012",
  "status": "active",
  "intent": "order",
  "subject": {
    "reference": "Patient/patient-123"
  },
  "authoredOn": "2026-02-07",
  "requester": {
    "reference": "Practitioner/pract-789"
  },
  "medicationReference": {
    "reference": "Medication/med-xyz"
  },
  "dosageInstruction": [{
    "text": "Take one tablet by mouth three times daily"
  }]
}
```

**PHI Elements**:
- ✅ subject (identifies patient)
- ✅ authoredOn (date of prescription)
- ✅ requester (provider identity)
- ⚠️ medicationReference (sensitive medication info)

**Sensitive Medications Requiring Extra Protection**:
- HIV/AIDS medications
- Psychiatric medications
- Substance abuse treatments
- Reproductive health medications

---

## CDA (Clinical Document Architecture)

**CDA** = XML-based clinical document format for electronic records (CCDs, C-CDAs).

Example CDA snippet:
```xml
<ClinicalDocument xmlns="urn:hl7-org:v3">
  <recordTarget>
    <patientRole>
      <id root="2.16.840.1.113883.3.933" extension="3141592654"/>
      <patient>
        <name>[REDACTED_NAME]</name>
        <birthTime value="19800115"/>
      </patient>
    </patientRole>
  </recordTarget>
  <author>
    <assignedAuthor>
      <assignedPerson>
        <name>[REDACTED_PROVIDER_NAME]</name>
      </assignedPerson>
    </assignedAuthor>
  </author>
</ClinicalDocument>
```

**PHI Elements**:
- ✅ id (patient identifier)
- ✅ name
- ✅ birthTime (date of birth)
- ✅ assignedPerson/name (provider name)

---

## HL7 v2 Messages (Legacy EDI)

**HL7 v2** = Pipe-delimited text format (older systems, still widely used).

Example segment:
```
PID|1||123456^^^MRN||SMITH^JOHN||19800115|M|||123 MAIN ST^^BOSTON^MA^02115||555-1234
OBX|1|NM|2345-7^^LN||118|mg/dL|70-100|N|||F
RXO|^DOXYCYCLINE^100MG|1|PO|QID^^^for 10 days
```

**Segments** (line prefixes):
- **PID** = Patient demographics (name, DOB, address, phone)
- **OBX** = Observation/lab results
- **RXO** = Medication order
- **ORC** = Order (generic)

**PHI Detection**: 
- ^SMITH^JOHN^ = name
- 19800115 = DOB
- 123 MAIN ST = address
- 555-1234 = phone

---

## X12 EDI (Insurance Claims)

**X12** = HIPAA standard for electronic claims submission.

Example EDI:
```
NM1*IL*1*SMITH*JOHN*M***MI*123456789
NM1*PR*2*HEALTH PLAN CO*****PI*987654321
CLM*12345*750*11*B*12*B*N*01*A*1
SVC*HC*99213*0*60***1*0*0*11
```

**Segments**:
- **NM1** = Names (patient, provider, payer)
- **CLM** = Claim header (amount charged, dates)
- **SVC** = Service lines (codes, amounts)

**PHI**: Member ID, diagnosis codes (ICD-10), provider NPI

---

## FHIR Validation Against HIPAA

**hipaa-guardian FHIR validation**:

✅ **Checks**:
1. All required PHI elements present? (completeness)
2. Identifiers in correct format? (MRN pattern, DOB valid)
3. Are sensitive medications protected? (extra access controls)
4. Dates sanitized properly? (year removed if de-identified)
5. References resolve correctly? (Patient -> Observation links)

❌ **Violations flagged**:
- Patient resource without identifier (can't identify subject)
- Full DOB in de-identified dataset (safe harbor violation)
- Unencrypted FHIR export (transmission security)
- Missing audit reference (who created/modified)

---

## FHIR Bundles & Collections

**Bundle** = Container for multiple FHIR resources (represents a transaction).

```json
{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": { "resourceType": "Patient", ... },
      "request": { "method": "POST", "url": "Patient" }
    },
    {
      "resource": { "resourceType": "Observation", ... },
      "request": { "method": "POST", "url": "Observation" }
    }
  ]
}
```

**hipaa-guardian Bundle analysis**:
- Count total PHI elements across all resources
- Detect if bundle contains sensitive combinations (e.g., HIV+ patient + psychiatric meds)
- Verify all identifiable data is encrypted if transmitted

---

## Compliance Mappings

| Standard | hipaa-guardian Support |
|---|---|
| **FHIR R5** | ✅ Full schema validation |
| **CDA / C-CDA** | ✅ XML parsing, identifier extraction |
| **HL7 v2** | ✅ Segment parsing, field extraction |
| **X12 EDI** | ✅ Claim element detection |
| **Direct Secure Mail** | ✅ Message encryption validation |
|  **SFTP File Transfer** | ✅ Transmission security check |

---

**Last Updated**: February 2026  
**FHIR Version**: R5  
**HL7 Versions Supported**: v2, CDA, FHIR R4/R5
