# PHI-Safe Logging Patterns and Filters

**HIPAA Security Rule Reference:** 45 CFR §164.312(b) - Audit Controls

---

## Overview

Logging is essential for security and debugging, but logging PHI creates serious HIPAA compliance risks. This document provides detection patterns for PHI in logs and compliant alternatives.

---

## The Problem

PHI in logs can be exposed through:
- Log aggregation systems (Splunk, ELK, CloudWatch)
- Error tracking services (Sentry, Rollbar, Bugsnag)
- APM tools (New Relic, Datadog)
- Developer access to production logs
- Log file backups
- Third-party log management

---

## Detection Patterns

### 1. Direct PHI Logging

```regex
# Python logging with PHI
(logger|logging)\.(info|debug|warning|error|critical).*\{.*patient
(logger|logging)\.(info|debug|warning|error|critical).*\b(ssn|social_security|mrn|dob|date_of_birth)\b
print\(.*patient\.

# JavaScript logging with PHI
console\.(log|info|warn|error|debug).*patient
console\.(log|info|warn|error|debug).*(ssn|mrn|dateOfBirth)

# Java logging with PHI
(log|logger)\.(info|debug|warn|error).*patient
(LOG|LOGGER)\.(info|debug|warn|error).*(ssn|mrn|dob)
```

### 2. Exception Logging with PHI

```regex
# Python exception with PHI context
logger\.exception.*patient
traceback\.format_exc.*patient
raise.*Exception.*\{.*patient

# JavaScript error with PHI
throw.*Error.*patient
console\.error.*patient.*stack
```

### 3. Structured Logging with PHI Fields

```regex
# JSON logging with PHI
"(ssn|mrn|dob|date_of_birth|social_security)":\s*"[^"]+
patient_name.*:.*"[^"]+"
```

### 4. Debug Logging with Full Objects

```regex
# Dumping full objects
logger\.(debug|info).*str\(patient\)
console\.log\(.*patient\)
pprint\(.*patient
JSON\.stringify\(patient
```

---

## PHI Patterns to Filter

```python
# Patterns that should NEVER appear in logs
PHI_LOG_PATTERNS = [
    # SSN
    r'\b\d{3}-\d{2}-\d{4}\b',
    r'\b\d{9}\b(?=.*ssn)',
    
    # MRN
    r'\b(MRN|MR#?)\s*:?\s*[A-Z0-9]{6,12}\b',
    
    # DOB
    r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b',
    r'\b(19|20)\d{2}[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b',
    
    # Email (in healthcare context)
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    
    # Phone
    r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    
    # Names (harder - context dependent)
    r'patient[_\s]?name\s*[:=]\s*["\'][^"\']+["\']',
]
```

---

## Compliant Implementation Patterns

### Python - Logging Filter

```python
import logging
import re
from typing import List, Tuple

class PHIRedactionFilter(logging.Filter):
    """
    Logging filter that redacts PHI patterns from log messages.
    
    Usage:
        logging.getLogger().addFilter(PHIRedactionFilter())
    """
    
    PHI_PATTERNS: List[Tuple[str, str]] = [
        # SSN: 123-45-6789 -> [SSN-REDACTED]
        (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]'),
        
        # DOB: Various date formats
        (r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b', 
         '[DOB-REDACTED]'),
        (r'\b(19|20)\d{2}[-/](0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])\b', 
         '[DOB-REDACTED]'),
        
        # MRN
        (r'\b(MRN|MR#?)\s*:?\s*[A-Z0-9]{6,12}\b', '[MRN-REDACTED]'),
        
        # Phone
        (r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE-REDACTED]'),
        
        # Email
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
         '[EMAIL-REDACTED]'),
    ]
    
    def __init__(self, additional_patterns: List[Tuple[str, str]] = None):
        super().__init__()
        self.patterns = self.PHI_PATTERNS.copy()
        if additional_patterns:
            self.patterns.extend(additional_patterns)
        # Compile patterns for performance
        self.compiled = [(re.compile(p, re.IGNORECASE), r) 
                         for p, r in self.patterns]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact PHI from log message and return True to allow logging."""
        if record.msg:
            msg = str(record.msg)
            for pattern, replacement in self.compiled:
                msg = pattern.sub(replacement, msg)
            record.msg = msg
        
        # Also filter args if present
        if record.args:
            args = list(record.args)
            for i, arg in enumerate(args):
                if isinstance(arg, str):
                    for pattern, replacement in self.compiled:
                        args[i] = pattern.sub(replacement, args[i])
            record.args = tuple(args)
        
        return True

# Setup
def configure_safe_logging():
    """Configure logging with PHI redaction."""
    logger = logging.getLogger()
    logger.addFilter(PHIRedactionFilter())
    
    # Also add to all handlers
    for handler in logger.handlers:
        handler.addFilter(PHIRedactionFilter())
```

### Python - Safe Logger Wrapper

```python
import hashlib
from typing import Any, Dict

class PHISafeLogger:
    """
    Wrapper around standard logger that provides safe logging methods.
    """
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.addFilter(PHIRedactionFilter())
    
    def _safe_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert PHI fields to safe representations."""
        safe_data = {}
        phi_fields = {'ssn', 'dob', 'date_of_birth', 'mrn', 'name', 
                      'patient_name', 'phone', 'email', 'address'}
        
        for key, value in data.items():
            if key.lower() in phi_fields:
                if key.lower() == 'ssn' and value:
                    safe_data[key] = f"***-**-{str(value)[-4:]}"
                else:
                    safe_data[f"{key}_hash"] = self._hash(value)
            else:
                safe_data[key] = value
        
        return safe_data
    
    def _hash(self, value: Any) -> str:
        """Create one-way hash of value for correlation without exposure."""
        return hashlib.sha256(str(value).encode()).hexdigest()[:12]
    
    def info_patient(self, message: str, patient_id: str, **extra):
        """Log patient-related info safely."""
        self.logger.info(
            f"{message} | patient_id={patient_id}",
            extra=self._safe_format(extra)
        )
    
    def error_patient(self, message: str, patient_id: str, 
                      error: Exception = None, **extra):
        """Log patient-related error safely."""
        safe_error = str(type(error).__name__) if error else None
        self.logger.error(
            f"{message} | patient_id={patient_id} | error_type={safe_error}",
            extra=self._safe_format(extra),
            exc_info=False  # Don't include traceback with PHI
        )

# Usage
safe_logger = PHISafeLogger(__name__)

# Instead of: logger.info(f"Processing {patient.name} SSN: {patient.ssn}")
safe_logger.info_patient("Processing patient", patient_id=patient.id)
```

### JavaScript/TypeScript - Pino Logger with Redaction

```typescript
import pino from 'pino';

// PHI patterns to redact
const PHI_PATTERNS = [
  { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, replacement: '[SSN-REDACTED]' },
  { pattern: /\b\d{2}\/\d{2}\/\d{4}\b/g, replacement: '[DOB-REDACTED]' },
  { pattern: /MRN:?\s*[A-Z0-9]{6,12}/gi, replacement: '[MRN-REDACTED]' },
];

function redactPHI(obj: any): any {
  if (typeof obj === 'string') {
    let result = obj;
    for (const { pattern, replacement } of PHI_PATTERNS) {
      result = result.replace(pattern, replacement);
    }
    return result;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(redactPHI);
  }
  
  if (obj && typeof obj === 'object') {
    const result: any = {};
    const phiFields = new Set(['ssn', 'dob', 'dateOfBirth', 'mrn', 'name']);
    
    for (const [key, value] of Object.entries(obj)) {
      if (phiFields.has(key.toLowerCase())) {
        result[key] = '[REDACTED]';
      } else {
        result[key] = redactPHI(value);
      }
    }
    return result;
  }
  
  return obj;
}

// Create logger with redaction
const logger = pino({
  redact: {
    paths: ['patient.ssn', 'patient.dob', 'patient.name', 'patient.mrn'],
    censor: '[REDACTED]'
  },
  hooks: {
    logMethod(inputArgs, method) {
      const redactedArgs = inputArgs.map(redactPHI);
      return method.apply(this, redactedArgs);
    }
  }
});

// Safe patient logger
const patientLogger = {
  info(message: string, patientId: string, extra: object = {}) {
    logger.info({ patientId, ...redactPHI(extra) }, message);
  },
  
  error(message: string, patientId: string, error?: Error) {
    logger.error({
      patientId,
      errorType: error?.name,
      // Don't log error.message if it might contain PHI
    }, message);
  }
};

// Usage
patientLogger.info('Patient record accessed', patient.id, {
  action: 'view',
  userId: currentUser.id
});
```

### Java - Logback Pattern Replacer

```java
// Custom converter for PHI redaction
public class PHIRedactionConverter extends ClassicConverter {
    
    private static final Pattern SSN_PATTERN = 
        Pattern.compile("\\b\\d{3}-\\d{2}-\\d{4}\\b");
    private static final Pattern DOB_PATTERN = 
        Pattern.compile("\\b\\d{2}/\\d{2}/\\d{4}\\b");
    private static final Pattern MRN_PATTERN = 
        Pattern.compile("MRN:?\\s*[A-Z0-9]{6,12}", Pattern.CASE_INSENSITIVE);
    
    @Override
    public String convert(ILoggingEvent event) {
        String message = event.getFormattedMessage();
        
        message = SSN_PATTERN.matcher(message).replaceAll("[SSN-REDACTED]");
        message = DOB_PATTERN.matcher(message).replaceAll("[DOB-REDACTED]");
        message = MRN_PATTERN.matcher(message).replaceAll("[MRN-REDACTED]");
        
        return message;
    }
}

// logback.xml configuration
/*
<configuration>
    <conversionRule conversionWord="phiSafe" 
                    converterClass="com.example.PHIRedactionConverter" />
    
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %phiSafe%n</pattern>
        </encoder>
    </appender>
</configuration>
*/

// Safe logger wrapper
@Component
public class PHISafeLogger {
    
    private final Logger logger;
    
    public PHISafeLogger(Class<?> clazz) {
        this.logger = LoggerFactory.getLogger(clazz);
    }
    
    public void infoPatient(String message, String patientId) {
        logger.info("{} | patient_id={}", message, patientId);
    }
    
    public void errorPatient(String message, String patientId, Exception e) {
        logger.error("{} | patient_id={} | error_type={}", 
            message, patientId, e.getClass().getSimpleName());
        // Do NOT log e.getMessage() if it might contain PHI
    }
}
```

---

## What TO Log vs NOT to Log

### ✅ Safe to Log

```python
# Transaction identifiers
logger.info(f"Processing transaction_id={transaction.id}")

# User actions (without PHI)
logger.info(f"User {user.id} accessed patient record {patient.id}")

# System metrics
logger.info(f"Query completed in {elapsed_ms}ms for patient_id={patient.id}")

# Error types (not messages)
logger.error(f"Validation failed for patient_id={patient.id} error_type=InvalidFormat")

# Hashed identifiers (for correlation)
logger.debug(f"Cache lookup hash={hash(patient.mrn)[:12]}")
```

### ❌ Never Log

```python
# Full names
logger.info(f"Processing patient: {patient.name}")  # BAD

# SSN
logger.debug(f"SSN validation: {ssn}")  # BAD

# Full patient objects
logger.info(f"Patient data: {patient}")  # BAD
logger.info(f"Patient data: {patient.__dict__}")  # BAD

# Error messages with PHI
logger.error(f"Failed to process: {str(e)}")  # BAD if e contains PHI

# Full request/response bodies
logger.debug(f"Request: {request.json}")  # BAD if contains PHI
```

---

## Exception Handling

### ❌ Unsafe Exception Logging

```python
try:
    process_patient(patient_data)
except Exception as e:
    logger.exception(f"Error: {e}")  # Traceback may contain PHI
    logger.error(f"Failed for {patient_data}")  # PHI in message
```

### ✅ Safe Exception Logging

```python
try:
    process_patient(patient_data)
except ValidationError as e:
    logger.error(
        f"Validation failed | patient_id={patient_data.get('id')} | "
        f"error_type={type(e).__name__} | field={e.field}"
    )
except Exception as e:
    # Log minimal info, track full error in secure system
    error_id = generate_error_id()
    secure_error_store.save(error_id, e, patient_data)  # Encrypted storage
    logger.error(
        f"Processing failed | patient_id={patient_data.get('id')} | "
        f"error_id={error_id}"
    )
```

---

## Audit Logging (What to Include)

```python
# Audit log entry structure
audit_entry = {
    "timestamp": datetime.utcnow().isoformat(),
    "user_id": current_user.id,
    "user_role": current_user.role,
    "action": "patient_record_view",
    "resource_type": "patient",
    "resource_id": patient.id,  # ID only, not PHI
    "fields_accessed": ["name", "dob", "diagnosis"],  # Field names, not values
    "ip_address": request.remote_addr,
    "user_agent": request.user_agent.string,
    "success": True,
    "session_id": session.id
}
```

---

## HIPAA Rule Mapping

| Violation | HIPAA Section | Description |
|-----------|---------------|-------------|
| PHI in application logs | §164.312(b) | Improper audit control implementation |
| PHI in error tracking | §164.530(c) | Inadequate safeguards |
| No log access control | §164.312(a)(1) | Access control required |
| PHI in third-party logs | §164.314(a) | BAA required with log vendors |

---

## Risk Scoring for Log Violations

| Issue | Base Score | Multipliers |
|-------|------------|-------------|
| SSN in logs | 95 | Cloud logs: 1.1x |
| Full patient record logged | 90 | Third-party service: 1.15x |
| PHI in error messages | 80 | Public error page: 1.2x |
| PHI in debug logs | 65 | Production: 1.1x |
