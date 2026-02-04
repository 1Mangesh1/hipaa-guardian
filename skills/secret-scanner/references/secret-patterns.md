# Secret Detection Patterns

Comprehensive regex patterns for detecting secrets across 50+ providers.

## Pattern Categories

### 1. Cloud Provider Credentials

#### AWS

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Access Key ID | `(?:A3T[A-Z0-9]\|AKIA\|AGPA\|AIDA\|AROA\|AIPA\|ANPA\|ANVA\|ASIA)[A-Z0-9]{16}` | Critical | Starts with AKIA for long-term keys |
| Secret Access Key | `(?i)aws[_\-\.]?secret[_\-\.]?(?:access)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9/+=]{40}[\'"]` | Critical | 40-char base64 |
| Session Token | `(?i)aws[_\-\.]?session[_\-\.]?token[\'"\s]*[:=]\s*[\'"][A-Za-z0-9/+=]{100,}[\'"]` | High | Temporary credentials |
| MWS Auth Token | `amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` | High | Marketplace Web Service |

**Example AWS Key:**
```
AKIAIOSFODNN7EXAMPLE (this is AWS's documented example key)
```

#### GCP

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `AIza[0-9A-Za-z_-]{35}` | High | Always starts with AIza |
| Service Account | `"type"\s*:\s*"service_account"` | Critical | JSON key file indicator |
| OAuth Client ID | `[0-9]+-[a-z0-9]+\.apps\.googleusercontent\.com` | Medium | Client ID format |

#### Azure

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Storage Account Key | `(?i)(?:DefaultEndpointsProtocol\|AccountKey)\s*=\s*[A-Za-z0-9+/=]{86,88}` | Critical | Base64 encoded |
| Connection String | `(?i)(?:Server\|Data\s+Source)=[^;]+;.*(?:Password\|PWD)=[^;]+` | Critical | SQL with credentials |
| SAS Token | `(?i)[?&]sig=[A-Za-z0-9%+/=]{43,}` | High | Shared Access Signature |
| Subscription Key | `(?i)(?:Ocp-Apim-Subscription-Key)[\'"\s]*[:=]\s*[\'"][a-f0-9]{32}[\'"]` | High | API Management |

### 2. Code Platform Tokens

#### GitHub

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Personal Access Token | `ghp_[A-Za-z0-9_]{36,255}` | Critical | Classic PAT |
| Fine-grained PAT | `github_pat_[A-Za-z0-9_]{22,255}` | Critical | New format |
| OAuth Access Token | `gho_[A-Za-z0-9_]{36,255}` | Critical | OAuth token |
| User-to-Server Token | `ghu_[A-Za-z0-9_]{36,255}` | Critical | GitHub App |
| Server-to-Server Token | `ghs_[A-Za-z0-9_]{36,255}` | Critical | GitHub App |
| Refresh Token | `ghr_[A-Za-z0-9_]{36,255}` | Critical | Refresh token |

#### GitLab

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Personal Access Token | `glpat-[A-Za-z0-9_-]{20,}` | Critical | PAT format |
| Pipeline Trigger Token | `glptt-[A-Za-z0-9_-]{20,}` | High | CI/CD trigger |
| Runner Registration | `GR1348941[A-Za-z0-9_-]{20,}` | High | Runner token |
| CI Job Token | `glcbt-[A-Za-z0-9_-]{20,}` | Medium | Temporary |

#### Bitbucket

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| App Password | `(?i)bitbucket[_\-\.]?(?:app)?[_\-\.]?password[\'"\s]*[:=]\s*[\'"][A-Za-z0-9]{20,}[\'"]` | Critical | App-specific |
| OAuth Token | `(?i)bitbucket[_\-\.]?(?:oauth)?[_\-\.]?token[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_-]{20,}[\'"]` | Critical | OAuth |

### 3. Package Registries

#### npm

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Auth Token | `npm_[A-Za-z0-9]{36}` | Critical | Publish access |
| Legacy Token | `(?i)//registry\.npmjs\.org/:_authToken=[A-Za-z0-9_-]+` | Critical | .npmrc format |

#### PyPI

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Token | `pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}` | Critical | Always this prefix |

#### RubyGems

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `rubygems_[a-f0-9]{48}` | Critical | Gem publish |

### 4. Payment Providers

#### Stripe

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Live Secret Key | `sk_live_[A-Za-z0-9]{24,}` | Critical | Production |
| Test Secret Key | `sk_test_[A-Za-z0-9]{24,}` | Medium | Test mode |
| Live Restricted Key | `rk_live_[A-Za-z0-9]{24,}` | High | Limited access |
| Live Publishable Key | `pk_live_[A-Za-z0-9]{24,}` | Low | Public key |

#### PayPal

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Client Secret | `(?i)paypal[_\-\.]?(?:client)?[_\-\.]?secret[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_-]{40,}[\'"]` | Critical | OAuth secret |
| Access Token | `A21AA[A-Za-z0-9_-]+` | High | API token |

#### Square

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Access Token | `sq0atp-[A-Za-z0-9_-]{22}` | Critical | API access |
| Application Secret | `sq0csp-[A-Za-z0-9_-]{43}` | Critical | OAuth secret |

### 5. Communication Services

#### Twilio

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Account SID | `AC[a-f0-9]{32}` | Medium | Account identifier |
| Auth Token | `(?i)twilio[_\-\.]?(?:auth)?[_\-\.]?token[\'"\s]*[:=]\s*[\'"][a-f0-9]{32}[\'"]` | Critical | Full access |
| API Key | `SK[a-f0-9]{32}` | High | Standard API key |
| API Key Secret | `(?i)twilio[_\-\.]?(?:api)?[_\-\.]?secret[\'"\s]*[:=]\s*[\'"][A-Za-z0-9]{32}[\'"]` | Critical | API key secret |

#### SendGrid

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}` | Critical | Full access |

#### Mailchimp

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `[a-f0-9]{32}-us[0-9]{1,2}` | High | Includes datacenter |

#### Slack

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Bot Token | `xoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24}` | Critical | Bot access |
| User Token | `xoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[a-f0-9]{32}` | Critical | User access |
| App Token | `xapp-[0-9]-[A-Z0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{64}` | Critical | App-level |
| Webhook URL | `https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24}` | High | Incoming webhook |

#### Discord

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Bot Token | `[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}` | Critical | Bot authentication |
| Webhook URL | `https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+` | High | Webhook |

### 6. AI Services

#### OpenAI

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key (Legacy) | `sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}` | Critical | Old format |
| Project API Key | `sk-proj-[A-Za-z0-9_-]{48,}` | Critical | New format |
| Organization API Key | `sk-org-[A-Za-z0-9_-]{48,}` | Critical | Org-level |

#### Anthropic

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `sk-ant-api[0-9]{2}-[A-Za-z0-9_-]{93}` | Critical | Claude API |

#### Cohere

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| API Key | `(?i)cohere[_\-\.]?(?:api)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9]{40}[\'"]` | Critical | API access |

### 7. Databases

#### MongoDB

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Connection String | `mongodb(?:\+srv)?://[^:]+:[^@]+@[^/\s]+` | Critical | With password |

#### PostgreSQL

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Connection String | `postgres(?:ql)?://[^:]+:[^@]+@[^/\s]+` | Critical | With password |

#### MySQL

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Connection String | `mysql://[^:]+:[^@]+@[^/\s]+` | Critical | With password |

#### Redis

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Connection String | `redis://[^:]*:[^@]+@[^/\s]+` | High | With password |
| Auth Password | `(?i)redis[_\-\.]?(?:auth)?[_\-\.]?password[\'"\s]*[:=]\s*[\'"][^\'"]+[\'"]` | High | Password only |

### 8. Cryptographic Keys

#### Private Keys

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| RSA Private Key | `-----BEGIN RSA PRIVATE KEY-----` | Critical | Unencrypted |
| OpenSSH Private Key | `-----BEGIN OPENSSH PRIVATE KEY-----` | Critical | SSH key |
| EC Private Key | `-----BEGIN EC PRIVATE KEY-----` | Critical | Elliptic curve |
| DSA Private Key | `-----BEGIN DSA PRIVATE KEY-----` | Critical | DSA key |
| PGP Private Key | `-----BEGIN PGP PRIVATE KEY BLOCK-----` | Critical | PGP/GPG |
| PKCS8 Private Key | `-----BEGIN PRIVATE KEY-----` | Critical | PKCS#8 format |
| Encrypted Private Key | `-----BEGIN ENCRYPTED PRIVATE KEY-----` | High | Encrypted |

### 9. Generic Patterns

| Pattern Name | Regex | Severity | Notes |
|--------------|-------|----------|-------|
| Generic API Key | `(?i)(?:api[_\-\.]?key\|apikey)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]` | Medium | Variable name context |
| Generic Secret | `(?i)(?:secret\|client[_\-\.]?secret)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]` | Medium | Secret variable |
| Generic Token | `(?i)(?:token\|bearer\|auth[_\-\.]?token)[\'"\s]*[:=]\s*[\'"][A-Za-z0-9_\-\.]{20,}[\'"]` | Medium | Token variable |
| Generic Password | `(?i)(?:password\|passwd\|pwd)[\'"\s]*[:=]\s*[\'"][^\'"]{8,}[\'"]` | High | Hardcoded password |
| Basic Auth | `(?i)authorization[\'"\s]*[:=]\s*[\'"]Basic\s+[A-Za-z0-9+/=]{20,}[\'"]` | High | Base64 credentials |
| Bearer Token | `(?i)authorization[\'"\s]*[:=]\s*[\'"]Bearer\s+[A-Za-z0-9_\-\.]{20,}[\'"]` | High | Bearer header |
| JWT Token | `eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}` | Medium | JSON Web Token |

## Known False Positives

### Example/Placeholder Values

```
# AWS
AKIAIOSFODNN7EXAMPLE

# Stripe
sk_test_PLACEHOLDER_VALUE_HERE
pk_test_PLACEHOLDER_VALUE_HERE

# Slack
xoxb-PLACEHOLDER-EXAMPLE-TOKEN

# Generic
YOUR_API_KEY_HERE
REPLACE_ME
PLACEHOLDER
TODO_REPLACE
example_key
fake_secret
mock_token
test_password
dummy_value
```

### Common Patterns to Exclude

```regex
# Version numbers that look like tokens
v[0-9]+\.[0-9]+\.[0-9]+

# UUIDs (usually not secrets)
[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}

# Git commit hashes
[0-9a-f]{40}

# Base64 encoded public data
data:image/[a-z]+;base64,

# CSS/HTML color codes
#[0-9A-Fa-f]{6}
```

## Entropy-Based Detection

For strings not matching known patterns, use Shannon entropy analysis:

```python
import math
from collections import Counter

def shannon_entropy(s):
    if not s:
        return 0
    counts = Counter(s)
    length = len(s)
    return -sum((c/length) * math.log2(c/length) for c in counts.values())

# Thresholds:
# > 4.5 with length >= 20: Likely secret
# > 5.0 with length >= 16: High probability
# > 5.5: Very high probability
```

## Context Boosters

Increase confidence when secret-like strings appear near:

```
key, secret, token, password, passwd, pwd, auth, credential,
api_key, apikey, access_key, private_key, client_secret,
bearer, authorization, authenticate, encrypt, decrypt
```

## File Type Priorities

### High Priority
- `.env`, `.env.*`
- `*.pem`, `*.key`, `*.p12`
- `credentials.*`, `secrets.*`
- `config.json`, `settings.json`

### Medium Priority
- Source code: `.py`, `.js`, `.ts`, `.java`, `.go`
- Config: `.yaml`, `.yml`, `.toml`, `.ini`
- Infrastructure: `.tf`, `.tfvars`

### Lower Priority
- Documentation: `.md`, `.rst`, `.txt`
- Test files: `*_test.*`, `test_*.*`
- Examples: `example.*`, `sample.*`
