#!/usr/bin/env python3
"""
HIPAA Guardian - Authentication Gate Scanner

Scans source code for API endpoints that access PHI without proper authentication.

Usage:
    python scan-auth.py <path> [options]

Options:
    --output, -o     Output file path
    --format, -f     Output format: json, markdown (default: markdown)
    --verbose, -v    Verbose output
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


# =============================================================================
# Framework Detection Patterns
# =============================================================================

FRAMEWORK_PATTERNS = {
    'flask': {
        'extensions': ['.py'],
        'route_pattern': r'@(?:app|blueprint|bp)\.(route|get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        'auth_decorators': [
            r'@require_auth',
            r'@login_required',
            r'@jwt_required',
            r'@auth\.login_required',
            r'@token_required',
        ],
        'role_decorators': [
            r'@require_role',
            r'@roles_required',
            r'@has_role',
            r'@permission_required',
        ],
    },
    'fastapi': {
        'extensions': ['.py'],
        'route_pattern': r'@(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        'auth_decorators': [
            r'Depends\s*\(\s*(?:get_current_user|verify_token|authenticate)',
            r'Security\s*\(',
        ],
        'role_decorators': [
            r'Depends\s*\(\s*(?:require_role|check_permission|verify_access)',
        ],
    },
    'django': {
        'extensions': ['.py'],
        'route_pattern': r'path\s*\(\s*[\'"]([^\'"]+)[\'"].*?(?:views?\.|as_view)',
        'auth_decorators': [
            r'@login_required',
            r'@permission_required',
            r'IsAuthenticated',
            r'IsAdminUser',
        ],
        'role_decorators': [
            r'@user_passes_test',
            r'@permission_required',
            r'HasPermission',
        ],
    },
    'express': {
        'extensions': ['.js', '.ts', '.mjs'],
        'route_pattern': r'(?:app|router)\.(get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"``]+)[\'"`]',
        'auth_decorators': [
            r'authenticate',
            r'requireAuth',
            r'isAuthenticated',
            r'verifyToken',
            r'passport\.authenticate',
            r'jwt\(',
        ],
        'role_decorators': [
            r'authorize',
            r'requireRole',
            r'hasRole',
            r'checkPermission',
        ],
    },
    'nestjs': {
        'extensions': ['.ts'],
        'route_pattern': r'@(Get|Post|Put|Delete|Patch)\s*\(\s*[\'"]?([^\'")\s]*)[\'"]?\s*\)',
        'auth_decorators': [
            r'@UseGuards\s*\(\s*(?:AuthGuard|JwtAuthGuard)',
            r'@Auth\(',
        ],
        'role_decorators': [
            r'@Roles\s*\(',
            r'@UseGuards\s*\(\s*RolesGuard',
        ],
    },
    'spring': {
        'extensions': ['.java', '.kt'],
        'route_pattern': r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?[\'"]([^\'"]+)[\'"]',
        'auth_decorators': [
            r'@PreAuthorize',
            r'@Secured',
            r'\.authenticated\(\)',
        ],
        'role_decorators': [
            r'@RolesAllowed',
            r'hasRole\s*\(',
            r'hasAuthority\s*\(',
        ],
    },
    'go': {
        'extensions': ['.go'],
        'route_pattern': r'(?:router|r|mux)\.(GET|POST|PUT|DELETE|PATCH|Handle(?:Func)?)\s*\(\s*[\'"`]([^\'"``]+)[\'"`]',
        'auth_decorators': [
            r'AuthMiddleware',
            r'RequireAuth',
            r'JWTMiddleware',
        ],
        'role_decorators': [
            r'RequireRole',
            r'CheckPermission',
        ],
    },
}

# PHI-related route patterns
PHI_ROUTE_PATTERNS = [
    r'patient',
    r'member',
    r'health',
    r'medical',
    r'record',
    r'diagnosis',
    r'prescription',
    r'medication',
    r'treatment',
    r'appointment',
    r'visit',
    r'claim',
    r'insurance',
    r'billing',
    r'chart',
    r'lab',
    r'result',
    r'document',
    r'history',
    r'provider',
    r'caregiver',
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class AuthFinding:
    """Represents an authentication vulnerability finding."""
    id: str
    timestamp: str
    file: str
    line: int
    framework: str
    route: str
    http_method: str
    issue_type: str  # 'no_auth', 'no_role_check', 'weak_auth'
    severity: str
    risk_score: int
    phi_keywords_found: List[str]
    context: str
    remediation: List[str] = field(default_factory=list)
    hipaa_sections: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.remediation = self._get_remediation()
        self.hipaa_sections = self._get_hipaa_sections()

    def _get_remediation(self) -> List[str]:
        """Get remediation steps based on issue type."""
        base_steps = []

        if self.issue_type == 'no_auth':
            base_steps = [
                'Add authentication decorator/middleware before the route handler',
                'Verify JWT/session token before processing request',
                'Return 401 Unauthorized for unauthenticated requests',
            ]
        elif self.issue_type == 'no_role_check':
            base_steps = [
                'Add role-based access control after authentication',
                'Implement principle of least privilege',
                'Log unauthorized access attempts',
            ]
        elif self.issue_type == 'weak_auth':
            base_steps = [
                'Replace weak authentication with proper auth middleware',
                'Use established auth libraries (passport, fastapi-users, etc.)',
                'Implement proper token validation',
            ]

        # Add framework-specific guidance
        framework_guidance = {
            'flask': 'Use @login_required or @jwt_required decorators',
            'fastapi': 'Use Depends(get_current_user) dependency',
            'express': 'Use authenticate middleware before route handler',
            'spring': 'Add @PreAuthorize annotation to endpoint',
            'django': 'Use @login_required decorator or IsAuthenticated permission',
        }

        if self.framework in framework_guidance:
            base_steps.append(f'Framework hint: {framework_guidance[self.framework]}')

        return base_steps

    def _get_hipaa_sections(self) -> List[str]:
        """Get applicable HIPAA sections."""
        sections = [
            '§164.312(d) - Person or Entity Authentication',
            '§164.312(a)(1) - Access Control',
        ]
        if self.issue_type == 'no_auth':
            sections.append('§164.312(b) - Audit Controls (for logging failed access)')
        return sections


@dataclass
class AuthScanResult:
    """Container for authentication scan results."""
    findings: List[AuthFinding] = field(default_factory=list)
    files_scanned: int = 0
    routes_analyzed: int = 0
    scan_timestamp: str = ''
    scan_duration: float = 0.0

    def add_finding(self, finding: AuthFinding):
        self.findings.append(finding)

    def to_dict(self) -> dict:
        return {
            'findings': [asdict(f) for f in self.findings],
            'summary': {
                'scan_timestamp': self.scan_timestamp,
                'scan_duration_seconds': self.scan_duration,
                'files_scanned': self.files_scanned,
                'routes_analyzed': self.routes_analyzed,
                'total_findings': len(self.findings),
                'by_severity': self._count_by_severity(),
                'by_issue_type': self._count_by_issue_type(),
                'by_framework': self._count_by_framework(),
            }
        }

    def _count_by_severity(self) -> Dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_issue_type(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.issue_type] = counts.get(f.issue_type, 0) + 1
        return counts

    def _count_by_framework(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.framework] = counts.get(f.framework, 0) + 1
        return counts


# =============================================================================
# Detection Functions
# =============================================================================

def detect_framework(file_path: Path, content: str) -> Optional[str]:
    """Detect which web framework is used in the file."""
    ext = file_path.suffix.lower()

    for framework, config in FRAMEWORK_PATTERNS.items():
        if ext in config['extensions']:
            # Check for framework-specific imports/patterns
            if framework == 'flask' and re.search(r'from flask import|import flask', content, re.I):
                return 'flask'
            elif framework == 'fastapi' and re.search(r'from fastapi import|import fastapi', content, re.I):
                return 'fastapi'
            elif framework == 'django' and re.search(r'from django|import django', content, re.I):
                return 'django'
            elif framework == 'express' and re.search(r'require\s*\(\s*[\'"]express[\'"]|from\s+[\'"]express[\'"]', content, re.I):
                return 'express'
            elif framework == 'nestjs' and re.search(r'@nestjs|from\s+[\'"]@nestjs', content, re.I):
                return 'nestjs'
            elif framework == 'spring' and re.search(r'@RestController|@Controller|import org\.springframework', content, re.I):
                return 'spring'
            elif framework == 'go' and re.search(r'net/http|gorilla/mux|gin-gonic|echo', content):
                return 'go'

    return None


def find_phi_keywords_in_route(route: str) -> List[str]:
    """Find PHI-related keywords in route path."""
    found = []
    route_lower = route.lower()
    for keyword in PHI_ROUTE_PATTERNS:
        if keyword in route_lower:
            found.append(keyword)
    return found


def has_auth_decorator(content: str, line_num: int, framework: str, lines: List[str]) -> Tuple[bool, bool]:
    """Check if route has authentication decorator/middleware."""
    config = FRAMEWORK_PATTERNS.get(framework, {})
    auth_patterns = config.get('auth_decorators', [])
    role_patterns = config.get('role_decorators', [])

    # Search in lines before the route definition (decorators)
    search_start = max(0, line_num - 10)
    search_end = line_num
    search_content = '\n'.join(lines[search_start:search_end])

    # Also check the route line itself and a few lines after (for inline middleware)
    search_content += '\n' + '\n'.join(lines[line_num:min(len(lines), line_num + 5)])

    has_auth = any(re.search(pattern, search_content, re.I) for pattern in auth_patterns)
    has_role = any(re.search(pattern, search_content, re.I) for pattern in role_patterns)

    return has_auth, has_role


def get_context(lines: List[str], line_num: int, context_lines: int = 3) -> str:
    """Get context around a line."""
    start = max(0, line_num - context_lines)
    end = min(len(lines), line_num + context_lines + 1)
    context = '\n'.join(lines[start:end])
    # Truncate if too long
    if len(context) > 300:
        context = context[:300] + '...'
    return context


def calculate_risk(issue_type: str, phi_keywords: List[str], is_public_route: bool) -> Tuple[int, str]:
    """Calculate risk score and severity."""
    base_scores = {
        'no_auth': 90,
        'no_role_check': 70,
        'weak_auth': 80,
    }

    score = base_scores.get(issue_type, 70)

    # Boost for PHI keywords
    score = min(100, score + len(phi_keywords) * 2)

    # Boost for public routes (no ID parameter)
    if is_public_route:
        score = min(100, score + 5)

    if score >= 90:
        severity = 'critical'
    elif score >= 70:
        severity = 'high'
    elif score >= 50:
        severity = 'medium'
    else:
        severity = 'low'

    return score, severity


def scan_file_for_auth(file_path: Path, finding_counter: List[int]) -> List[AuthFinding]:
    """Scan a file for authentication vulnerabilities."""
    findings = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return findings

    framework = detect_framework(file_path, content)
    if not framework:
        return findings

    config = FRAMEWORK_PATTERNS[framework]
    lines = content.split('\n')

    # Find all routes
    for match in re.finditer(config['route_pattern'], content, re.I | re.M):
        route = match.group(2) if match.lastindex >= 2 else match.group(1)
        http_method = match.group(1).upper() if match.lastindex >= 2 else 'ANY'

        # Find PHI keywords in route
        phi_keywords = find_phi_keywords_in_route(route)

        # Only analyze routes with PHI-related keywords
        if not phi_keywords:
            continue

        # Find line number
        line_num = content[:match.start()].count('\n')

        # Check for auth decorators
        has_auth, has_role = has_auth_decorator(content, line_num, framework, lines)

        # Determine issue type
        issue_type = None
        if not has_auth:
            issue_type = 'no_auth'
        elif not has_role:
            issue_type = 'no_role_check'

        if issue_type:
            finding_counter[0] += 1
            is_public = ':' not in route and '<' not in route and '{' not in route
            risk_score, severity = calculate_risk(issue_type, phi_keywords, is_public)

            finding = AuthFinding(
                id=f"AUTH-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                timestamp=datetime.now().isoformat() + 'Z',
                file=str(file_path),
                line=line_num + 1,
                framework=framework,
                route=route,
                http_method=http_method,
                issue_type=issue_type,
                severity=severity,
                risk_score=risk_score,
                phi_keywords_found=phi_keywords,
                context=get_context(lines, line_num),
            )
            findings.append(finding)

    return findings


def get_source_files(path: Path) -> List[Path]:
    """Get all source files to scan."""
    files = []

    all_extensions = set()
    for config in FRAMEWORK_PATTERNS.values():
        all_extensions.update(config['extensions'])

    skip_dirs = {'node_modules', '.git', 'venv', '__pycache__', 'vendor', 'dist', 'build'}

    if path.is_file():
        return [path] if path.suffix in all_extensions else []

    for ext in all_extensions:
        for file_path in path.glob(f'**/*{ext}'):
            if not any(skip in file_path.parts for skip in skip_dirs):
                files.append(file_path)

    return files


# =============================================================================
# Output Functions
# =============================================================================

def output_json(result: AuthScanResult) -> str:
    """Format results as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def output_markdown(result: AuthScanResult) -> str:
    """Format results as Markdown."""
    lines = [
        '# Authentication Gate Scan Results\n',
        f'**Scan Time:** {result.scan_timestamp}',
        f'**Files Scanned:** {result.files_scanned}',
        f'**Routes Analyzed:** {result.routes_analyzed}',
        f'**Findings:** {len(result.findings)}\n',
        '## Summary by Severity\n',
        '| Severity | Count |',
        '|----------|-------|',
    ]

    summary = result.to_dict()['summary']
    for sev, count in summary['by_severity'].items():
        if count > 0:
            lines.append(f'| {sev.capitalize()} | {count} |')

    lines.append('\n## Findings\n')

    for f in result.findings:
        lines.extend([
            f'### {f.id} - {f.issue_type.replace("_", " ").title()}',
            f'- **Severity:** {f.severity.upper()}',
            f'- **Risk Score:** {f.risk_score}',
            f'- **Framework:** {f.framework}',
            f'- **Route:** `{f.http_method} {f.route}`',
            f'- **File:** `{f.file}:{f.line}`',
            f'- **PHI Keywords:** {", ".join(f.phi_keywords_found)}',
            '',
            '**HIPAA Sections:**',
        ])
        for section in f.hipaa_sections:
            lines.append(f'- {section}')
        lines.append('')
        lines.append('**Remediation:**')
        for step in f.remediation:
            lines.append(f'- {step}')
        lines.append('')

    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Scan code for PHI endpoints without authentication')
    parser.add_argument('path', help='Directory or file to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='markdown')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    start_time = datetime.now()
    path = Path(args.path)
    result = AuthScanResult()
    result.scan_timestamp = start_time.isoformat() + 'Z'
    finding_counter = [0]
    routes_count = 0

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    files = get_source_files(path)
    result.files_scanned = len(files)

    if args.verbose:
        print(f"Scanning {len(files)} source files...", file=sys.stderr)

    for file_path in files:
        findings = scan_file_for_auth(file_path, finding_counter)
        routes_count += len(findings)
        for f in findings:
            result.add_finding(f)

    result.routes_analyzed = routes_count
    result.scan_duration = (datetime.now() - start_time).total_seconds()

    if args.format == 'json':
        output = output_json(result)
    else:
        output = output_markdown(result)

    if args.output:
        Path(args.output).write_text(output)
        if args.verbose:
            print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    if any(f.severity == 'critical' for f in result.findings):
        sys.exit(2)
    elif any(f.severity == 'high' for f in result.findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
