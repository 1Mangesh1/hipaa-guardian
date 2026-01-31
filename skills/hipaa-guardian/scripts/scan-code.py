#!/usr/bin/env python3
"""
HIPAA Guardian - Code Scanning Script

Scans source code files for PHI/PII leakage in:
- String literals and variable assignments
- Comments and documentation
- Test fixtures and mock data
- Configuration files
- SQL statements

Usage:
    python scan-code.py <path> [options]

Options:
    --output, -o     Output file path
    --format, -f     Output format: json, markdown (default: json)
    --verbose, -v    Verbose output
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


# =============================================================================
# Code-Specific Detection Patterns
# =============================================================================

# PHI patterns for detection
PHI_PATTERNS = {
    'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
    'phone': r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
    'date': r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b',
}

# Language-specific patterns
CODE_PATTERNS = {
    'python': {
        'extensions': ['.py'],
        'string_patterns': [
            # SSN in string
            (r'["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']', 'ssn_in_string'),
            # PHI variable assignment
            (r'(ssn|social_security|patient_id|mrn|dob|date_of_birth)\s*=\s*["\'][^"\']+["\']', 'phi_assignment'),
        ],
        'comment_patterns': [
            (r'#.*\b\d{3}-\d{2}-\d{4}\b', 'ssn_in_comment'),
            (r'#.*(patient|ssn|mrn|dob).*\b\d', 'phi_in_comment'),
            (r'"""[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?"""', 'ssn_in_docstring'),
        ],
        'fixture_patterns': [
            (r'(test_data|fixture|mock|sample)\s*=\s*\{[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\}', 'phi_in_fixture'),
        ],
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.ts', '.tsx'],
        'string_patterns': [
            (r'["\'].*\b\d{3}-\d{2}-\d{4}\b.*["\']', 'ssn_in_string'),
            (r'(const|let|var)\s+(ssn|patientId|mrn)\s*=\s*["\'][^"\']+["\']', 'phi_declaration'),
            (r'(ssn|patientId|mrn|dateOfBirth)\s*:\s*["\'][^"\']+["\']', 'phi_property'),
        ],
        'comment_patterns': [
            (r'//.*\b\d{3}-\d{2}-\d{4}\b', 'ssn_in_comment'),
            (r'/\*[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\*/', 'ssn_in_block_comment'),
        ],
        'fixture_patterns': [
            (r'(testData|fixture|mock)\s*=\s*\{[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\}', 'phi_in_fixture'),
        ],
    },
    'sql': {
        'extensions': ['.sql'],
        'string_patterns': [
            (r"INSERT\s+INTO\s+\w+.*VALUES.*\b\d{3}-\d{2}-\d{4}\b", 'ssn_in_insert'),
            (r"UPDATE\s+\w+\s+SET.*\b\d{3}-\d{2}-\d{4}\b", 'ssn_in_update'),
        ],
        'comment_patterns': [
            (r'--.*\b\d{3}-\d{2}-\d{4}\b', 'ssn_in_comment'),
            (r'/\*[\s\S]*?\b\d{3}-\d{2}-\d{4}\b[\s\S]*?\*/', 'ssn_in_block_comment'),
        ],
        'fixture_patterns': [],
    },
    'config': {
        'extensions': ['.env', '.yaml', '.yml', '.json', '.xml', '.ini', '.conf'],
        'string_patterns': [
            (r'(SSN|PATIENT|MRN|TEST_SSN)\s*[=:]\s*\d{3}-\d{2}-\d{4}', 'ssn_in_config'),
            (r'(ssn|patient_id|mrn):\s*["\']?\d{3}-\d{2}-\d{4}', 'phi_in_yaml'),
            (r'"(ssn|patientId|mrn)":\s*"\d{3}-\d{2}-\d{4}"', 'phi_in_json'),
        ],
        'comment_patterns': [
            (r'#.*\b\d{3}-\d{2}-\d{4}\b', 'ssn_in_comment'),
        ],
        'fixture_patterns': [],
    },
}

# Test file patterns
TEST_FILE_PATTERNS = [
    '*_test.*', '*_spec.*', 'test_*.*', 'spec_*.*',
    '*Test.*', '*Spec.*', '*/tests/*', '*/test/*',
    '*/__tests__/*', '*/spec/*', '*/fixtures/*', '*/testdata/*',
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class CodeFinding:
    """Represents a code scanning finding."""
    id: str
    timestamp: str
    file: str
    line: int
    column: int
    finding_type: str  # string_literal, comment, fixture, config
    pattern_name: str
    language: str
    value_hash: str
    context: str
    risk_score: int
    severity: str
    is_test_file: bool
    remediation: List[str] = field(default_factory=list)
    status: str = 'open'

    def __post_init__(self):
        self.severity = self._get_severity()
        self.remediation = self._get_remediation()

    def _get_severity(self) -> str:
        """Determine severity based on risk score."""
        # Lower severity for test files
        adjusted_score = self.risk_score * 0.7 if self.is_test_file else self.risk_score

        if adjusted_score >= 90:
            return 'critical'
        elif adjusted_score >= 70:
            return 'high'
        elif adjusted_score >= 50:
            return 'medium'
        elif adjusted_score >= 25:
            return 'low'
        return 'informational'

    def _get_remediation(self) -> List[str]:
        """Get remediation steps based on finding type."""
        steps = []

        if self.finding_type == 'string_literal':
            steps = [
                'Remove hardcoded PHI value',
                'Replace with environment variable reference',
                'Use synthetic data generator (e.g., Faker library)',
            ]
        elif self.finding_type == 'comment':
            steps = [
                'Remove PHI from comment',
                'Use placeholder format (e.g., XXX-XX-XXXX)',
                'Reference documentation instead of examples',
            ]
        elif self.finding_type == 'fixture':
            steps = [
                'Replace with synthetic test data',
                'Implement data factory pattern',
                'Use Faker or similar library for test data',
            ]
        elif self.finding_type == 'config':
            steps = [
                'Remove PHI from configuration file',
                'Use environment variables for sensitive values',
                'Add file to .gitignore if test-only',
                'Implement secrets management',
            ]

        return steps


@dataclass
class CodeScanResult:
    """Container for code scan results."""
    findings: List[CodeFinding] = field(default_factory=list)
    files_scanned: int = 0
    scan_timestamp: str = ''
    scan_duration: float = 0.0
    security_controls: Dict = field(default_factory=dict)

    def add_finding(self, finding: CodeFinding):
        self.findings.append(finding)

    def to_dict(self) -> dict:
        return {
            'findings': [asdict(f) for f in self.findings],
            'summary': {
                'scan_timestamp': self.scan_timestamp,
                'scan_duration_seconds': self.scan_duration,
                'files_scanned': self.files_scanned,
                'total_findings': len(self.findings),
                'by_severity': self._count_by_severity(),
                'by_type': self._count_by_type(),
                'by_language': self._count_by_language(),
            },
            'security_controls': self.security_controls,
        }

    def _count_by_severity(self) -> Dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'informational': 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_type(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.finding_type] = counts.get(f.finding_type, 0) + 1
        return counts

    def _count_by_language(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.language] = counts.get(f.language, 0) + 1
        return counts


# =============================================================================
# Detection Functions
# =============================================================================

def hash_value(value: str) -> str:
    """Create SHA-256 hash of detected value."""
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]}"


def redact_context(context: str) -> str:
    """Redact PHI values in context string."""
    # Redact SSN
    context = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', context)
    # Redact phone
    context = re.sub(r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED-PHONE]', context)
    # Redact email (simple)
    context = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[REDACTED-EMAIL]', context)
    return context


def get_line_context(content: str, match_start: int, max_length: int = 100) -> tuple:
    """Get line number and context for a match."""
    lines_before = content[:match_start].count('\n')
    line_num = lines_before + 1

    # Get the line containing the match
    line_start = content.rfind('\n', 0, match_start) + 1
    line_end = content.find('\n', match_start)
    if line_end == -1:
        line_end = len(content)

    line_content = content[line_start:line_end]
    column = match_start - line_start + 1

    # Truncate if too long
    if len(line_content) > max_length:
        # Center around the match
        match_pos = match_start - line_start
        start = max(0, match_pos - max_length // 2)
        end = min(len(line_content), start + max_length)
        line_content = '...' + line_content[start:end] + '...'

    return line_num, column, redact_context(line_content)


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file."""
    path = Path(file_path)

    # Check common test patterns
    test_indicators = ['test', 'spec', 'fixture', 'mock', '__tests__']
    path_str = str(path).lower()

    for indicator in test_indicators:
        if indicator in path_str:
            return True

    # Check filename patterns
    name = path.stem.lower()
    if name.startswith('test_') or name.endswith('_test'):
        return True
    if name.startswith('spec_') or name.endswith('_spec'):
        return True

    return False


def get_language(file_path: str) -> str:
    """Determine language from file extension."""
    ext = Path(file_path).suffix.lower()

    for lang, config in CODE_PATTERNS.items():
        if ext in config['extensions']:
            return lang

    return 'unknown'


def calculate_risk(finding_type: str, language: str, pattern_name: str) -> int:
    """Calculate risk score for code finding."""
    base_scores = {
        'string_literal': 80,
        'comment': 60,
        'fixture': 65,
        'config': 85,
    }

    base = base_scores.get(finding_type, 70)

    # Adjust for SSN (highest risk)
    if 'ssn' in pattern_name.lower():
        base = min(100, base + 15)

    # Config files are higher risk (often committed)
    if language == 'config':
        base = min(100, base + 10)

    return base


def scan_file_for_code_phi(file_path: Path, finding_counter: List[int]) -> List[CodeFinding]:
    """Scan a source code file for PHI."""
    findings = []
    language = get_language(str(file_path))

    if language == 'unknown':
        return findings

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return findings

    config = CODE_PATTERNS.get(language, {})
    is_test = is_test_file(str(file_path))

    # Scan string patterns
    for pattern, pattern_name in config.get('string_patterns', []):
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            line_num, column, context = get_line_context(content, match.start())
            finding_counter[0] += 1

            finding = CodeFinding(
                id=f"CF-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                timestamp=datetime.now().isoformat() + 'Z',
                file=str(file_path),
                line=line_num,
                column=column,
                finding_type='string_literal',
                pattern_name=pattern_name,
                language=language,
                value_hash=hash_value(match.group()),
                context=context,
                risk_score=calculate_risk('string_literal', language, pattern_name),
                is_test_file=is_test,
            )
            findings.append(finding)

    # Scan comment patterns
    for pattern, pattern_name in config.get('comment_patterns', []):
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            line_num, column, context = get_line_context(content, match.start())
            finding_counter[0] += 1

            finding = CodeFinding(
                id=f"CF-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                timestamp=datetime.now().isoformat() + 'Z',
                file=str(file_path),
                line=line_num,
                column=column,
                finding_type='comment',
                pattern_name=pattern_name,
                language=language,
                value_hash=hash_value(match.group()),
                context=context,
                risk_score=calculate_risk('comment', language, pattern_name),
                is_test_file=is_test,
            )
            findings.append(finding)

    # Scan fixture patterns
    for pattern, pattern_name in config.get('fixture_patterns', []):
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            line_num, column, context = get_line_context(content, match.start())
            finding_counter[0] += 1

            finding = CodeFinding(
                id=f"CF-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                timestamp=datetime.now().isoformat() + 'Z',
                file=str(file_path),
                line=line_num,
                column=column,
                finding_type='fixture',
                pattern_name=pattern_name,
                language=language,
                value_hash=hash_value(match.group()),
                context=context,
                risk_score=calculate_risk('fixture', language, pattern_name),
                is_test_file=is_test,
            )
            findings.append(finding)

    return findings


def check_security_controls(path: Path) -> Dict:
    """Check for security controls in the project."""
    controls = {
        'gitignore': {'present': False, 'complete': False, 'missing': []},
        'precommit': {'present': False},
        'env_example': {'present': False},
    }

    # Check .gitignore
    gitignore = path / '.gitignore'
    if gitignore.exists():
        controls['gitignore']['present'] = True
        content = gitignore.read_text()

        required = ['.env', '*.pem', '*.key', 'credentials']
        missing = [p for p in required if p not in content]

        controls['gitignore']['complete'] = len(missing) == 0
        controls['gitignore']['missing'] = missing

    # Check pre-commit config
    precommit_files = ['.pre-commit-config.yaml', '.pre-commit-config.yml']
    for f in precommit_files:
        if (path / f).exists():
            controls['precommit']['present'] = True
            break

    # Check for .env.example
    env_example_files = ['.env.example', '.env.sample', '.env.template']
    for f in env_example_files:
        if (path / f).exists():
            controls['env_example']['present'] = True
            break

    return controls


def get_code_files(path: Path) -> List[Path]:
    """Get all source code files to scan."""
    files = []

    # Get all extensions we care about
    all_extensions = set()
    for config in CODE_PATTERNS.values():
        all_extensions.update(config['extensions'])

    # Directories to skip
    skip_dirs = {'node_modules', '.git', 'venv', '__pycache__', 'vendor', '.idea', 'dist', 'build'}

    for ext in all_extensions:
        pattern = f'**/*{ext}'
        for file_path in path.glob(pattern):
            # Skip excluded directories
            if any(skip in file_path.parts for skip in skip_dirs):
                continue
            files.append(file_path)

    return files


# =============================================================================
# Output Functions
# =============================================================================

def output_json(result: CodeScanResult) -> str:
    """Format results as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def output_markdown(result: CodeScanResult) -> str:
    """Format results as Markdown."""
    lines = [
        '# Code Scanning Results\n',
        f'**Scan Time:** {result.scan_timestamp}',
        f'**Files Scanned:** {result.files_scanned}',
        f'**Total Findings:** {len(result.findings)}\n',
        '## Summary\n',
        '| Severity | Count |',
        '|----------|-------|',
    ]

    summary = result.to_dict()['summary']
    for sev, count in summary['by_severity'].items():
        if count > 0:
            lines.append(f'| {sev.capitalize()} | {count} |')

    lines.append('\n## Security Controls\n')
    controls = result.security_controls

    if controls.get('gitignore', {}).get('present'):
        status = '✓' if controls['gitignore'].get('complete') else '⚠️'
        lines.append(f'- {status} `.gitignore` present')
        if controls['gitignore'].get('missing'):
            lines.append(f'  - Missing: {", ".join(controls["gitignore"]["missing"])}')
    else:
        lines.append('- ✗ `.gitignore` not found')

    if controls.get('precommit', {}).get('present'):
        lines.append('- ✓ Pre-commit config present')
    else:
        lines.append('- ✗ No pre-commit hooks configured')

    lines.append('\n## Findings\n')

    for f in result.findings:
        test_badge = ' (test file)' if f.is_test_file else ''
        lines.extend([
            f'### {f.id} - {f.finding_type}{test_badge}',
            f'- **Severity:** {f.severity.upper()}',
            f'- **File:** `{f.file}:{f.line}`',
            f'- **Language:** {f.language}',
            f'- **Pattern:** {f.pattern_name}',
            f'- **Context:** `{f.context}`',
            '',
            '**Remediation:**',
        ])
        for step in f.remediation:
            lines.append(f'- {step}')
        lines.append('')

    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Scan source code for PHI leakage')
    parser.add_argument('path', help='Directory to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'],
                        default='json', help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Initialize
    start_time = datetime.now()
    path = Path(args.path)
    result = CodeScanResult()
    result.scan_timestamp = start_time.isoformat() + 'Z'
    finding_counter = [0]

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    # Get files
    files = get_code_files(path)
    result.files_scanned = len(files)

    if args.verbose:
        print(f"Scanning {len(files)} code files...", file=sys.stderr)

    # Scan files
    for file_path in files:
        findings = scan_file_for_code_phi(file_path, finding_counter)
        for f in findings:
            result.add_finding(f)

    # Check security controls
    result.security_controls = check_security_controls(path)

    # Calculate duration
    result.scan_duration = (datetime.now() - start_time).total_seconds()

    # Format output
    if args.format == 'json':
        output = output_json(result)
    else:
        output = output_markdown(result)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        if args.verbose:
            print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit code based on findings
    if any(f.severity == 'critical' for f in result.findings):
        sys.exit(2)
    elif any(f.severity == 'high' for f in result.findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
