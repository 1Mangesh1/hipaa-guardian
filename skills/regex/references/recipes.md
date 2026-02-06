# Regex Recipes

## Data Extraction

### Parse Log Files

```
# Apache/Nginx access log
^(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d{3}) (\d+)
# Groups: IP, timestamp, method, path, status, bytes

# Application log with timestamp
^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+)$
# Groups: timestamp, level, message

# Stack trace (Python)
File "([^"]+)", line (\d+), in (\w+)
```

### Parse URLs

```
# Full URL decomposition
^(https?):\/\/([^/:]+)(?::(\d+))?(\/[^?#]*)?(?:\?([^#]*))?(?:#(.*))?$
# Groups: protocol, host, port, path, query, fragment

# Extract query parameters
[?&](\w+)=([^&#]+)

# Extract file extension from URL
\.([a-zA-Z0-9]+)(?:\?|#|$)
```

### Parse Code

```
# Import statements (Python)
^(?:from\s+(\S+)\s+)?import\s+(.+)$

# Import statements (JavaScript)
^import\s+(?:(\{[^}]+\})|(\w+))(?:\s*,\s*(?:(\{[^}]+\})|(\w+)))?\s+from\s+['"]([^'"]+)['"]

# Function definitions (Python)
def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(\w+))?:

# Function definitions (JavaScript)
(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))
```

## Find & Replace Patterns

### Code Transformations

```
# Convert camelCase to snake_case
Find:    ([a-z])([A-Z])
Replace: $1_\L$2

# Convert snake_case to camelCase
Find:    _([a-z])
Replace: \U$1

# Add semicolons to line ends (JS)
Find:    ([^;{}\s])$
Replace: $1;

# Convert string concatenation to template literal
Find:    "([^"]*)" \+ (\w+) \+ "([^"]*)"
Replace: `$1${$2}$3`

# Swap function arguments
Find:    (\w+)\((\w+),\s*(\w+)\)
Replace: $1($3, $2)
```

### Cleanup Patterns

```
# Remove trailing whitespace
Find:    \s+$
Replace: (empty)

# Remove blank lines
Find:    ^\s*\n
Replace: (empty)

# Remove comments (single-line)
Find:    //.*$
Replace: (empty)

# Collapse multiple spaces
Find:    [ ]{2,}
Replace: (single space)

# Remove console.log (JavaScript)
Find:    ^\s*console\.log\([^)]*\);?\s*\n
Replace: (empty)
```

## Validation Patterns

### Strict Patterns

```
# Credit card (Luhn check requires code, but format check)
^(?:4\d{15}|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})$

# SSN (US)
^\d{3}-?\d{2}-?\d{4}$

# ZIP code (US, with optional +4)
^\d{5}(?:-\d{4})?$

# MAC address
^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$

# JWT token (structure only)
^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$

# Cron expression (5 fields)
^(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)\s+(\*|[0-9,\-\/]+)$
```

## Performance Tips

```
1. Be specific - [0-9] vs \d (same, but [0-9] clearer intent)
2. Avoid catastrophic backtracking:
   BAD:  (a+)+b      - Exponential on "aaaaaac"
   GOOD: a+b

3. Use atomic groups or possessive quantifiers when available:
   (?>a+)b            - Atomic group
   a++b               - Possessive quantifier

4. Use non-capturing groups when you don't need the match:
   (?:abc)            - vs (abc)

5. Anchor patterns when possible:
   ^pattern$          - vs pattern

6. For large inputs, prefer specific character classes:
   [^"]*              - vs .*? between quotes
```
