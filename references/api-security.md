# API Response Masking and Field-Level Authorization

**HIPAA Security Rule Reference:** 45 CFR §164.312(a)(1) - Access Control, §164.502(b) - Minimum Necessary

---

## Overview

APIs exposing patient data must implement:
1. **Field-level authorization** - Different roles see different fields
2. **Data masking** - Sensitive fields masked unless explicitly needed
3. **Minimum necessary principle** - Only return required data
4. **Response filtering** - Never return full ORM objects directly

---

## Detection Patterns

### 1. Full Object Returns (Dangerous)

```regex
# Python - returning full ORM objects
return\s+jsonify\s*\(\s*patient\s*\)
return\s+patient\.to_dict\(\)
return\s+PatientSchema\(\)\.dump\(patient\)(?!.*exclude)

# JavaScript - returning full documents
res\.json\s*\(\s*patient\s*\)
res\.send\s*\(\s*patient\s*\)
return\s+patient(?!\.select|\.project)

# Java - returning full entities
return\s+ResponseEntity\.ok\s*\(\s*patient\s*\)
return\s+patient;(?!.*DTO)
```

### 2. SELECT * Queries

```regex
# SQL
SELECT\s+\*\s+FROM\s+patient
SELECT\s+\*\s+FROM\s+medical_record

# ORM
Patient\.query\.all\(\)
Patient\.objects\.all\(\)
Patient\.find\(\{\}\)
patientRepository\.findAll\(\)
```

### 3. Missing Field Filtering

```regex
# No explicit field selection
Patient\.query\.get\(
Patient\.findById\(
Patient\.objects\.get\(
patientRepository\.findById\(
```

### 4. GraphQL Without Field Authorization

```regex
# GraphQL resolvers without auth checks
resolve:\s*\([^)]*\)\s*=>\s*[^{]*patient\.(ssn|dob|mrn)
```

---

## Compliant Implementation Patterns

### Python - Response Masking

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Set
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    NURSE = "nurse"
    RECEPTIONIST = "receptionist"
    BILLING = "billing"

@dataclass
class FieldPolicy:
    """Defines access and masking policy for a field."""
    allowed_roles: Set[Role]
    mask_for_roles: Set[Role] = None  # Roles that see masked version
    mask_func: callable = None
    
    def can_access(self, role: Role) -> bool:
        return role in self.allowed_roles
    
    def should_mask(self, role: Role) -> bool:
        return self.mask_for_roles and role in self.mask_for_roles

class PatientResponseFilter:
    """
    Filters patient data based on user role and field policies.
    Implements HIPAA minimum necessary principle.
    """
    
    FIELD_POLICIES = {
        # Identifiers
        'id': FieldPolicy(allowed_roles={Role.ADMIN, Role.DOCTOR, Role.NURSE, 
                                          Role.RECEPTIONIST, Role.BILLING}),
        'mrn': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.DOCTOR, Role.NURSE},
            mask_for_roles={Role.RECEPTIONIST},
            mask_func=lambda x: f"***{x[-4:]}" if x else None
        ),
        
        # Demographics
        'name': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.DOCTOR, Role.NURSE, Role.RECEPTIONIST},
            mask_for_roles={Role.BILLING},
            mask_func=lambda x: f"{x[0]}***" if x else None
        ),
        'dob': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.DOCTOR, Role.NURSE},
            mask_for_roles={Role.RECEPTIONIST},
            mask_func=lambda x: f"**/**/****"
        ),
        
        # Sensitive identifiers
        'ssn': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.BILLING},
            mask_for_roles={Role.ADMIN},
            mask_func=lambda x: f"***-**-{x[-4:]}" if x else None
        ),
        
        # Clinical data
        'diagnosis': FieldPolicy(allowed_roles={Role.DOCTOR, Role.NURSE}),
        'medications': FieldPolicy(allowed_roles={Role.DOCTOR, Role.NURSE}),
        'allergies': FieldPolicy(allowed_roles={Role.DOCTOR, Role.NURSE}),
        
        # Contact
        'email': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.RECEPTIONIST},
            mask_func=lambda x: f"{x[0]}***@***" if x else None
        ),
        'phone': FieldPolicy(
            allowed_roles={Role.ADMIN, Role.RECEPTIONIST},
            mask_func=lambda x: f"(***) ***-{x[-4:]}" if x else None
        ),
        
        # Financial
        'insurance_id': FieldPolicy(allowed_roles={Role.ADMIN, Role.BILLING}),
        'balance': FieldPolicy(allowed_roles={Role.ADMIN, Role.BILLING}),
    }
    
    @classmethod
    def filter_response(cls, patient_data: Dict[str, Any], 
                       user_role: Role,
                       requested_fields: List[str] = None) -> Dict[str, Any]:
        """
        Filter patient data based on role and requested fields.
        
        Args:
            patient_data: Raw patient data dictionary
            user_role: Role of the requesting user
            requested_fields: Optional list of specifically requested fields
            
        Returns:
            Filtered and masked patient data
        """
        result = {}
        
        # If specific fields requested, only consider those
        fields_to_check = requested_fields or patient_data.keys()
        
        for field in fields_to_check:
            if field not in patient_data:
                continue
                
            policy = cls.FIELD_POLICIES.get(field)
            
            if policy is None:
                # Unknown field - exclude by default (fail secure)
                continue
            
            if not policy.can_access(user_role):
                # User cannot access this field
                continue
            
            value = patient_data[field]
            
            if policy.should_mask(user_role) and policy.mask_func:
                # User can access but sees masked version
                result[field] = policy.mask_func(value)
            else:
                result[field] = value
        
        return result

# Usage in API endpoint
@app.route('/api/patient/<patient_id>')
@require_auth
def get_patient(patient_id):
    user = get_current_user()
    patient = Patient.query.get(patient_id)
    
    # Get raw data
    patient_data = patient.to_dict()
    
    # Filter based on role
    filtered = PatientResponseFilter.filter_response(
        patient_data,
        user_role=Role(user.role),
        requested_fields=request.args.getlist('fields')  # Optional field selection
    )
    
    # Audit log what was accessed
    audit_log.phi_access(
        user_id=user.id,
        patient_id=patient_id,
        fields_returned=list(filtered.keys())
    )
    
    return jsonify(filtered)
```

### JavaScript/TypeScript - Response Transformer

```typescript
interface FieldPolicy {
  allowedRoles: string[];
  maskForRoles?: string[];
  maskFn?: (value: any) => any;
}

const FIELD_POLICIES: Record<string, FieldPolicy> = {
  id: { allowedRoles: ['admin', 'doctor', 'nurse', 'receptionist', 'billing'] },
  mrn: {
    allowedRoles: ['admin', 'doctor', 'nurse'],
    maskForRoles: ['receptionist'],
    maskFn: (v) => v ? `***${v.slice(-4)}` : null
  },
  name: {
    allowedRoles: ['admin', 'doctor', 'nurse', 'receptionist'],
    maskForRoles: ['billing'],
    maskFn: (v) => v ? `${v[0]}***` : null
  },
  dob: {
    allowedRoles: ['admin', 'doctor', 'nurse'],
    maskForRoles: ['receptionist'],
    maskFn: () => '**/**/****'
  },
  ssn: {
    allowedRoles: ['admin', 'billing'],
    maskForRoles: ['admin', 'billing'],
    maskFn: (v) => v ? `***-**-${v.slice(-4)}` : null
  },
  diagnosis: { allowedRoles: ['doctor', 'nurse'] },
  medications: { allowedRoles: ['doctor', 'nurse'] },
  email: {
    allowedRoles: ['admin', 'receptionist'],
    maskFn: (v) => v ? `${v[0]}***@***` : null
  },
  phone: {
    allowedRoles: ['admin', 'receptionist'],
    maskFn: (v) => v ? `(***) ***-${v.slice(-4)}` : null
  }
};

function filterPatientResponse(
  patientData: Record<string, any>,
  userRole: string,
  requestedFields?: string[]
): Record<string, any> {
  const result: Record<string, any> = {};
  const fields = requestedFields || Object.keys(patientData);

  for (const field of fields) {
    if (!(field in patientData)) continue;

    const policy = FIELD_POLICIES[field];
    if (!policy) continue; // Unknown field - exclude

    if (!policy.allowedRoles.includes(userRole)) continue;

    let value = patientData[field];

    if (policy.maskForRoles?.includes(userRole) && policy.maskFn) {
      value = policy.maskFn(value);
    }

    result[field] = value;
  }

  return result;
}

// Express middleware for automatic filtering
const filterPHIResponse = (req: Request, res: Response, next: NextFunction) => {
  const originalJson = res.json.bind(res);

  res.json = (body: any) => {
    // Check if response contains patient data
    if (body && (body.patient || body.patients)) {
      const userRole = req.user?.role || 'guest';
      
      if (body.patient) {
        body.patient = filterPatientResponse(body.patient, userRole);
      }
      
      if (body.patients) {
        body.patients = body.patients.map((p: any) => 
          filterPatientResponse(p, userRole)
        );
      }
    }

    return originalJson(body);
  };

  next();
};

// Apply middleware
app.use('/api/patient*', authenticate, filterPHIResponse);
```

### Java - DTO with Role-Based Projection

```java
// Base Patient DTO
@JsonInclude(JsonInclude.Include.NON_NULL)
public class PatientDTO {
    private String id;
    private String name;
    private String dob;
    private String ssn;
    private String mrn;
    private String diagnosis;
    private String email;
    private String phone;
    
    // Role-based static factory methods
    public static PatientDTO forDoctor(Patient patient) {
        return PatientDTO.builder()
            .id(patient.getId())
            .name(patient.getName())
            .dob(patient.getDob())
            .mrn(patient.getMrn())
            .diagnosis(patient.getDiagnosis())
            .build();
    }
    
    public static PatientDTO forNurse(Patient patient) {
        return PatientDTO.builder()
            .id(patient.getId())
            .name(patient.getName())
            .dob(patient.getDob())
            .mrn(patient.getMrn())
            .diagnosis(patient.getDiagnosis())
            .build();
    }
    
    public static PatientDTO forReceptionist(Patient patient) {
        return PatientDTO.builder()
            .id(patient.getId())
            .name(patient.getName())
            .dob(maskDate(patient.getDob()))  // Masked
            .phone(patient.getPhone())
            .email(patient.getEmail())
            .build();
    }
    
    public static PatientDTO forBilling(Patient patient) {
        return PatientDTO.builder()
            .id(patient.getId())
            .name(maskName(patient.getName()))  // Masked
            .ssn(maskSSN(patient.getSsn()))     // Masked
            .build();
    }
    
    private static String maskSSN(String ssn) {
        if (ssn == null || ssn.length() < 4) return null;
        return "***-**-" + ssn.substring(ssn.length() - 4);
    }
    
    private static String maskDate(String date) {
        return "**/**/****";
    }
    
    private static String maskName(String name) {
        if (name == null || name.isEmpty()) return null;
        return name.charAt(0) + "***";
    }
}

// Service with role-aware projection
@Service
public class PatientService {
    
    public PatientDTO getPatient(String patientId, User currentUser) {
        Patient patient = patientRepository.findById(patientId)
            .orElseThrow(() -> new PatientNotFoundException(patientId));
        
        // Role-based projection
        PatientDTO dto = switch (currentUser.getRole()) {
            case DOCTOR -> PatientDTO.forDoctor(patient);
            case NURSE -> PatientDTO.forNurse(patient);
            case RECEPTIONIST -> PatientDTO.forReceptionist(patient);
            case BILLING -> PatientDTO.forBilling(patient);
            default -> throw new AccessDeniedException("Unknown role");
        };
        
        // Audit log
        auditService.logPatientAccess(currentUser, patientId, dto.getAccessedFields());
        
        return dto;
    }
}
```

### GraphQL - Field-Level Authorization

```javascript
const { GraphQLObjectType, GraphQLString, GraphQLID } = require('graphql');

const PatientType = new GraphQLObjectType({
  name: 'Patient',
  fields: () => ({
    id: { type: GraphQLID },
    
    name: {
      type: GraphQLString,
      resolve: (patient, args, context) => {
        if (!hasFieldAccess(context.user, 'name')) {
          return null;
        }
        auditFieldAccess(context.user, patient.id, 'name');
        return patient.name;
      }
    },
    
    ssn: {
      type: GraphQLString,
      resolve: (patient, args, context) => {
        // Very restricted access
        if (!context.user.hasRole(['admin', 'billing'])) {
          auditUnauthorizedAccess(context.user, patient.id, 'ssn');
          return null;
        }
        
        auditFieldAccess(context.user, patient.id, 'ssn');
        
        // Always return masked
        return patient.ssn ? `***-**-${patient.ssn.slice(-4)}` : null;
      }
    },
    
    dob: {
      type: GraphQLString,
      resolve: (patient, args, context) => {
        if (!context.user.hasRole(['doctor', 'nurse', 'admin'])) {
          return null;
        }
        
        auditFieldAccess(context.user, patient.id, 'dob');
        
        // Mask for non-clinical roles
        if (context.user.hasRole(['admin'])) {
          return '**/**/****';
        }
        
        return patient.dob;
      }
    },
    
    diagnosis: {
      type: GraphQLString,
      resolve: (patient, args, context) => {
        // Clinical data - clinical roles only
        if (!context.user.hasRole(['doctor', 'nurse'])) {
          auditUnauthorizedAccess(context.user, patient.id, 'diagnosis');
          return null;
        }
        
        auditFieldAccess(context.user, patient.id, 'diagnosis');
        return patient.diagnosis;
      }
    }
  })
});

// Field access checker
function hasFieldAccess(user, fieldName) {
  const fieldRoles = {
    name: ['admin', 'doctor', 'nurse', 'receptionist'],
    dob: ['admin', 'doctor', 'nurse'],
    ssn: ['admin', 'billing'],
    diagnosis: ['doctor', 'nurse'],
    medications: ['doctor', 'nurse'],
    phone: ['admin', 'receptionist'],
    email: ['admin', 'receptionist'],
  };
  
  const allowedRoles = fieldRoles[fieldName] || [];
  return allowedRoles.some(role => user.hasRole([role]));
}
```

---

## Masking Functions

```python
# Common masking utilities
class PHIMasking:
    
    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """SSN: 123-45-6789 -> ***-**-6789"""
        if not ssn or len(ssn) < 4:
            return None
        return f"***-**-{ssn[-4:]}"
    
    @staticmethod
    def mask_dob(dob: str) -> str:
        """DOB: Any format -> **/**/****"""
        return "**/**/****"
    
    @staticmethod
    def mask_name(name: str) -> str:
        """Name: John Smith -> J*** S***"""
        if not name:
            return None
        parts = name.split()
        return " ".join(f"{p[0]}***" for p in parts if p)
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Email: john@example.com -> j***@e***.com"""
        if not email or '@' not in email:
            return None
        local, domain = email.split('@', 1)
        domain_parts = domain.rsplit('.', 1)
        return f"{local[0]}***@{domain_parts[0][0]}***.{domain_parts[-1]}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Phone: (555) 123-4567 -> (***) ***-4567"""
        if not phone or len(phone) < 4:
            return None
        digits = ''.join(c for c in phone if c.isdigit())
        return f"(***) ***-{digits[-4:]}"
    
    @staticmethod
    def mask_mrn(mrn: str) -> str:
        """MRN: AB12345678 -> ****5678"""
        if not mrn or len(mrn) < 4:
            return None
        return f"****{mrn[-4:]}"
    
    @staticmethod
    def mask_address(address: str) -> str:
        """Address: 123 Main St -> *** Main St"""
        if not address:
            return None
        # Mask street number
        import re
        return re.sub(r'^\d+', '***', address)
```

---

## HIPAA Rule Mapping

| Violation | HIPAA Section | Description |
|-----------|---------------|-------------|
| Returning full patient object | §164.502(b) | Minimum necessary violation |
| No role-based filtering | §164.312(a)(1) | Access control required |
| SELECT * on PHI tables | §164.502(b) | Minimum necessary violation |
| No field-level auth | §164.312(a)(1) | Granular access control |
| Missing data masking | §164.514(b) | De-identification required |

---

## Risk Scoring for Response Violations

| Issue | Base Score | Multipliers |
|-------|------------|-------------|
| Full patient object in response | 85 | Public API: 1.15x |
| SELECT * on patient table | 75 | No WHERE clause: 1.2x |
| SSN returned unmasked | 95 | Any role: 1.1x |
| No role-based filtering | 80 | Internet-facing: 1.15x |
| Missing field-level auth | 70 | GraphQL: 1.1x |

---

## Checklist for API PHI Protection

- [ ] Never return full ORM/Document objects directly
- [ ] Implement field-level access control
- [ ] Apply masking based on user role and need
- [ ] Use SELECT with explicit columns, never SELECT *
- [ ] Implement response DTOs/transformers
- [ ] Audit log which fields are returned
- [ ] Apply minimum necessary principle
- [ ] Validate requested fields against allowed list
- [ ] Use projections in GraphQL/MongoDB queries
- [ ] Test response filtering for each role
