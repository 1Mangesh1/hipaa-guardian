#!/bin/bash
#
# HIPAA Guardian - Security Controls Validation Script
#
# Validates security controls in a project directory:
# - .gitignore configuration
# - Pre-commit hooks
# - Secrets management
# - File permissions
#
# Usage:
#   ./validate-controls.sh [directory]
#
# Exit codes:
#   0 - All controls pass
#   1 - Some controls need attention
#   2 - Critical controls missing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default to current directory
TARGET_DIR="${1:-.}"

# Counters
PASS=0
WARN=0
FAIL=0

# Output functions
pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

info() {
    echo -e "  $1"
}

header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════"
    echo " $1"
    echo "═══════════════════════════════════════════════════════════"
}

# =============================================================================
# Check Functions
# =============================================================================

check_gitignore() {
    header "Checking .gitignore"

    local gitignore="$TARGET_DIR/.gitignore"

    if [[ ! -f "$gitignore" ]]; then
        fail ".gitignore file not found"
        info "Create a .gitignore file to prevent committing sensitive files"
        return
    fi

    pass ".gitignore file exists"

    # Required patterns
    local required_patterns=(
        ".env"
        "*.pem"
        "*.key"
        "*.p12"
    )

    # Recommended patterns
    local recommended_patterns=(
        ".env.*"
        "*credentials*"
        "*secret*"
        "*.log"
        "node_modules"
        "__pycache__"
        "venv"
        ".idea"
        ".vscode"
    )

    # Check required patterns
    for pattern in "${required_patterns[@]}"; do
        if grep -q "$pattern" "$gitignore" 2>/dev/null; then
            pass "Required pattern '$pattern' present"
        else
            fail "Required pattern '$pattern' missing"
        fi
    done

    # Check recommended patterns
    for pattern in "${recommended_patterns[@]}"; do
        if grep -q "$pattern" "$gitignore" 2>/dev/null; then
            pass "Recommended pattern '$pattern' present"
        else
            warn "Recommended pattern '$pattern' missing"
        fi
    done
}

check_precommit() {
    header "Checking Pre-commit Hooks"

    local precommit_config=""
    local precommit_files=(
        ".pre-commit-config.yaml"
        ".pre-commit-config.yml"
    )

    for f in "${precommit_files[@]}"; do
        if [[ -f "$TARGET_DIR/$f" ]]; then
            precommit_config="$TARGET_DIR/$f"
            break
        fi
    done

    if [[ -n "$precommit_config" ]]; then
        pass "Pre-commit config found: $precommit_config"

        # Check for security-related hooks
        if grep -q "detect-secrets" "$precommit_config" 2>/dev/null; then
            pass "detect-secrets hook configured"
        else
            warn "detect-secrets hook not configured"
            info "Consider adding: https://github.com/Yelp/detect-secrets"
        fi

        if grep -q "detect-private-key" "$precommit_config" 2>/dev/null; then
            pass "detect-private-key hook configured"
        else
            warn "detect-private-key hook not configured"
        fi
    else
        warn "No pre-commit config found"
        info "Install pre-commit: pip install pre-commit"
        info "Create .pre-commit-config.yaml with security hooks"
    fi

    # Check git hooks directory
    local hooks_dir="$TARGET_DIR/.git/hooks"
    if [[ -d "$hooks_dir" ]]; then
        if [[ -x "$hooks_dir/pre-commit" ]]; then
            pass "Git pre-commit hook is executable"
        else
            warn "Git pre-commit hook not set up"
            info "Run: pre-commit install"
        fi
    fi

    # Check for husky (npm projects)
    if [[ -d "$TARGET_DIR/.husky" ]]; then
        pass "Husky hooks directory found"
        if [[ -f "$TARGET_DIR/.husky/pre-commit" ]]; then
            pass "Husky pre-commit hook configured"
        fi
    fi
}

check_env_files() {
    header "Checking Environment Files"

    # Find all .env files
    local env_files
    env_files=$(find "$TARGET_DIR" -name ".env*" -type f 2>/dev/null | grep -v node_modules | grep -v venv || true)

    if [[ -z "$env_files" ]]; then
        info "No .env files found"
        return
    fi

    for env_file in $env_files; do
        local relative_path="${env_file#$TARGET_DIR/}"
        info "Found: $relative_path"

        # Check if it contains sensitive patterns
        if grep -qiE "(password|secret|key|token|ssn|api_key)" "$env_file" 2>/dev/null; then
            warn "  Contains potentially sensitive variables"
        fi

        # Check if .env.example exists
        local example_file="${env_file}.example"
        if [[ ! -f "$example_file" ]] && [[ "$env_file" == *".env" ]] && [[ "$env_file" != *".example" ]]; then
            warn "  No .env.example counterpart found"
            info "  Create $relative_path.example with placeholder values"
        fi
    done

    # Check if .env is in git
    if [[ -d "$TARGET_DIR/.git" ]]; then
        if git -C "$TARGET_DIR" ls-files --cached | grep -q "^\.env$" 2>/dev/null; then
            fail ".env is tracked in git!"
            info "Remove with: git rm --cached .env"
        else
            pass ".env is not tracked in git"
        fi
    fi
}

check_secrets_in_code() {
    header "Checking for Hardcoded Secrets"

    # Patterns that might indicate hardcoded secrets
    local secret_patterns=(
        'password\s*=\s*["\x27][^"\x27]+'
        'api_key\s*=\s*["\x27][^"\x27]+'
        'secret\s*=\s*["\x27][^"\x27]+'
        'token\s*=\s*["\x27][^"\x27]+'
        'AWS_SECRET'
        'PRIVATE_KEY'
    )

    local found_secrets=0

    for pattern in "${secret_patterns[@]}"; do
        local matches
        matches=$(grep -rniE "$pattern" "$TARGET_DIR" \
            --include="*.py" \
            --include="*.js" \
            --include="*.ts" \
            --include="*.java" \
            --include="*.go" \
            --exclude-dir=node_modules \
            --exclude-dir=venv \
            --exclude-dir=.git \
            2>/dev/null | head -5 || true)

        if [[ -n "$matches" ]]; then
            ((found_secrets++))
            warn "Potential hardcoded secret pattern found"
            echo "$matches" | while read -r line; do
                info "  $line"
            done
        fi
    done

    if [[ $found_secrets -eq 0 ]]; then
        pass "No obvious hardcoded secrets detected"
    fi
}

check_file_permissions() {
    header "Checking File Permissions"

    # Check for overly permissive files
    local sensitive_patterns=(
        "*.pem"
        "*.key"
        "*.p12"
        "*credentials*"
        "*secret*"
    )

    for pattern in "${sensitive_patterns[@]}"; do
        local files
        files=$(find "$TARGET_DIR" -name "$pattern" -type f 2>/dev/null | grep -v node_modules || true)

        for file in $files; do
            local perms
            perms=$(stat -f "%Lp" "$file" 2>/dev/null || stat -c "%a" "$file" 2>/dev/null)

            if [[ "$perms" =~ [0-7][4-7][4-7] ]]; then
                warn "File may be too permissive: $file (permissions: $perms)"
                info "  Consider: chmod 600 $file"
            fi
        done
    done

    pass "File permission check complete"
}

check_docker_security() {
    header "Checking Docker Security"

    local dockerfile="$TARGET_DIR/Dockerfile"
    local compose_file=""

    # Check for docker-compose files
    for f in "docker-compose.yml" "docker-compose.yaml" "compose.yml" "compose.yaml"; do
        if [[ -f "$TARGET_DIR/$f" ]]; then
            compose_file="$TARGET_DIR/$f"
            break
        fi
    done

    if [[ -f "$dockerfile" ]]; then
        pass "Dockerfile found"

        # Check for secrets in Dockerfile
        if grep -qiE "(password|secret|key|token)" "$dockerfile" 2>/dev/null; then
            warn "Dockerfile may contain sensitive values"
            info "Use build args or runtime environment variables instead"
        fi

        # Check for .dockerignore
        if [[ -f "$TARGET_DIR/.dockerignore" ]]; then
            pass ".dockerignore exists"

            if grep -q ".env" "$TARGET_DIR/.dockerignore"; then
                pass ".env excluded from Docker context"
            else
                warn ".env not excluded in .dockerignore"
            fi
        else
            warn ".dockerignore not found"
            info "Create .dockerignore to exclude sensitive files from build context"
        fi
    else
        info "No Dockerfile found"
    fi

    if [[ -n "$compose_file" ]]; then
        pass "Docker Compose file found"

        # Check for hardcoded secrets in compose file
        if grep -qiE "password:|secret:|api_key:" "$compose_file" 2>/dev/null; then
            if ! grep -q "secrets:" "$compose_file" 2>/dev/null; then
                warn "Compose file may contain hardcoded secrets"
                info "Consider using Docker secrets or environment files"
            fi
        fi
    fi
}

# =============================================================================
# Main
# =============================================================================

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║         HIPAA Guardian - Security Controls Check          ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Target directory: $TARGET_DIR"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"

    # Verify target directory exists
    if [[ ! -d "$TARGET_DIR" ]]; then
        echo -e "${RED}Error: Directory not found: $TARGET_DIR${NC}"
        exit 2
    fi

    # Run checks
    check_gitignore
    check_precommit
    check_env_files
    check_secrets_in_code
    check_file_permissions
    check_docker_security

    # Summary
    header "Summary"
    echo -e "${GREEN}Passed:${NC}  $PASS"
    echo -e "${YELLOW}Warnings:${NC} $WARN"
    echo -e "${RED}Failed:${NC}  $FAIL"
    echo ""

    # Exit code
    if [[ $FAIL -gt 0 ]]; then
        echo -e "${RED}Critical security controls need attention.${NC}"
        exit 2
    elif [[ $WARN -gt 0 ]]; then
        echo -e "${YELLOW}Some security controls could be improved.${NC}"
        exit 1
    else
        echo -e "${GREEN}All security controls passed!${NC}"
        exit 0
    fi
}

main
