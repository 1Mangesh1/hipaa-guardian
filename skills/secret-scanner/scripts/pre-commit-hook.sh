#!/bin/bash
#
# Secret Scanner Pre-Commit Hook
#
# Scans staged files for hardcoded secrets before allowing commits.
# Blocks commits containing critical or high severity findings.
#
# Installation:
#   cp pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# Configuration (environment variables):
#   SECRET_SCANNER_SEVERITY=high     # Minimum severity to block (default: high)
#   SECRET_SCANNER_ALLOWLIST=path    # Path to allowlist file
#   SECRET_SCANNER_VERBOSE=true      # Show detailed output
#   SECRET_SCANNER_SKIP=true         # Skip scanning (use with caution)
#

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SEVERITY="${SECRET_SCANNER_SEVERITY:-high}"
ALLOWLIST="${SECRET_SCANNER_ALLOWLIST:-}"
VERBOSE="${SECRET_SCANNER_VERBOSE:-false}"
SKIP="${SECRET_SCANNER_SKIP:-false}"

# Banner
echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════╗"
echo "║       🔐 Secret Scanner Pre-Commit        ║"
echo "╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# Check if skip is enabled
if [ "$SKIP" = "true" ]; then
    echo -e "${YELLOW}⚠️  Secret scanning skipped (SECRET_SCANNER_SKIP=true)${NC}"
    echo -e "${YELLOW}   This is not recommended for security!${NC}"
    exit 0
fi

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find the detect-secrets.py script
SCANNER_SCRIPT=""
POSSIBLE_PATHS=(
    "$SCRIPT_DIR/../scripts/detect-secrets.py"
    "$SCRIPT_DIR/detect-secrets.py"
    "$(git rev-parse --show-toplevel)/.agents/skills/secret-scanner/scripts/detect-secrets.py"
    "$HOME/.claude/skills/secret-scanner/scripts/detect-secrets.py"
    "$HOME/.cursor/skills/secret-scanner/scripts/detect-secrets.py"
)

for path in "${POSSIBLE_PATHS[@]}"; do
    if [ -f "$path" ]; then
        SCANNER_SCRIPT="$path"
        break
    fi
done

# Fallback to inline scanning if script not found
USE_INLINE_SCAN=false
if [ -z "$SCANNER_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️  detect-secrets.py not found, using inline patterns${NC}"
    USE_INLINE_SCAN=true
fi

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR)

if [ -z "$STAGED_FILES" ]; then
    echo -e "${GREEN}✓ No files staged for commit${NC}"
    exit 0
fi

# Count files
FILE_COUNT=$(echo "$STAGED_FILES" | wc -l | tr -d ' ')
echo -e "${BLUE}Scanning $FILE_COUNT staged file(s)...${NC}"

# Create temporary directory for staged content
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Export staged files to temp directory
echo "$STAGED_FILES" | while read -r file; do
    if [ -n "$file" ]; then
        # Create directory structure
        mkdir -p "$TEMP_DIR/$(dirname "$file")"
        # Export staged version of file
        git show ":$file" > "$TEMP_DIR/$file" 2>/dev/null || true
    fi
done

FINDINGS_COUNT=0
CRITICAL_COUNT=0
HIGH_COUNT=0

if [ "$USE_INLINE_SCAN" = "true" ]; then
    # Inline secret detection patterns
    PATTERNS=(
        # AWS
        '(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'
        # GitHub
        'ghp_[A-Za-z0-9_]{36,}'
        'gho_[A-Za-z0-9_]{36,}'
        'github_pat_[A-Za-z0-9_]{22,}'
        # GitLab
        'glpat-[A-Za-z0-9_-]{20,}'
        # Stripe
        'sk_live_[A-Za-z0-9]{24,}'
        'rk_live_[A-Za-z0-9]{24,}'
        # Slack
        'xoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{24}'
        'xoxp-[0-9]{10,}-[0-9]{10,}-[0-9]{10,}-[a-f0-9]{32}'
        # SendGrid
        'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}'
        # OpenAI
        'sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}'
        'sk-proj-[A-Za-z0-9_-]{48,}'
        # Private Keys
        '-----BEGIN (RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY'
        # Database URIs with passwords
        'mongodb(\+srv)?://[^:]+:[^@]+@'
        'postgres(ql)?://[^:]+:[^@]+@'
        'mysql://[^:]+:[^@]+@'
        # npm/PyPI
        'npm_[A-Za-z0-9]{36}'
        'pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}'
        # DigitalOcean
        'dop_v1_[a-f0-9]{64}'
        # Generic passwords (be careful with false positives)
        'password["\x27]?\s*[:=]\s*["\x27][^"\x27]{8,}["\x27]'
    )

    # False positive patterns
    FALSE_POSITIVES=(
        'AKIAIOSFODNN7EXAMPLE'
        'sk_test_'
        'pk_test_'
        'EXAMPLE'
        'YOUR_API_KEY'
        'PLACEHOLDER'
        'TODO'
        'xxxx'
        'XXXX'
    )

    echo "$STAGED_FILES" | while read -r file; do
        if [ -n "$file" ] && [ -f "$TEMP_DIR/$file" ]; then
            for pattern in "${PATTERNS[@]}"; do
                matches=$(grep -nEo "$pattern" "$TEMP_DIR/$file" 2>/dev/null || true)
                if [ -n "$matches" ]; then
                    # Check for false positives
                    is_false_positive=false
                    for fp in "${FALSE_POSITIVES[@]}"; do
                        if echo "$matches" | grep -qi "$fp"; then
                            is_false_positive=true
                            break
                        fi
                    done

                    if [ "$is_false_positive" = "false" ]; then
                        echo -e "${RED}🚨 Potential secret found in: $file${NC}"
                        echo "$matches" | head -3
                        FINDINGS_COUNT=$((FINDINGS_COUNT + 1))
                        CRITICAL_COUNT=$((CRITICAL_COUNT + 1))
                    fi
                fi
            done
        fi
    done
else
    # Use the full scanner script
    SCAN_ARGS="--format json --severity $SEVERITY"

    if [ -n "$ALLOWLIST" ] && [ -f "$ALLOWLIST" ]; then
        SCAN_ARGS="$SCAN_ARGS --allowlist $ALLOWLIST"
    fi

    # Run scanner
    SCAN_OUTPUT=$(python3 "$SCANNER_SCRIPT" "$TEMP_DIR" $SCAN_ARGS 2>/dev/null || true)

    if [ -n "$SCAN_OUTPUT" ]; then
        # Parse JSON output
        FINDINGS_COUNT=$(echo "$SCAN_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('findings', [])))" 2>/dev/null || echo "0")
        CRITICAL_COUNT=$(echo "$SCAN_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len([f for f in d.get('findings', []) if f.get('severity') == 'critical']))" 2>/dev/null || echo "0")
        HIGH_COUNT=$(echo "$SCAN_OUTPUT" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len([f for f in d.get('findings', []) if f.get('severity') == 'high']))" 2>/dev/null || echo "0")

        if [ "$FINDINGS_COUNT" -gt 0 ]; then
            echo -e "${RED}🚨 Found $FINDINGS_COUNT potential secret(s)!${NC}"
            echo ""

            if [ "$VERBOSE" = "true" ]; then
                echo "$SCAN_OUTPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('findings', []):
    print(f\"  [{f['severity'].upper()}] {f['file']}:{f['line']}\")
    print(f\"    Type: {f['secret_type']}\")
    print(f\"    Provider: {f['provider']}\")
    print(f\"    Preview: {f['value_preview']}\")
    print()
" 2>/dev/null || true
            else
                echo "$SCAN_OUTPUT" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for f in data.get('findings', [])[:5]:
    print(f\"  • {f['file']}:{f['line']} - {f['secret_type']} ({f['severity']})\")
if len(data.get('findings', [])) > 5:
    print(f\"  ... and {len(data['findings']) - 5} more\")
" 2>/dev/null || true
            fi
        fi
    fi
fi

# Determine exit status
BLOCK_COMMIT=false

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    BLOCK_COMMIT=true
fi

if [ "$SEVERITY" = "high" ] && [ "$HIGH_COUNT" -gt 0 ]; then
    BLOCK_COMMIT=true
fi

if [ "$SEVERITY" = "medium" ] && [ "$FINDINGS_COUNT" -gt 0 ]; then
    BLOCK_COMMIT=true
fi

if [ "$BLOCK_COMMIT" = "true" ]; then
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         ❌ COMMIT BLOCKED                 ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Secrets detected in staged files!${NC}"
    echo ""
    echo "To fix this:"
    echo "  1. Remove the hardcoded secrets"
    echo "  2. Use environment variables instead"
    echo "  3. Add to .gitignore if appropriate"
    echo ""
    echo "To temporarily bypass (NOT RECOMMENDED):"
    echo "  git commit --no-verify"
    echo "  # or"
    echo "  SECRET_SCANNER_SKIP=true git commit"
    echo ""
    exit 1
fi

if [ "$FINDINGS_COUNT" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Potential secrets found but below blocking threshold${NC}"
    echo -e "${YELLOW}   Review the findings and address if necessary${NC}"
fi

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         ✅ Secret scan passed             ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo ""

exit 0
