# Audit Trail Implementation Standards (§164.312(b))

## Regulatory Requirement

**45 CFR §164.312(b) Audit Controls**:
> "Implement hardware, software, and/or procedural mechanisms that record and examine activity in information systems containing or using ePHI."

Simply: **Log all PHI access and changes**

---

## Mandatory Log Fields

Per HIPAA, each audit entry MUST include:

1. **User Identification**: Who accessed the data
   - User ID/username
   - Role/title (optional but recommended)
   - Authentication method used
   
2. **Date & Time**: When accessed
   - ISO 8601 format (RFC 3339): `2026-02-07T14:30:00.123Z`
   - Must use synchronized server time (NTP)
   - Timezone: UTC preferred
   
3. **Action**: What was done
   - CREATE, READ, UPDATE, DELETE, EXPORT, LOGIN, LOGOUT
   - SCAN (PHI detection), DECRYPT, ENCRYPT, PRINT
   
4. **Object**: What was accessed
   - Patient ID / MRN
   - Resource type (medical record, lab result, medication)
   - Data classification (PHI, ePHI, sensitive)
   
5. **Result**: If successful/failed
   - SUCCESS, FAILURE, PARTIAL
   - Error code / exception (if failed)
   
6. **Source**: Where from
   - IP address
   - hostname / workstation name
   - System identifier (if automated)

---

## hipaa-guardian Audit Log Format (JSON)

```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2026-02-07T14:30:00.123Z",
  "user_id": "user@hospital.org",
  "user_role": "clinician",
  "ip_address": "192.168.1.100",
  "action": "PHI_SCAN",
  "object": {
    "id": "patient-12345",
    "type": "MedicalRecord",
    "data_classification": "PHI"
  },
  "result": "SUCCESS",
  "details": {
    "phi_detected": [
      "name",
      "dob",
      "mrn",
      "contact_number"
    ],
    "phi_count": 4,
    "severity": "HIGH",
    "compliance": "NON_COMPLIANT_IDENTIFIABLE"
  },
  "previous_entry_hash": "sha256:abcdef123456...",
  "current_entry_hash": "sha256:fedcba654321...",
  "immutable": true,
  "retention_until": "2035-02-07"
}
```

---

## Audit Entry Types

### 1. LOGIN/LOGOUT
```json
{
  "action": "LOGIN",
  "timestamp": "2026-02-07T08:30:00Z",
  "user_id": "alice@hospital.org",
  "ip_address": "203.0.113.45",
  "result": "SUCCESS",
  "auth_method": "MFA_FIDO2"
}
```

**Capture**: Every login attempt (success & failure)

---

### 2. PHI_ACCESS (READ)
```json
{
  "action": "READ",
  "timestamp": "2026-02-07T09:15:00Z",
  "user_id": "bob@hospital.org",
  "object": {
    "id": "patient-99999",
    "type": "LabResult",
    "sections": ["glucose", "creatinine"]
  },
  "result": "SUCCESS",
  "access_reason": "Treatment",
  "duration_seconds": 45
}
```

**Capture**: Every PHI access for treatment, payment, healthcare operation

---

### 3. PHI_MODIFICATION (CREATE/UPDATE/DELETE)
```json
{
  "action": "UPDATE",
  "timestamp": "2026-02-07T10:00:00Z",
  "user_id": "carol@hospital.org",
  "object": {
    "id": "patient-88888",
    "type": "MedicationList",
    "fields_changed": [
      {
        "field": "medications",
        "old_value": "[REDACTED_HASH]",
        "new_value": "[REDACTED_HASH]"
      }
    ]
  },
  "result": "SUCCESS",
  "change_reason": "Medication reconciliation",
  "approver": "davd@hospital.org"
}
```

**Capture**: 
- Who made the change
- When (timestamp)
- What field was changed (can use hash for values)
- Why (change reason)
- Who approved it (if required)

**DO NOT LOG**: Actual sensitive values (use hash instead)

---

### 4. PHI_EXPORT
```json
{
  "action": "EXPORT",
  "timestamp": "2026-02-07T11:30:00Z",
  "user_id": "eve@hospital.org",
  "object": {
    "count": 250,
    "type": "Patient",
    "format": "CSV",
    "destination": "RESEARCHER_SYSTEM"
  },
  "result": "SUCCESS",
  "approvals": [
    "irb@research.org"
  ],
  "encryption": "AES-256-GCM"
}
```

**Capture**: 
- What was exported (count, type, format)
- Where to (system, researcher, analysis platform)
- Who approved it
- How many records (volume audit)
- Encryption applied

---

### 5. AUTHENTICATION_FAILURE
```json
{
  "action": "LOGIN_FAILED",
  "timestamp": "2026-02-07T12:00:00Z",
  "user_id": "unknown",
  "ip_address": "198.51.100.1",
  "reason": "INVALID_PASSWORD",
  "failed_attempts_remaining": 2,
  "result": "FAILURE"
}
```

**Capture**: Failed login attempts (possible breach indicator)

**Alert Threshold**: 5 failed attempts → auto-lockout 30 min

---

### 6. BREACH_DETECTION
```json
{
  "action": "BREACH_DETECT",
  "timestamp": "2026-02-07T13:00:00Z",
  "severity": "CRITICAL",
  "alert_type": "UNAUTHORIZED_ACCESS",
  "details": {
    "anomaly": "User accessing 10,000 records (normal: 50/day)",
    "user_id": "frank@hospital.org",
    "actions_taken": [
      "ACCOUNT_DISABLED",
      "SESSION_TERMINATED",
      "INCIDENT_TICKET_CREATED"
    ]
  },
  "incident_number": "INC-2026-001234"
}
```

---

### 7. COMPLIANCE_CHECK
```json
{
  "action": "COMPLIANCE_CHECK",
  "timestamp": "2026-02-07T14:00:00Z",
  "checker_id": "audit@hospital.org",
  "scope": "MONTHLY_AUDIT",
  "findings": {
    "total_accesses": 15234,
    "unauthorized_attempts": 2,
    "missing_logs": 0,
    "audit_integrity": "VALID"
  },
  "result": "PASS"
}
```

---

## Audit Log Integrity Protection

### Cryptographic Hashing Chain

Each log entry contains:
- **previous_entry_hash**: SHA-256 hash of previous complete entry
- **current_entry_hash**: SHA-256 hash of current entry

```
Entry 1: hash_previous="null", hash_current="abc123"
Entry 2: hash_previous="abc123", hash_current="def456"
Entry 3: hash_previous="def456", hash_current="ghi789"
```

**Tamper Detection**: If Entry 2 is modified:
- Its hash_current changes from "def456" → "xyz999"
- Entry 3's hash_previous still points to "def456"
- Mismatch detected → TAMPERING ALERT

---

## Retention Requirements

**HIPAA Standard**: Minimum 6 years

**hipaa-guardian Retention**:
- Critical events (breaches): 10 years
- Login logs: 3 years  minimum
- PHI access logs: 6 years minimum
- Deletion logs: 6 years minimum
- Compliance checks: 10 years (legal hold)

**Deletion Date Calculation**: 
```
log_date + 6 years = retention_until
2026-02-07 + 6 years = 2032-02-07 (auto-delete after this date)
```

---

## Access Controls for Audit Logs

**WHO can access audit logs?**
- ✅ **Auditor role** (designated security officer)
- ✅ **Compliance team** (HIPAA oversight)
- ✅ **Legal team** (breach investigations only)
- ❌ **Regular clinicians** (no audit access)
- ❌ **System administrators** (no backdoor access)

**WHAT can they do?**
- ✅ READ / Query logs
- ✅ EXPORT for compliance report
- ✅ Generate audit trail (SELECT)
- ❌ UPDATE / MODIFY (immutable)
- ❌ DELETE (except after retention period)

---

## Audit Log Monitoring & Alerts

### Automated Alerts

**Real-time monitoring triggers**:

| Alert | Threshold | Action |
|---|---|---|
| Failed logins | 5 attempts | Lock account, alert admin |
| Unusual access pattern | 10x normal volume | Notify supervisor, flag activity |
| After-hours access | Non-business hours | Alert on-call security |
| Unauthorized deletion | Any delete attempt by non-admin | Escalate to CISO |
| Breach keywords | "steal", "virus", "ransom" | Incident response activation |
| Encryption key access | Any key usage | Log & monitor |

---

## Reporting & Compliance

### Monthly Audit Report

```yaml
Report Period: 2026-01-01 to 2026-01-31
Generated: 2026-02-01
Reported By: audit@hospital.org

Summary:
  Total Access Events: 45,234
  Unique Users: 234
  Unique Patients: 15,234
  
Activity by Type:
  LOGIN: 5,234
  READ_PHI: 32,123
  UPDATE_PHI: 6,234
  EXPORT: 89
  DELETE: 12
  
Security Events:
  Failed Logins: 23
  Unauthorized Access Attempts: 0
  Potential Breaches Detected: 0
  
Compliance Status: ✅ COMPLIANT
  Audit Integrity: ✅ VALID (no tampering detected)
  Missing Logs: 0
  Retention: ✅ All logs retained per policy
```

### Annual Compliance Certification

```
ATTESTATION OF HIPAA SECURITY COMPLIANCE

[Organization Name] certifies that:

✓ All access to PHI is logged per §164.312(b)
✓ Audit logs are protected from unauthorized modification
✓ Logs are retained for minimum 6 years
✓ No unauthorized access detected during reporting period
✓ Breach notification procedures are in place
✓ Annual evaluation completed

Signed by: [CISO/Compliance Officer]
Date: February 7, 2026
```

---

## hipaa-guardian Audit Automation

**hipaa-guardian features**:
- ✅ Auto-generate audit entries for all PHI scans
- ✅ Immutability validation (hash chain integrity)
- ✅ Retention policy enforcement (auto-deletion)
- ✅ Monthly compliance report generation
- ✅ Breach detection scoring & escalation
- ✅ Encryption validation for log storage

---

**Last Updated**: February 2026  
**Audit Standards Version**: HIPAA 2024-Compliant  
**Next Compliance Review**: February 2027
