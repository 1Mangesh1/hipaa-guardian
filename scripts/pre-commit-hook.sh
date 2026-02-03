#!/bin/bash
#
# HIPAA Guardian Pre-Commit Hook
#
# Scans staged files for PHI/PII before allowing commit.
# Install: cp scripts/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#
# Exit codes:
#   0 - No PHI found, commit allowed
#   1 - High severity findings, commit blocked
#   2 - Critical findings, commit blocked
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Configuration
BLOCK_ON_HIGH=${HIPAA_BLOCK_ON_HIGH:-true}
BLOCK_ON_CRITICAL=${HIPAA_BLOCK_ON_CRITICAL:-true}
SCAN_DATA=${HIPAA_SCAN_DATA:-true}
SCAN_CODE=${HIPAA_SCAN_CODE:-true}
VERBOSE=${HIPAA_VERBOSE:-false}

echo "🔍 HIPAA Guardian Pre-Commit Scan"
echo "================================="

# Get list of staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo -e "${GREEN}✓ No files staged for commit${NC}"
    exit 0
fi

# Create temp directory for staged content
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy staged files to temp directory
for file in $STAGED_FILES; do
    if [ -f "$file" ]; then
        mkdir -p "$TEMP_DIR/$(dirname "$file")"
        git show ":$file" > "$TEMP_DIR/$file" 2>/dev/null || true
    fi
done

FINDINGS_CRITICAL=0
FINDINGS_HIGH=0
FINDINGS_MEDIUM=0
FINDINGS_LOW=0

# Function to run PHI detection
run_phi_scan() {
    local script_path="$1"
    local scan_type="$2"

    if [ -f "$script_path" ]; then
        if [ "$VERBOSE" = "true" ]; then
            echo "Running $scan_type scan..."
        fi

        output=$(python3 "$script_path" "$TEMP_DIR" --format json 2>/dev/null) || true

        if [ -n "$output" ]; then
            # Parse findings count from JSON
            local critical=$(echo "$output" | grep -o '"critical": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")
            local high=$(echo "$output" | grep -o '"high": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")
            local medium=$(echo "$output" | grep -o '"medium": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")
            local low=$(echo "$output" | grep -o '"low": [0-9]*' | head -1 | grep -o '[0-9]*' || echo "0")

            FINDINGS_CRITICAL=$((FINDINGS_CRITICAL + ${critical:-0}))
            FINDINGS_HIGH=$((FINDINGS_HIGH + ${high:-0}))
            FINDINGS_MEDIUM=$((FINDINGS_MEDIUM + ${medium:-0}))
            FINDINGS_LOW=$((FINDINGS_LOW + ${low:-0}))

            if [ "$VERBOSE" = "true" ] && [ $((critical + high + medium + low)) -gt 0 ]; then
                echo "$output" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for f in data.get('findings', [])[:5]:
        print(f\"  - {f.get('severity', 'unknown').upper()}: {f.get('file', 'unknown')}:{f.get('line', '?')}\")
except:
    pass
"
            fi
        fi
    fi
}

# Run data file scan
if [ "$SCAN_DATA" = "true" ]; then
    # Try to find detect-phi.py in various locations
    for script_loc in \
        "$SCRIPT_DIR/detect-phi.py" \
        "$(dirname "$SCRIPT_DIR")/scripts/detect-phi.py" \
        "$HOME/.claude/skills/hipaa-guardian/scripts/detect-phi.py" \
        "./scripts/detect-phi.py"
    do
        if [ -f "$script_loc" ]; then
            run_phi_scan "$script_loc" "PHI/PII data"
            break
        fi
    done
fi

# Run code scan
if [ "$SCAN_CODE" = "true" ]; then
    for script_loc in \
        "$SCRIPT_DIR/scan-code.py" \
        "$(dirname "$SCRIPT_DIR")/scripts/scan-code.py" \
        "$HOME/.claude/skills/hipaa-guardian/scripts/scan-code.py" \
        "./scripts/scan-code.py"
    do
        if [ -f "$script_loc" ]; then
            run_phi_scan "$script_loc" "code"
            break
        fi
    done
fi

# Report results
echo ""
echo "Scan Results:"
echo "-------------"

if [ $FINDINGS_CRITICAL -gt 0 ]; then
    echo -e "${RED}Critical: $FINDINGS_CRITICAL${NC}"
fi
if [ $FINDINGS_HIGH -gt 0 ]; then
    echo -e "${RED}High: $FINDINGS_HIGH${NC}"
fi
if [ $FINDINGS_MEDIUM -gt 0 ]; then
    echo -e "${YELLOW}Medium: $FINDINGS_MEDIUM${NC}"
fi
if [ $FINDINGS_LOW -gt 0 ]; then
    echo -e "${YELLOW}Low: $FINDINGS_LOW${NC}"
fi

TOTAL=$((FINDINGS_CRITICAL + FINDINGS_HIGH + FINDINGS_MEDIUM + FINDINGS_LOW))

if [ $TOTAL -eq 0 ]; then
    echo -e "${GREEN}✓ No PHI/PII detected in staged files${NC}"
    exit 0
fi

# Determine if commit should be blocked
if [ "$BLOCK_ON_CRITICAL" = "true" ] && [ $FINDINGS_CRITICAL -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ COMMIT BLOCKED: Critical PHI findings detected${NC}"
    echo ""
    echo "To bypass this check (NOT RECOMMENDED for production):"
    echo "  git commit --no-verify"
    echo ""
    echo "To review findings:"
    echo "  python3 scripts/detect-phi.py <path> --format markdown"
    exit 2
fi

if [ "$BLOCK_ON_HIGH" = "true" ] && [ $FINDINGS_HIGH -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ COMMIT BLOCKED: High severity PHI findings detected${NC}"
    echo ""
    echo "To bypass this check (NOT RECOMMENDED):"
    echo "  git commit --no-verify"
    exit 1
fi

# Warnings only
echo ""
echo -e "${YELLOW}⚠️  PHI/PII findings detected but commit allowed${NC}"
echo "Please review and remediate these findings."
exit 0
