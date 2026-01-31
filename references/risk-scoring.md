# Risk Scoring Methodology

A comprehensive framework for assessing and scoring PHI/PII detection findings based on sensitivity, exposure, volume, and identifiability factors.

## Overview

Risk scores range from 0-100 and indicate the severity and urgency of addressing a PHI finding.

| Score Range | Severity | Response Time | Action Required |
|-------------|----------|---------------|-----------------|
| 90-100 | Critical | Immediate | Stop work, remediate now |
| 70-89 | High | 24 hours | Prioritize remediation |
| 50-69 | Medium | 1 week | Schedule remediation |
| 25-49 | Low | 1 month | Plan remediation |
| 0-24 | Informational | As needed | Review and document |

---

## Risk Score Formula

```
Risk Score = (Sensitivity × 0.35) + (Exposure × 0.25) +
             (Volume × 0.20) + (Identifiability × 0.20)
```

Each factor is scored 0-100, then weighted to produce final score.

---

## Factor 1: Sensitivity (35% weight)

How sensitive is the detected information type?

### Base Sensitivity Scores

| Data Type | Score | Rationale |
|-----------|-------|-----------|
| SSN | 100 | Universal identifier, high fraud risk |
| Financial (credit card, bank account) | 95 | Direct financial harm potential |
| Biometric data | 95 | Immutable, cannot be changed |
| Medical diagnosis/treatment | 90 | Highly sensitive health information |
| Mental health records | 95 | Stigma potential, extra protections |
| Substance abuse records | 95 | 42 CFR Part 2 protections |
| HIV/AIDS status | 95 | Stigma, discrimination potential |
| Genetic information | 95 | GINA protections, family implications |
| Full DOB | 85 | Key identifier for fraud |
| Medical Record Number | 80 | Healthcare-specific identifier |
| Health plan ID | 75 | Insurance fraud potential |
| Full name | 70 | Common identifier |
| Address | 70 | Location information |
| Phone number | 60 | Contact information |
| Email address | 55 | Contact, account recovery |
| Age (not DOB) | 40 | Partial identifier |
| ZIP code (full) | 35 | Geographic, population dependent |
| Gender | 20 | Demographic only |

### Sensitivity Modifiers

```python
def calculate_sensitivity(data_type, context):
    base_score = SENSITIVITY_SCORES.get(data_type, 50)

    # Modifier: Combined with health information
    if context.get('health_context'):
        base_score = min(100, base_score + 15)

    # Modifier: Minor's information
    if context.get('minor'):
        base_score = min(100, base_score + 10)

    # Modifier: Deceased individual (lower sensitivity)
    if context.get('deceased'):
        base_score = max(0, base_score - 20)

    # Modifier: Already public information
    if context.get('public_record'):
        base_score = max(0, base_score - 30)

    return base_score
```

---

## Factor 2: Exposure (25% weight)

How accessible is the PHI to unauthorized parties?

### Exposure Level Scores

| Exposure Level | Score | Description |
|---------------|-------|-------------|
| Public internet | 100 | Accessible to anyone online |
| Public repository | 95 | GitHub public, etc. |
| Shared network drive | 75 | Internal but broadly accessible |
| Cloud storage (misconfigured) | 85 | S3 bucket, etc. without proper ACL |
| Application logs | 70 | Potentially accessible to ops team |
| Database (unencrypted) | 65 | Accessible to DBAs, backups |
| Source code repository | 60 | Accessible to development team |
| Test environment | 55 | Usually less protected |
| Local file system | 40 | Single machine access |
| Encrypted storage | 25 | Protected but still present |
| Encrypted + access controlled | 15 | Multiple layers of protection |

### Exposure Modifiers

```python
def calculate_exposure(location, access_controls):
    base_score = EXPOSURE_SCORES.get(location, 50)

    # Modifier: No authentication required
    if not access_controls.get('authentication'):
        base_score = min(100, base_score + 20)

    # Modifier: Multi-factor authentication
    if access_controls.get('mfa'):
        base_score = max(0, base_score - 15)

    # Modifier: Audit logging enabled
    if access_controls.get('audit_logging'):
        base_score = max(0, base_score - 10)

    # Modifier: Time-limited access
    if access_controls.get('time_limited'):
        base_score = max(0, base_score - 10)

    return base_score
```

---

## Factor 3: Volume (20% weight)

How many individuals or records are affected?

### Volume Thresholds

| Count | Score | Description |
|-------|-------|-------------|
| 500+ | 100 | Triggers media notification requirement |
| 100-499 | 85 | Significant breach potential |
| 50-99 | 70 | Moderate scope |
| 10-49 | 55 | Limited scope |
| 2-9 | 40 | Small number affected |
| 1 | 25 | Single individual |
| Unknown | 75 | Assume moderate until determined |

### Volume Calculation

```python
def calculate_volume(record_count, unique_individuals=None):
    if unique_individuals:
        count = unique_individuals
    else:
        count = record_count

    if count is None:
        return 75  # Unknown, assume moderate

    if count >= 500:
        return 100
    elif count >= 100:
        return 85
    elif count >= 50:
        return 70
    elif count >= 10:
        return 55
    elif count >= 2:
        return 40
    else:
        return 25
```

---

## Factor 4: Identifiability (20% weight)

How easily can the data be linked to a specific individual?

### Identifiability Levels

| Level | Score | Description |
|-------|-------|-------------|
| Direct identifier (SSN, name) | 100 | Immediate identification |
| Quasi-identifier combination | 85 | DOB + ZIP + Gender = 87% unique |
| Linked to known individual | 80 | Foreign key to identified record |
| Contextually identifiable | 65 | Can be identified with effort |
| Aggregated data | 40 | Statistical, not individual |
| De-identified (Safe Harbor) | 20 | 18 identifiers removed |
| Expert certified de-identified | 10 | Statistical verification |
| Synthetic data | 5 | No real individuals |

### Combination Risk

When multiple identifiers appear together, identifiability increases:

```python
def calculate_identifiability(identifiers_found, context):
    if not identifiers_found:
        return 0

    # Direct identifiers
    direct = ['ssn', 'mrn', 'email', 'phone', 'name', 'account_number']
    quasi = ['dob', 'zip', 'gender', 'age']

    direct_count = sum(1 for i in identifiers_found if i in direct)
    quasi_count = sum(1 for i in identifiers_found if i in quasi)

    # Single direct identifier
    if direct_count >= 1:
        base_score = 100
    # Multiple quasi-identifiers
    elif quasi_count >= 3:
        base_score = 90  # High re-identification risk
    elif quasi_count == 2:
        base_score = 75
    elif quasi_count == 1:
        base_score = 50
    else:
        base_score = 30

    # Combined with health information
    if context.get('health_context'):
        base_score = min(100, base_score + 10)

    return base_score
```

### Re-identification Research Reference

| Combination | Population Uniqueness |
|-------------|----------------------|
| DOB + Gender + 5-digit ZIP | 87% |
| DOB + Gender + 3-digit ZIP | 53% |
| Birth year + Gender + ZIP | 18% |
| DOB alone | <1% |

Source: Sweeney, L. (2000). Simple Demographics Often Identify People Uniquely.

---

## Complete Risk Calculation

```python
def calculate_risk_score(finding):
    """
    Calculate overall risk score for a PHI finding.

    Args:
        finding: dict with keys:
            - data_type: Type of PHI detected
            - location: Where PHI was found
            - record_count: Number of records
            - identifiers: List of identifier types found
            - context: Additional context dict
            - access_controls: Access control information

    Returns:
        dict with overall score and factor breakdowns
    """

    # Calculate each factor
    sensitivity = calculate_sensitivity(
        finding['data_type'],
        finding.get('context', {})
    )

    exposure = calculate_exposure(
        finding['location'],
        finding.get('access_controls', {})
    )

    volume = calculate_volume(
        finding.get('record_count'),
        finding.get('unique_individuals')
    )

    identifiability = calculate_identifiability(
        finding.get('identifiers', []),
        finding.get('context', {})
    )

    # Apply weights
    overall = (
        (sensitivity * 0.35) +
        (exposure * 0.25) +
        (volume * 0.20) +
        (identifiability * 0.20)
    )

    return {
        'overall': round(overall),
        'severity': get_severity_level(overall),
        'factors': {
            'sensitivity': {
                'score': sensitivity,
                'weight': 0.35,
                'weighted': round(sensitivity * 0.35)
            },
            'exposure': {
                'score': exposure,
                'weight': 0.25,
                'weighted': round(exposure * 0.25)
            },
            'volume': {
                'score': volume,
                'weight': 0.20,
                'weighted': round(volume * 0.20)
            },
            'identifiability': {
                'score': identifiability,
                'weight': 0.20,
                'weighted': round(identifiability * 0.20)
            }
        }
    }

def get_severity_level(score):
    """Map numeric score to severity level."""
    if score >= 90:
        return 'critical'
    elif score >= 70:
        return 'high'
    elif score >= 50:
        return 'medium'
    elif score >= 25:
        return 'low'
    else:
        return 'informational'
```

---

## Example Risk Calculations

### Example 1: SSN in Public GitHub Repository
```yaml
finding:
  data_type: ssn
  location: public_repository
  record_count: 1
  identifiers: [ssn]
  context:
    health_context: false

calculation:
  sensitivity: 100 (SSN = 100)
  exposure: 95 (public repo)
  volume: 25 (1 record)
  identifiability: 100 (direct identifier)

  overall: (100×0.35) + (95×0.25) + (25×0.20) + (100×0.20)
         = 35 + 23.75 + 5 + 20
         = 83.75 → 84

result:
  score: 84
  severity: high
  action: Remediate within 24 hours
```

### Example 2: Names + DOB in Encrypted Database
```yaml
finding:
  data_type: name
  location: database
  record_count: 500
  identifiers: [name, dob]
  context:
    health_context: true
  access_controls:
    authentication: true
    mfa: true
    audit_logging: true

calculation:
  sensitivity: 85 (name=70 + health_context=15)
  exposure: 30 (65 - 15 MFA - 10 audit - 10 encryption)
  volume: 100 (500+ records)
  identifiability: 100 (name + health context)

  overall: (85×0.35) + (30×0.25) + (100×0.20) + (100×0.20)
         = 29.75 + 7.5 + 20 + 20
         = 77.25 → 77

result:
  score: 77
  severity: high
  action: Prioritize remediation, review access controls
```

### Example 3: Test Email in Local Code Comment
```yaml
finding:
  data_type: email
  location: source_code
  record_count: 1
  identifiers: [email]
  context:
    health_context: false
    test_data: true

calculation:
  sensitivity: 55 (email)
  exposure: 40 (local, test context)
  volume: 25 (1 record)
  identifiability: 50 (quasi-identifier)

  overall: (55×0.35) + (40×0.25) + (25×0.20) + (50×0.20)
         = 19.25 + 10 + 5 + 10
         = 44.25 → 44

result:
  score: 44
  severity: low
  action: Plan remediation, use synthetic data
```

---

## Risk Score Output Format

```json
{
  "finding_id": "F-20260128-0001",
  "risk_assessment": {
    "overall_score": 84,
    "severity": "high",
    "response_required": "24 hours",
    "factors": {
      "sensitivity": {
        "score": 100,
        "weight": "35%",
        "weighted_contribution": 35,
        "rationale": "SSN - universal identifier with high fraud risk"
      },
      "exposure": {
        "score": 95,
        "weight": "25%",
        "weighted_contribution": 23.75,
        "rationale": "Public GitHub repository - accessible to anyone"
      },
      "volume": {
        "score": 25,
        "weight": "20%",
        "weighted_contribution": 5,
        "rationale": "Single record affected"
      },
      "identifiability": {
        "score": 100,
        "weight": "20%",
        "weighted_contribution": 20,
        "rationale": "Direct identifier - immediate identification possible"
      }
    },
    "recommended_actions": [
      "Immediately remove SSN from repository",
      "Rotate git history to remove from commits",
      "Assess if breach notification required",
      "Implement pre-commit hooks to prevent recurrence"
    ]
  }
}
```
