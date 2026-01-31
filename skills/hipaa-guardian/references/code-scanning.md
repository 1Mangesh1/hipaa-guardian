# Code Scanning Patterns

Detect PHI/PII leakage in source code, comments, test fixtures, and configuration files.

## Target File Types

### Source Code Files
```python
SOURCE_CODE_EXTENSIONS = [
    '.py',      # Python
    '.js',      # JavaScript
    '.ts',      # TypeScript
    '.tsx',     # TypeScript React
    '.jsx',     # JavaScript React
    '.java',    # Java
    '.cs',      # C#
    '.go',      # Go
    '.rb',      # Ruby
    '.php',     # PHP
    '.swift',   # Swift
    '.kt',      # Kotlin
    '.scala',   # Scala
    '.rs',      # Rust
    '.c',       # C
    '.cpp',     # C++
    '.h',       # C/C++ headers
]
```

### Configuration Files
```python
CONFIG_EXTENSIONS = [
    '.env',           # Environment variables
    '.env.local',
    '.env.development',
    '.env.production',
    '.yaml', '.yml',  # YAML configs
    '.json',          # JSON configs
    '.xml',           # XML configs
    '.ini',           # INI configs
    '.conf',          # Generic config
    '.properties',    # Java properties
    '.toml',          # TOML configs
]
```

### Data Files
```python
DATA_EXTENSIONS = [
    '.sql',           # SQL files
    '.csv',           # CSV data
    '.tsv',           # TSV data
    '.json',          # JSON data
    '.xml',           # XML data
    '.hl7',           # HL7 messages
    '.fhir',          # FHIR resources
]
```

### Test Files
```python
TEST_FILE_PATTERNS = [
    '*_test.*',
    '*_spec.*',
    'test_*.*',
    'spec_*.*',
    '*Test.*',
    '*Spec.*',
    '**/tests/**',
    '**/test/**',
    '**/__tests__/**',
    '**/spec/**',
    '**/fixtures/**',
    '**/testdata/**',
    '**/mock/**',
    '**/mocks/**',
]
```

---

## Detection Scenarios

### 1. Hardcoded PHI in String Literals

```python
# Python examples
PYTHON_STRING_PATTERNS = [
    # SSN in strings
    r'["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']',

    # SSN assignment
    r'(ssn|social_security|social_security_number)\s*=\s*["\'].*\d{3}-\d{2}-\d{4}.*["\']',

    # Patient data assignment
    r'(patient_name|patient_id|mrn|medical_record)\s*=\s*["\'][^"\']+["\']',

    # DOB assignment
    r'(dob|date_of_birth|birth_date|birthdate)\s*=\s*["\'][\d/\-]+["\']',
]

# JavaScript/TypeScript examples
JS_STRING_PATTERNS = [
    # const/let/var with PHI
    r'(const|let|var)\s+(ssn|socialSecurity|patientId|mrn)\s*=\s*["\'][^"\']+["\']',

    # Object property with PHI
    r'(ssn|socialSecurity|patientId|mrn|dateOfBirth)\s*:\s*["\'][^"\']+["\']',

    # Template literal with PHI
    r'`.*\$\{.*\b\d{3}-\d{2}-\d{4}\b.*\}.*`',
]

# Java examples
JAVA_STRING_PATTERNS = [
    # String assignment
    r'String\s+(ssn|patientId|mrn|socialSecurity)\s*=\s*"[^"]+"',

    # Method parameter
    r'\(\s*"[^"]*\d{3}-\d{2}-\d{4}[^"]*"\s*\)',
]
```

### 2. PHI in Comments

```python
COMMENT_PATTERNS = {
    'python': [
        # Single-line comment with SSN
        r'#.*\b\d{3}-\d{2}-\d{4}\b',

        # Docstring with patient info
        r'""".*(?:patient|ssn|mrn|dob).*"""',
        r"'''.*(?:patient|ssn|mrn|dob).*'''",

        # TODO/FIXME with PHI
        r'#\s*(TODO|FIXME|XXX|HACK).*\b\d{3}-\d{2}-\d{4}\b',
    ],

    'javascript': [
        # Single-line comment
        r'//.*\b\d{3}-\d{2}-\d{4}\b',

        # Multi-line comment
        r'/\*[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\*/',

        # JSDoc with PHI
        r'/\*\*[\s\S]*?(?:patient|ssn|mrn)[\s\S]*?\*/',
    ],

    'java': [
        # Single-line
        r'//.*\b\d{3}-\d{2}-\d{4}\b',

        # Multi-line/Javadoc
        r'/\*[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\*/',
    ],

    'sql': [
        # SQL comments
        r'--.*\b\d{3}-\d{2}-\d{4}\b',
        r'/\*[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\*/',
    ],
}
```

### 3. Test Fixtures and Mock Data

```python
TEST_DATA_PATTERNS = [
    # Fixture definitions with PHI
    r'(fixture|test_data|mock_data|sample_data)\s*=\s*\{[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\}',

    # Factory definitions
    r'(Factory|Builder)\s*\{[\s\S]*?(ssn|mrn|patient)[\s\S]*?["\'][^"\']+["\'][\s\S]*?\}',

    # Test case data
    r'(test_cases?|test_inputs?|expected)\s*=\s*\[[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\]',

    # JSON test fixtures
    r'"(ssn|mrn|patientId|socialSecurity)":\s*"[^"]+"',

    # YAML test fixtures
    r'(ssn|mrn|patient_id):\s*["\']?[^\n]+',
]
```

### 4. Database Queries and Seeds

```python
SQL_PATTERNS = [
    # INSERT with PHI
    r'INSERT\s+INTO\s+\w+.*VALUES\s*\(.*\b\d{3}-\d{2}-\d{4}\b.*\)',

    # INSERT with patient data
    r'INSERT\s+INTO\s+(patient|member|person|user)s?\s*\(.*\)\s*VALUES',

    # UPDATE with PHI
    r'UPDATE\s+\w+\s+SET.*=\s*["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']',

    # Seed data comments
    r'--\s*(seed|sample|test)\s+data[\s\S]*?\b\d{3}-\d{2}-\d{4}\b',

    # SELECT with PHI in WHERE (hardcoded value)
    r'WHERE\s+\w+\s*=\s*["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']',
]
```

### 5. Configuration Files

```python
CONFIG_PATTERNS = {
    'env': [
        # .env files with PHI
        r'^(SSN|PATIENT_ID|MRN|TEST_SSN)=.+$',
        r'^[A-Z_]+=(.*\d{3}-\d{2}-\d{4}.*)$',
    ],

    'yaml': [
        # YAML with PHI values
        r'(ssn|mrn|patient_id|social_security):\s*["\']?[^"\'\n]+',
        r':\s*["\']?\d{3}-\d{2}-\d{4}["\']?',
    ],

    'json': [
        # JSON config with PHI
        r'"(ssn|mrn|patientId|socialSecurity)":\s*"[^"]+"',
        r'"[^"]*":\s*"\d{3}-\d{2}-\d{4}"',
    ],

    'xml': [
        # XML config with PHI
        r'<(ssn|mrn|patientId)[^>]*>[^<]+</',
        r'>\d{3}-\d{2}-\d{4}<',
    ],
}
```

### 6. Logging Statements

```python
LOGGING_PATTERNS = [
    # Python logging with PHI
    r'(logger|logging)\.(debug|info|warning|error|critical)\s*\([^)]*\b\d{3}-\d{2}-\d{4}\b[^)]*\)',
    r'print\s*\([^)]*\b\d{3}-\d{2}-\d{4}\b[^)]*\)',

    # JavaScript logging
    r'console\.(log|debug|info|warn|error)\s*\([^)]*\b\d{3}-\d{2}-\d{4}\b[^)]*\)',

    # Java logging
    r'(log|logger)\.(debug|info|warn|error)\s*\([^)]*\b\d{3}-\d{2}-\d{4}\b[^)]*\)',

    # Generic logging with patient data
    r'(log|print|console|logger).*patient.*["\'][^"\']+["\']',
]
```

---

## Security Control Checks

### .gitignore Verification

```python
GITIGNORE_REQUIRED = [
    '.env',
    '.env.*',
    '*.pem',
    '*.key',
    '*.p12',
    '*.pfx',
    '*credentials*',
    '*secret*',
    '*.log',
    'logs/',
    'node_modules/',
    '__pycache__/',
    '*.pyc',
    '.idea/',
    '.vscode/',
    '*.sqlite',
    '*.db',
]

def check_gitignore(repo_path):
    """Check if .gitignore includes required patterns."""
    gitignore_path = os.path.join(repo_path, '.gitignore')
    if not os.path.exists(gitignore_path):
        return {'status': 'missing', 'missing': GITIGNORE_REQUIRED}

    with open(gitignore_path) as f:
        content = f.read()

    missing = []
    for pattern in GITIGNORE_REQUIRED:
        if pattern not in content:
            missing.append(pattern)

    return {
        'status': 'incomplete' if missing else 'complete',
        'missing': missing
    }
```

### Pre-commit Hook Detection

```python
PRECOMMIT_CHECKS = [
    # Check for pre-commit config
    '.pre-commit-config.yaml',
    '.pre-commit-config.yml',

    # Git hooks directory
    '.git/hooks/pre-commit',
    '.husky/pre-commit',
]

RECOMMENDED_HOOKS = [
    'detect-secrets',      # Secret detection
    'detect-private-key',  # Private key detection
    'check-added-large-files',
    'no-commit-to-branch',
]
```

### Secrets Management Check

```python
SECRETS_INDICATORS = {
    'good': [
        # Environment variable references
        r'os\.environ\[',
        r'process\.env\.',
        r'System\.getenv\(',
        r'ENV\[',

        # Secrets manager references
        r'(aws_secretsmanager|hashicorp_vault|azure_keyvault)',
        r'(SecretsManager|KeyVault|Vault)',

        # Config from file
        r'(config|settings)\.(get|load)',
    ],
    'bad': [
        # Hardcoded secrets
        r'(password|secret|api_key|token)\s*=\s*["\'][^"\']+["\']',
        r'(AWS_SECRET|PRIVATE_KEY)\s*=\s*["\'][^"\']+["\']',
    ],
}
```

---

## Language-Specific Patterns

### Python

```python
PYTHON_PATTERNS = {
    'string_literals': [
        r'["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']',
        r'f["\'].*\{.*ssn.*\}.*["\']',  # f-strings
    ],
    'variable_assignments': [
        r'^(\s*)(ssn|patient_id|mrn|social_security)\s*=',
        r'^(\s*)(patient|member|user)\s*=\s*\{',
    ],
    'function_args': [
        r'def\s+\w+\(.*\bssn\b.*\)',  # SSN as parameter name
        r'def\s+\w+\(.*\bpatient_id\b.*\)',
    ],
    'class_attributes': [
        r'self\.(ssn|patient_id|mrn)\s*=',
    ],
}
```

### JavaScript/TypeScript

```python
JS_PATTERNS = {
    'variable_declarations': [
        r'(const|let|var)\s+(ssn|patientId|mrn)\s*=',
        r'(const|let|var)\s+\w+\s*=\s*["\'].*\d{3}-\d{2}-\d{4}.*["\']',
    ],
    'object_properties': [
        r'\b(ssn|patientId|mrn|dateOfBirth)\s*:',
        r'["\']?(ssn|patientId|mrn)["\']?\s*:',
    ],
    'interface_definitions': [
        r'interface\s+\w+\s*\{[\s\S]*?(ssn|patientId|mrn)[\s\S]*?\}',
    ],
    'type_definitions': [
        r'type\s+\w+\s*=\s*\{[\s\S]*?(ssn|patientId|mrn)[\s\S]*?\}',
    ],
}
```

### Java

```python
JAVA_PATTERNS = {
    'field_declarations': [
        r'(private|public|protected)?\s*(String|int|long)\s+(ssn|patientId|mrn)',
        r'(private|public|protected)?\s*\w+\s+\w+\s*=\s*".*\d{3}-\d{2}-\d{4}.*"',
    ],
    'method_parameters': [
        r'(public|private|protected)?\s*\w+\s+\w+\s*\([^)]*\b(ssn|patientId)\b[^)]*\)',
    ],
    'annotations': [
        r'@\w+\([^)]*\b\d{3}-\d{2}-\d{4}\b[^)]*\)',
    ],
}
```

### SQL

```python
SQL_PATTERNS = {
    'insert_statements': [
        r'INSERT\s+INTO\s+\w+.*VALUES.*\d{3}-\d{2}-\d{4}',
        r'INSERT\s+INTO\s+(patient|member|person)',
    ],
    'update_statements': [
        r'UPDATE\s+\w+\s+SET.*\d{3}-\d{2}-\d{4}',
    ],
    'column_definitions': [
        r'(ssn|social_security|patient_id|mrn)\s+(VARCHAR|CHAR|TEXT|INT)',
    ],
    'sample_data': [
        r'--.*sample.*\d{3}-\d{2}-\d{4}',
        r'--.*test.*\d{3}-\d{2}-\d{4}',
    ],
}
```

---

## Risk Assessment for Code Findings

```python
CODE_RISK_FACTORS = {
    'location': {
        'production_code': 1.0,
        'test_code': 0.7,
        'comments': 0.6,
        'documentation': 0.5,
        'example_code': 0.4,
    },
    'exposure': {
        'public_repo': 1.0,
        'private_repo': 0.7,
        'local_only': 0.3,
    },
    'data_type': {
        'ssn': 1.0,
        'mrn': 0.9,
        'dob': 0.8,
        'name': 0.7,
        'address': 0.7,
        'phone': 0.6,
        'email': 0.6,
    },
}

def calculate_code_risk(finding):
    """Calculate risk score for code-based PHI finding."""
    base = CODE_RISK_FACTORS['data_type'].get(finding['type'], 0.5)
    location = CODE_RISK_FACTORS['location'].get(finding['location'], 0.5)
    exposure = CODE_RISK_FACTORS['exposure'].get(finding['exposure'], 0.5)

    return int((base * 0.4 + location * 0.3 + exposure * 0.3) * 100)
```

---

## Remediation Recommendations

### For Hardcoded PHI

```markdown
1. **Immediate**: Remove the hardcoded value
2. **Replace with**: Environment variable or secrets manager reference
3. **Example**:
   ```python
   # Before (BAD)
   ssn = "123-45-6789"

   # After (GOOD)
   ssn = os.environ.get('TEST_SSN')
   ```
```

### For Test Data

```markdown
1. **Use synthetic data generators**:
   - Faker library for names, addresses
   - Custom generators for format-valid but fake SSNs

2. **Example**:
   ```python
   from faker import Faker
   fake = Faker()

   test_patient = {
       'name': fake.name(),
       'ssn': fake.ssn(),  # Generates format-valid fake SSN
       'dob': fake.date_of_birth(),
   }
   ```
```

### For Comments

```markdown
1. **Remove real PHI from comments**
2. **Use placeholder format**:
   ```python
   # Example: SSN format XXX-XX-XXXX
   # NOT: Patient John Doe SSN 123-45-6789
   ```
```

### For Configuration

```markdown
1. **Never commit .env files with real data**
2. **Use .env.example with placeholder values**:
   ```
   # .env.example
   DATABASE_URL=postgres://user:pass@localhost/db
   TEST_SSN=XXX-XX-XXXX
   ```
```
