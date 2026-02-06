# Security Architecture & Data Handling

## Design Principles

HIPAA Guardian is built on three core security principles:

1. **Zero Trust**: No data is assumed safe; all flows are validated
2. **Privacy by Design**: PHI minimization and data reduction at every step
3. **Audit Everything**: All PHI access is logged and traceable

---

## Technical Safeguards Implementation

### Encryption (§164.312(a)(2))

#### Data at Rest
- **Algorithm**: AES-256-GCM (authenticated encryption)
- **Key Management**: NIST SP 800-57 recommendations
- **Key Rotation**: Annual minimum, more frequent for high-risk data
- **Storage**: Hardware security modules (HSM) or equivalent
- **Deletion**: Cryptographic erasure (immediate key deletion)

**Configuration**:
```yaml
encryption:
  algorithm: "AES-256-GCM"
  key_size_bits: 256
  key_derivation_function: "PBKDF2-SHA-256"
  iterations: 100000
  iv_length: 12  # bytes
  auth_tag_length: 16  # bytes
```

#### Data in Transit
- **Protocol**: TLS 1.3 minimum (RFC 8446)
- **Cipher Suites**: ECDHE with AES-256-GCM (forward secrecy)
- **Certificate Pinning**: For critical connections
- **HSTS**: Enforce HTTPS-only connections
- **Perfect Forward Secrecy**: Required

**Configuration**:
```yaml
tls:
  minimum_version: "1.3"
  preferred_ciphers:
    - "TLS_AES_256_GCM_SHA384"
  certificate_validation: "strict"
  hsts_max_age: 31536000  # 1 year
```

### Authentication & Access Control (§164.312(a)(1))

#### User Authentication
- **Multi-Factor Authentication (MFA)**: Required for PHI access
  - Something you know (password, passphrase)
  - Something you have (hardware token, FIDO2 key)
  - Something you are (biometric - optional)

- **Password Requirements**:
  - Minimum 12 characters
  - Complexity: uppercase, lowercase, numbers, special characters
  - Change frequency: Annual minimum
  - Reuse prevention: Last 12 passwords cannot be reused
  - Lockout: After 5 failed attempts, 30-minute lockout

- **Session Management**:
  - Session timeout: 15 minutes of inactivity
  - Absolute timeout: 8 hours maximum
  - Concurrent session limit: 1 per user (configurable)
  - Session fixation protection

#### Role-Based Access Control (RBAC)
- **Roles**: Admin, DataAnalyst, Screener, Auditor
- **Principle of Least Privilege**: Minimal permissions assigned
- **Segregation of Duties**: No user can perform incompatible actions
- **Access Reviews**: Quarterly access audits

**Role Definitions**:
```json
{
  "roles": {
    "admin": {
      "permissions": ["scan_any", "export_audit", "manage_users", "configure_system"],
      "mfa_required": true
    },
    "data_analyst": {
      "permissions": ["scan_own_data", "view_own_audit"],
      "mfa_required": true
    },
    "auditor": {
      "permissions": ["view_all_audit", "generate_reports"],
      "mfa_required": true
    }
  }
}
```

### Audit Logging (§164.312(b))

#### Mandatory Audit Events
- ✅ User login/logout
- ✅ PHI access (scan, detect, export)
- ✅ Configuration changes
- ✅ Report generation
- ✅ Export operations
- ✅ Authentication failures
- ✅ Permission changes
- ✅ System errors

#### Audit Log Format (JSON)
```json
{
  "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-02-07T14:30:00.123Z",
  "user_id": "user@example.com",
  "user_ip": "192.168.1.100",
  "action": "PHI_SCAN",
  "resource": "patient_record_12345",
  "resource_type": "MedicalRecord",
  "result": "DETECTED_PHI",
  "phi_count": 5,
  "severity": "HIGH",
  "details": {
    "detected_elements": ["name", "dob", "mrn"],
    "compliance_status": "NON_COMPLIANT"
  },
  "hash_previous_entry": "sha256:...",
  "immutable": true,
  "retention_until": "2035-02-07"
}
```

#### Audit Log Protection
- **Immutability**: Cryptographic chain linking (tamper detection)
- **Integrity**: SHA-256 hash of previous entry + current entry
- **Retention**: Minimum 6 years (HIPAA requirement)
- **Access Control**: Auditor role only (append, no delete)
- **Replication**: Redundant storage locations
- **Encryption**: At-rest encryption with separate KEKs

### Integrity Controls (§164.312(c))

#### Mechanisms
- **Digital Signatures**: ECDSA SHA-256 for critical data
- **Message Authentication Codes**: HMAC-SHA-256
- **Checksums**: MD5 for quick validation (non-cryptographic)
- **Timestamps**: Verifiable NTP time synchronization

#### Cryptographic Linking
Each audit entry contains the hash of the previous entry, creating an unbreakable chain:

```
Entry N-1: {..., "hash_previous": "previous_hash", "hash_current": "abc123..."}
Entry N:   {..., "hash_previous": "abc123...", "hash_current": "def456..."}
Entry N+1: {..., "hash_previous": "def456...", "hash_current": "ghi789..."}
```

If Entry N is modified, its hash changes, breaking the chain for Entry N+1, which immediately reveals tampering.

---

## Data Minimization & Privacy

### PHI Collection Principles
- **Collect**: Only necessary for stated purpose
- **Use**: Only for specified use case
- **Retain**: Minimum necessary period
- **Destroy**: Cryptographic erasure upon retention expiration
- **Transfer**: Only to authorized recipients under BAA

### De-Identification Compliance
- **Safe Harbor Method**: Removal of 18 identifiers per §164.514(b)
- **Expert Determination**: Statistical disclosure control (SDC) optional
- **Limited Data Sets**: File-restricted identifiers per §164.514(e)

### Data Destruction
- **Overwrite**: 3-pass overwrite (Schneier/DoD standard) OR
- **Cryptographic**: Immediate key deletion (preferred)
- **Certification**: Destruction certificate generated per §164.504(b)(2)

**Destruction Log Entry**:
```json
{
  "destruction_id": "uuid",
  "timestamp": "2026-02-07T15:00:00Z",
  "data_category": "scan_results",
  "record_count": 1250,
  "method": "CRYPTOGRAPHIC_ERASURE",
  "kek_destroyed": "sha256:...",
  "authorized_by": "admin@example.com",
  "certificate_number": "2026-02-0001"
}
```

---

## Business Continuity & Disaster Recovery

### Backup Strategy
- **Frequency**: Daily backups, encrypted with separate KEK
- **Retention**: 90 days minimum (longer for compliance data)
- **Testing**: Monthly restore tests documented
- **Geographic Distribution**: Separate physical locations minimum 50 km apart

### Disaster Recovery Plan
- **RTO (Recovery Time Objective)**: 4 hours for critical systems
- **RPO (Recovery Point Objective)**: 1 hour maximum data loss
- **Failover**: Automated with manual override capability
- **Testing**: Annual DR drill with full-scale recovery test

### High Availability
- **Redundancy**: Active-passive replication
- **Monitoring**: Real-time system health checks
- **Alerting**: Automated escalation for critical alerts
- **Load Balancing**: Distribution across multiple systems

---

## Incident Response & Breach Procedures

### Incident Detection
- **Monitoring**: 24/7 intrusion detection system (IDS)
- **Alerting**: Automated alerts for suspicious patterns
- **Response Team**: On-call incident response team
- **Timeline**: Initial response within 1 hour

### Breach Assessment (§164.400-414)
1. **Detection**: Identify unauthorized PHI access/disclosure
2. **Containment**: Isolate affected systems (< 1 hour)
3. **Investigation**: Determine scope, affected individuals
4. **Risk Assessment**: Likelihood of compromise evaluation
5. **Notification**: Required within 60 days

### Notification Requirements
- **Individual**: Contact each affected person
- **Media**: If 500+ individuals affected in same jurisdiction
- **HHS Secretary**: Required for all breaches
- **Notification Template**: HIPAA-compliant notification letter

**Sample Notification Timeline**:
```
Day 1:   Breach detected & contained
Day 2:   Investigation initiated, HHS notified
Day 7:   Risk assessment completed
Day 30:  Detailed notification prepared, individuals contacted
Day 60:  Media/HHS notification completed
```

---

## Compliance Validation

### Internal Controls Testing
- **Quarterly**: Access control review
- **Quarterly**: Audit log integrity verification
- **Semi-annually**: Encryption key strength assessment
- **Annually**: Full risk assessment & penetration testing

### External Audits
- **Annual**: Third-party security audit (SOC 2 Type II)
- **Biennial**: HIPAA-specific compliance audit
- **As-needed**: Forensic investigation (breach response)

### Remediation
- **Critical Findings**: Must remediate within 30 days
- **High Findings**: Must remediate within 60 days
- **Medium Findings**: Must remediate within 90 days
- **Follow-up**: Verification of remediation within specified timeframe

---

## Third-Party Risk Management

### Vendor Assessment
- **Contracts**: Mandatory Business Associate Agreements (BAA)
- **Due Diligence**: On-site security audits for high-risk vendors
- **Ongoing Monitoring**: Quarterly compliance verification
- **Incident Response**: Vendor breach notification within 24 hours

### Acceptable Use Policy
Authorized uses of PHI:
- Clinical care delivery
- Payment processing
- Healthcare operations (administration, compliance)
- De-identified research (IRB approval required)
- Public health activities (government-authorized)

Prohibited uses:
- Marketing (except treatment-related)
- Sale of PHI (unless patient-authorized)
- Genetic research (without explicit consent)
- Unauthorized combinations with other data

---

## Security Incident Examples

### Scenario 1: Unauthorized PHI Access
```
Detected: User account accessing 10,000+ records vs. normal 50/day
Response:
1. Immediately revoke access (< 5 min)
2. Isolate affected data
3. Assess: Did attacker succeed?
4. Notify: If successful, 60-day notification triggered
5. Remediate: Enforce stronger MFA
```

### Scenario 2: Encryption Key Compromise
```
Detected: SSL certificate expires in 7 days, renewal failed
Response:
1. Emergency certificate reissuance (< 1 hour)
2. HSTS preload verification
3. Audit: Find any unencrypted data exposure
4. Document: Severity assessment for breach notification
```

###Scenario 3: Data Theft via Backup
```
Detected: Backup storage device not physically accounted for
Response:
1. Assume compromise (conservative approach)
2. Assess: What data was on device? (encrypted?)
3. Notify: If unencrypted, breach notification required
4. Remediate: Implement backup encryption, inventory tracking
```

---

## Compliance Resources

- [NIST SP 800-66: HIPAA Security Implementation](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-66r1.pdf)
- [NIST SP 800-52 Rev. 2: TLS Guidelines](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-52r2.pdf)
- [NIST SP 800-57: Key Management](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57Pt1R5.pdf)
- [CMS HIPAA Encryption Guidance](https://www.cms.gov/cms-forms/cms-forms-instructions)

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Next Review**: August 2026
