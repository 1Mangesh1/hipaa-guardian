# Authentication Gate Patterns for PHI Endpoints

**HIPAA Security Rule Reference:** 45 CFR §164.312(d) - Person or Entity Authentication

---

## Overview

Any API endpoint, function, or code path that accesses Protected Health Information (PHI) MUST implement authentication and authorization gates. This document provides detection patterns and compliant implementations.

---

## Detection Patterns

### 1. Unprotected Route Detection

#### Python (Flask/FastAPI)

```regex
# Flask routes without auth decorator
@app\.route\([^)]*patient[^)]*\)\s*\n\s*def\s+\w+\([^)]*\):(?!\s*@require_auth)

# FastAPI routes without Depends(auth)
@(app|router)\.(get|post|put|delete|patch)\([^)]*patient[^)]*\)(?!.*Depends.*auth)
```

#### JavaScript/TypeScript (Express/NestJS)

```regex
# Express routes without middleware
(app|router)\.(get|post|put|delete)\s*\(\s*['"]/.*patient.*['"],\s*(?!.*authenticate)

# NestJS controllers without guards
@(Get|Post|Put|Delete)\([^)]*patient[^)]*\)(?!\s*@UseGuards)
```

#### Java (Spring)

```regex
# Spring endpoints without @PreAuthorize
@(GetMapping|PostMapping|PutMapping|DeleteMapping)\([^)]*patient[^)]*\)(?!\s*@PreAuthorize)
```

### 2. Missing Role-Based Access Control

```regex
# Generic auth but no role check
@require_auth\s*\n\s*def\s+\w+\([^)]*patient[^)]*\):(?!.*role|permission|authorize)
```

### 3. Direct Database PHI Access Without Auth Context

```regex
# ORM queries for PHI without user context
Patient\.(query|objects|find|where).*(?!user|current_user|request\.user)
```

---

## Compliant Implementation Patterns

### Python - Flask

```python
from functools import wraps
from flask import request, abort, g
import jwt

def require_auth(f):
    """Authentication decorator - verifies JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            abort(401, description="Authentication required")
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            g.current_user = User.query.get(payload['user_id'])
            if not g.current_user:
                abort(401, description="Invalid user")
        except jwt.ExpiredSignatureError:
            abort(401, description="Token expired")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token")
            
        return f(*args, **kwargs)
    return decorated

def require_role(roles):
    """Authorization decorator - checks user roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not g.current_user:
                abort(401)
            if g.current_user.role not in roles:
                audit_log.unauthorized_access(
                    user_id=g.current_user.id,
                    required_roles=roles,
                    endpoint=request.endpoint
                )
                abort(403, description="Insufficient permissions")
            return f(*args, **kwargs)
        return decorated
    return decorator

def require_patient_access(f):
    """Resource-level authorization - user must have access to specific patient."""
    @wraps(f)
    def decorated(*args, **kwargs):
        patient_id = kwargs.get('patient_id') or request.view_args.get('patient_id')
        if not patient_id:
            abort(400, description="Patient ID required")
        
        if not g.current_user.can_access_patient(patient_id):
            audit_log.unauthorized_patient_access(
                user_id=g.current_user.id,
                patient_id=patient_id
            )
            abort(403, description="Access to this patient denied")
        
        return f(*args, **kwargs)
    return decorated

# Usage
@app.route('/api/patient/<patient_id>')
@require_auth
@require_role(['doctor', 'nurse', 'admin'])
@require_patient_access
@audit_phi_access
def get_patient(patient_id):
    # Safe to access - auth verified
    pass
```

### Python - FastAPI

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from typing import List

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency for authentication."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = await User.get(payload["sub"])
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception

def require_roles(allowed_roles: List[str]):
    """Dependency factory for role-based access."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

async def verify_patient_access(
    patient_id: str,
    current_user: User = Depends(get_current_user)
):
    """Dependency for resource-level authorization."""
    if not await current_user.can_access_patient(patient_id):
        await AuditLog.create(
            user_id=current_user.id,
            action="unauthorized_patient_access",
            resource_id=patient_id
        )
        raise HTTPException(status_code=403, detail="Access denied to this patient")
    return current_user

# Usage
@app.get("/api/patient/{patient_id}")
async def get_patient(
    patient_id: str,
    current_user: User = Depends(verify_patient_access)
):
    # Safe to access
    pass
```

### JavaScript - Express

```javascript
const jwt = require('jsonwebtoken');

// Authentication middleware
const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = await User.findById(payload.userId);
    
    if (!req.user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Authorization middleware factory
const authorize = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    if (!allowedRoles.includes(req.user.role)) {
      AuditLog.create({
        userId: req.user.id,
        action: 'unauthorized_access',
        endpoint: req.originalUrl,
        requiredRoles: allowedRoles
      });
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    next();
  };
};

// Resource-level authorization
const verifyPatientAccess = async (req, res, next) => {
  const patientId = req.params.patientId || req.params.id;
  
  const hasAccess = await req.user.canAccessPatient(patientId);
  
  if (!hasAccess) {
    await AuditLog.create({
      userId: req.user.id,
      action: 'unauthorized_patient_access',
      patientId: patientId
    });
    return res.status(403).json({ error: 'Access denied to this patient' });
  }
  
  next();
};

// Usage
app.get('/api/patient/:patientId',
  authenticate,
  authorize('doctor', 'nurse', 'admin'),
  verifyPatientAccess,
  auditPhiAccess,
  getPatientHandler
);
```

### Java - Spring Security

```java
@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
            .authorizeRequests()
                .antMatchers("/api/patient/**").authenticated()
                .antMatchers("/api/admin/**").hasRole("ADMIN")
            .and()
            .oauth2ResourceServer()
                .jwt();
    }
}

@RestController
@RequestMapping("/api/patient")
public class PatientController {

    @GetMapping("/{patientId}")
    @PreAuthorize("hasAnyRole('DOCTOR', 'NURSE') and @patientAccessService.canAccess(#patientId)")
    @AuditPHIAccess
    public ResponseEntity<PatientDTO> getPatient(
            @PathVariable String patientId,
            @AuthenticationPrincipal UserDetails user) {
        
        Patient patient = patientService.findById(patientId);
        return ResponseEntity.ok(patientMapper.toDTO(patient, user.getRole()));
    }
}

@Service
public class PatientAccessService {
    
    public boolean canAccess(String patientId) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        User user = (User) auth.getPrincipal();
        
        // Check if user has explicit access to this patient
        boolean hasAccess = patientAssignmentRepository
            .existsByUserIdAndPatientId(user.getId(), patientId);
        
        if (!hasAccess) {
            auditService.logUnauthorizedAccess(user.getId(), patientId);
        }
        
        return hasAccess;
    }
}
```

---

## Anti-Patterns to Detect

### 1. Auth Check After PHI Access

```python
# WRONG: PHI accessed before auth check
def get_patient(patient_id):
    patient = Patient.query.get(patient_id)  # PHI already accessed!
    if not is_authenticated():
        abort(401)
    return patient
```

### 2. Auth in Business Logic Instead of Middleware

```python
# WRONG: Auth mixed with business logic
@app.route('/api/patient/<id>')
def get_patient(id):
    if request.headers.get('Authorization'):  # Weak check
        return Patient.query.get(id)
    return {'error': 'Unauthorized'}
```

### 3. Bypassable Authorization

```python
# WRONG: Role check can be bypassed with query param
@app.route('/api/patient/<id>')
@require_auth
def get_patient(id):
    if request.args.get('admin') == 'true':  # Bypassable!
        return get_full_patient(id)
    return get_limited_patient(id)
```

---

## Checklist for PHI Endpoints

- [ ] Authentication required (JWT, OAuth, Session)
- [ ] Authorization checked (role-based access)
- [ ] Resource-level access verified (user can access THIS patient)
- [ ] Auth happens BEFORE any PHI access
- [ ] Failed auth attempts are logged
- [ ] Successful PHI access is audited
- [ ] Rate limiting applied
- [ ] Token expiration enforced

---

## HIPAA Rule Mapping

| Violation | HIPAA Section | Description |
|-----------|---------------|-------------|
| No authentication | §164.312(d) | Person/entity authentication required |
| No access control | §164.312(a)(1) | Access control mechanisms required |
| No audit logging | §164.312(b) | Audit controls required |
| Bypassable auth | §164.312(a)(1) | Access controls must be effective |

---

## Risk Scoring for Auth Violations

| Issue | Base Score | Exposure Multiplier |
|-------|------------|---------------------|
| No auth on PHI endpoint | 90 | Public API: 1.1x |
| Missing role check | 75 | Admin endpoint: 1.2x |
| Bypassable auth | 85 | Internet-facing: 1.15x |
| Auth after access | 80 | High-volume endpoint: 1.1x |
