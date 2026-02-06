# NIST Cybersecurity Framework 2.0 Mapping to HIPAA

## Framework Overview

The **NIST Cybersecurity Framework (CSF) 2.0** organizes cybersecurity practices into 6 core functions:

- **Govern (GV)**: Establishes organizational context & risk management
- **Detect (DE)**: Identifies cybersecurity incidents in progress
- **Protect (PR)**: Safeguards against threats
- **Respond (RS)**: Takes action to manage incidents
- **Recover (RC)**: Restores capabilities after incidents
- **Inform (IF)**: Provides actionable insights (NEW in 2.0)

---

## HIPAA-to-CSF Mapping

### Govern (GV) - Organizational Risk Context

| HIPAA Requirement | CSF Function | Implementation |
|---|---|---|
| §164.308(a)(1) Security Management | GV.RM-01 | Annual risk assessment, mitigation planning |
| §164.308(a)(3) Workforce Security | GV.RM-02 | Access policy documentation, role definitions |
| §164.314(a) BAA Requirements | GV.RM-03 | Vendor risk assessment, BAA enforcement |
| §164.308(a)(5) Training | GV.AT-01 | Annual HIPAA training with documentation |

**hipaa-guardian Role**: Provide risk assessment templates & BAA checklists

---

### Detect (DE) - Incident Identification

| HIPAA Requirement | CSF Function | Implementation |
|---|---|---|
| §164.312(b) Audit Logging | DE.DM-01 | Monitor audit logs for suspicious patterns |
| §164.312(a)(1) Access Controls | DE.CM-01 | Unauthorized access attempts, login failures |
| Breach Notification | DE.CM-02 | Malware detection, unauthorized changes |
| §164.312(c) Integrity | DE.CM-07 | Data integrity monitoring, checksums |

**hipaa-guardian Role**: 
- ✅ Detect PHI in unstructured text (documents, emails, logs)
- ✅ Flag potential breaches by monitoring for PHI in unusual locations
- ✅ Identify failed de-identification attempts
- ✅ Detect entropy signatures of compromised data exports

---

### Protect (PR) - Preventive Safeguards

| HIPAA Requirement | CSF Function | Implementation |
|---|---|---|
| §164.312(a)(2) Encryption | PR.DS-01 | AES-256 at rest, TLS 1.3 in transit |
| §164.312(a)(1) Authentication | PR.AC-01 | Multi-factor auth, role-based access control |
| §164.308(a)(4) Information Access | PR.AC-03 | RBAC matrix, principle of least privilege |
| §164.310(b) Workstation Security | PR.AC-04 | Screen locks, inactivity timeouts |
| §164.308(a)(7) Backup/Recovery | PR.DS-04 | Encrypted backups, geographic distribution |

**hipaa-guardian Role**: 
- ✅ Validate encryption configurations against NIST SP 800-66 standards
- ✅ Test access control matrices for segregation of duties violations
- ✅ Verify backup encryption & retention policies

---

### Respond (RS) - Incident Response

| HIPAA Requirement | CSF Function | Implementation |
|---|---|---|
| §164.400-414 Breach Notification | RS.CO-01 | Incident response plan activation |
| Breach Assessment | RS.AN-01 | Risk assessment per §164.404(b)(2) |
| Investigation | RS.AN-02 | Forensic investigation, evidence preservation |
| Notification | RS.CO-02 | 60-day notification timeline |

**hipaa-guardian Role**: 
- ✅ Generate breach notification letters
- ✅ Track breach investigation timeline
- ✅ Calculate notification requirements (individual/media/HHS)
- ✅ Document risk assessment findings

---

### Recover (RC) - Restoration

| HIPAA Requirement | CSF Function | Implementation |
|---|---|---|
| §164.308(a)(7) Contingency Planning | RC.RP-01 | Tested disaster recovery procedures |
| System Restoration | RC.RP-02 | RTO ≤ 4 hours, RPO ≤ 1 hour |
| Post-Incident Review | RC.IM-01 | Conduct lessons-learned review |
| Remediation | RC.CO-01 | Implement corrective actions |

**hipaa-guardian Role**: 
- ✅ Validate backup integrity for recovery
- ✅ Document recovery procedures
- ✅ Track remediation completion

---

### Inform (IF) - Strategic Insights [NEW in CSF 2.0]

| CSF Function | HIPAA Alignment | Implementation |
|---|---|---|
| IF.GV-01 Supply Chain | BAA requirements | Vendor compliance tracking |
| IF.GV-02 Environmental Factors | Regulatory changes | HIPAA updates, state law compliance |
| IF.RV-01 Risk Insights | Risk assessment | Continuous risk monitoring |
| IF.RV-02 Threat Landscape | External threats | Healthcare sector threat intelligence |

**hipaa-guardian Role**: 
- ✅ Monitor HHS Office for Civil Rights (OCR) precedents
- ✅ Track breach notification rule changes
- ✅ Highlight emerging PHI attack vectors (e.g., ransomware)

---

## CSF 2.0 Tiers (Maturity Model)

hipaa-guardian supports assessment across maturity tiers:

| Tier | Characteristics | HIPAA Alignment |
|---|---|---|
| **Tier 1: Partial** | Reactive, ad hoc processes | Below HIPAA standard |
| **Tier 2: Risk-Informed** | Risk-based policies, inconsistent implementation | HIPAA minimum baseline |
| **Tier 3: Repeatable** | Documented procedures, regular reviews | HIPAA best practices |
| **Tier 4: Optimized** | Continuous improvement, automated monitoring | Exceeds HIPAA requirements |

**hipaa-guardian Assessment**:
- Tier 1: ❌ No formal PHI detection procedures
- Tier 2: ✅ Annual risk assessment, basic audit logging
- Tier 3: ✅ Documented de-identification, regular monitoring
- Tier 4: ✅ Real-time PHI detection, continuous compliance

---

## Profile Development

Create a CSF Profile to align HIPAA objectives with CSF functions:

### Example: Telehealth PHI Protection Profile

| HIPAA Goal | CSF Function | Control |
|---|---|---|
| Protect patient notes | PR.DS-01 | Encrypt all files at rest (AES-256) |
| Detect unauthorized access | DE.CM-01 | Monitor login attempts, alert on failures |
| Respond to breaches | RS.CO-01 | Activate incident response within 1 hour |
| Document safeguards | GV.RV-01 | Monthly compliance report |

---

## Assessment Tool (hipaa-guardian)

Use hipaa-guardian to assess HIPAA/CSF maturity:

```yaml
# HIPAA-CSF Assessment Template
assessment:
  organization: "Healthcare Clinic XYZ"
  date: "2026-02-07"
  
  categories:
    - function: "Govern"
      controls:
        - GV.RM-01: "Risk Assessment"
          status: "Compliant"  # Tier 3+
          last_reviewed: "2025-12-15"
          findings: []
        
    - function: "Detect"
      controls:
        - DE.CM-01: "PHI Unauthorized Access Monitoring"
          status: "Non-Compliant"  # Tier 2 only
          gap: "No real-time monitoring, only manual logs"
          recommendation: "Implement SIEM with PHI detection rules"
          estimated_effort: "3 months"
```

---

## HIPAA Organizations as CSF Profile Users

| Organization Type | CSF Profile Focus | hipaa-guardian Role |
|---|---|---|
| Small Clinic | GV (governance) + DE (detection) | Risk assessment, audit templates |
| Hospital Network | All functions | Comprehensive monitoring, breach response |
| Health Plan | GV, PR (protection), RS (response) | Member data protection, audit controls |
| Covered Entity (Telehealth) | DE, PR, RS | Real-time PHI detection, incident response |

---

**Last Updated**: February 2026  
**CSF Version**: 2.0  
**HIPAA Alignment**: Full mapping
