# Secret Remediation Guide

Step-by-step instructions for rotating and securing leaked secrets.

## Immediate Response Checklist

When a secret is exposed:

- [ ] **1. Revoke immediately** - Don't wait, assume it's compromised
- [ ] **2. Check access logs** - Look for unauthorized usage
- [ ] **3. Generate new credentials** - Create replacement secret
- [ ] **4. Update applications** - Deploy new credentials
- [ ] **5. Remove from code** - Delete hardcoded value
- [ ] **6. Clean git history** - Remove from version control
- [ ] **7. Document incident** - Record for compliance

---

## Provider-Specific Rotation

### AWS

**Compromised: Access Key ID / Secret Access Key**

1. **Revoke the key:**
   ```
   AWS Console → IAM → Users → [Username] → Security credentials
   → Make inactive or Delete
   ```

2. **Create new key:**
   ```bash
   aws iam create-access-key --user-name <username>
   ```

3. **Check CloudTrail:**
   ```bash
   aws cloudtrail lookup-events \
     --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=AKIAEXAMPLE
   ```

4. **Update applications** with new credentials

**Best Practice:** Use IAM roles instead of access keys when possible.

---

### GitHub

**Compromised: Personal Access Token**

1. **Revoke the token:**
   ```
   GitHub → Settings → Developer settings → Personal access tokens
   → Delete the compromised token
   ```

2. **Create new token** with minimum required scopes

3. **Check security log:**
   ```
   GitHub → Settings → Security log
   ```

4. **Review repository access** and third-party applications

**Fine-grained tokens:** Prefer fine-grained PATs over classic tokens for limited scope.

---

### Stripe

**Compromised: Secret Key**

1. **Roll the key:**
   ```
   Stripe Dashboard → Developers → API keys → Roll key
   ```
   (This gives you 24 hours to update before old key expires)

2. **Check logs:**
   ```
   Stripe Dashboard → Developers → Logs
   ```

3. **Review recent transactions** for suspicious activity

4. **Update all integrations** with new key

**Note:** Test keys (`sk_test_*`) are lower risk but should still be rotated.

---

### Slack

**Compromised: Bot Token / User Token**

1. **Regenerate token:**
   ```
   Slack App Settings → OAuth & Permissions → Regenerate token
   ```

2. **Review activity:**
   - Check message history
   - Review workspace access logs (Enterprise)

3. **Update bot/application** with new token

**Webhooks:** If webhook URL is compromised, regenerate it from Incoming Webhooks settings.

---

### OpenAI

**Compromised: API Key**

1. **Delete the key:**
   ```
   OpenAI → API Keys → Delete
   ```

2. **Create new key** with appropriate permissions

3. **Check usage:**
   ```
   OpenAI → Usage → View activity
   ```

4. **Set up usage limits** to prevent abuse

---

### Database Credentials

**Compromised: Connection String with Password**

1. **Change password immediately:**
   ```sql
   -- PostgreSQL
   ALTER USER username WITH PASSWORD 'new_secure_password';

   -- MySQL
   ALTER USER 'username'@'host' IDENTIFIED BY 'new_secure_password';

   -- MongoDB
   db.changeUserPassword("username", "new_secure_password")
   ```

2. **Review database logs** for unauthorized access

3. **Check for data exfiltration:**
   - Unusual queries
   - Large data exports
   - New users created

4. **Update connection strings** in all applications

---

### Private Keys (SSH, SSL/TLS)

**Compromised: Private Key**

1. **Generate new key pair:**
   ```bash
   # SSH
   ssh-keygen -t ed25519 -C "your_email@example.com"

   # SSL/TLS
   openssl genrsa -out new_private.key 4096
   openssl req -new -key new_private.key -out new_cert.csr
   ```

2. **Replace public keys** on all servers

3. **Revoke old certificates** if applicable

4. **Update authorized_keys** files

5. **Review access logs** for unauthorized SSH sessions

---

## Cleaning Git History

### Using BFG Repo-Cleaner (Recommended)

```bash
# Install BFG
brew install bfg  # macOS
# or download from https://rtyley.github.io/bfg-repo-cleaner/

# Create a file with secrets to remove
echo "AKIAIOSFODNN7EXAMPLE" > secrets.txt
echo "sk_live_xxxxxxxxxxxxx" >> secrets.txt

# Clone a fresh copy (mirror)
git clone --mirror git@github.com:user/repo.git

# Run BFG
bfg --replace-text secrets.txt repo.git

# Clean up
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force
```

### Using git filter-branch

```bash
# Remove a specific file from history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/secret/file' \
  --prune-empty --tag-name-filter cat -- --all

# Remove a string from all files
git filter-branch --tree-filter \
  "find . -type f -exec sed -i 's/SECRET_VALUE/REDACTED/g' {} \;" \
  HEAD

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push origin --force --all
git push origin --force --tags
```

### Post-Cleanup

1. **Notify collaborators** - They need to re-clone
2. **Invalidate caches:**
   - GitHub: Contact support for cache purge
   - CI/CD: Clear build caches
3. **Update branch protections** - Re-apply if needed
4. **Verify removal:**
   ```bash
   git log -p --all -S 'SECRET_VALUE'
   ```

---

## Prevention Measures

### 1. Pre-commit Hooks

Install the secret-scanner pre-commit hook:
```bash
cp pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### 2. Environment Variables

Replace hardcoded secrets:
```python
# Bad
API_KEY = "sk_live_xxxxx"

# Good
import os
API_KEY = os.environ.get("API_KEY")
```

### 3. Secrets Managers

Use dedicated secrets management:

- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**
- **1Password Secrets Automation**

Example with AWS Secrets Manager:
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])
```

### 4. .gitignore

Always exclude sensitive files:
```gitignore
# Environment files
.env
.env.*
*.env

# Credentials
credentials.json
secrets.json
*.pem
*.key
*.p12

# Config with secrets
config.local.json
settings.local.yaml
```

### 5. CI/CD Secrets

Use platform-provided secret storage:

- **GitHub Actions:** Repository/Organization secrets
- **GitLab CI:** CI/CD Variables (masked, protected)
- **CircleCI:** Project Environment Variables
- **Jenkins:** Credentials Plugin

---

## Compliance Considerations

### Incident Documentation

Record the following:
1. Date/time of discovery
2. Type of secret exposed
3. Duration of exposure
4. Potential impact assessment
5. Remediation actions taken
6. Prevention measures implemented

### Notification Requirements

Depending on the data exposed:
- **GDPR:** 72-hour notification for personal data
- **HIPAA:** Breach notification requirements
- **PCI-DSS:** Card data breach procedures
- **SOC 2:** Incident response documentation

### Audit Trail

Maintain evidence of:
- Secret rotation timestamps
- Access log reviews
- Git history cleaning
- Updated security controls
