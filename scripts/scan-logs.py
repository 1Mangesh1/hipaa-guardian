#!/usr/bin/env python3
"""
HIPAA Guardian - Log Safety Scanner

Scans source code for PHI leakage in logging statements.

Usage:
    python scan-logs.py <path> [options]

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
from typing import List, Dict, Tuple


# =============================================================================
# Logging Pattern Detection
# =============================================================================

# Logging function patterns by language
LOGGING_PATTERNS = {
    'python': {
        'extensions': ['.py'],
        'log_functions': [
            r'(logger|logging|log)\.(debug|info|warning|warn|error|critical|exception)\s*\(',
            r'print\s*\(',
        ],
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.ts', '.tsx', '.mjs'],
        'log_functions': [
            r'console\.(log|debug|info|warn|error)\s*\(',
            r'(logger|log)\.(debug|info|warn|error|trace)\s*\(',
            r'winston\.(debug|info|warn|error)\s*\(',
            r'bunyan\.(debug|info|warn|error)\s*\(',
        ],
    },
    'java': {
        'extensions': ['.java'],
        'log_functions': [
            r'(logger|log|LOG)\.(debug|info|warn|error|trace)\s*\(',
            r'System\.(out|err)\.print(ln)?\s*\(',
        ],
    },
    'csharp': {
        'extensions': ['.cs'],
        'log_functions': [
            r'(logger|_logger|Logger)\.(Log|Debug|Info|Warning|Error)\s*\(',
            r'Console\.Write(Line)?\s*\(',
            r'Debug\.Write(Line)?\s*\(',
        ],
    },
    'go': {
        'extensions': ['.go'],
        'log_functions': [
            r'(log|logger)\.(Print|Printf|Println|Debug|Info|Warn|Error|Fatal)\s*\(',
            r'fmt\.(Print|Printf|Println)\s*\(',
        ],
    },
    'ruby': {
        'extensions': ['.rb'],
        'log_functions': [
            r'(logger|Rails\.logger)\.(debug|info|warn|error|fatal)\s*[\(\s]',
            r'puts\s+',
        ],
    },
}

# PHI patterns to detect in log statements
PHI_IN_LOG_PATTERNS = [
    # Direct PHI values
    (r'\b(ssn|social_security)\b', 'ssn', 'Social Security Number'),
    (r'\b(patient\.?name|patient_name|patientName)\b', 'patient_name', 'Patient Name'),
    (r'\b(mrn|medical_record|medicalRecord)\b', 'mrn', 'Medical Record Number'),
    (r'\b(dob|date_of_birth|dateOfBirth|birthDate|birth_date)\b', 'dob', 'Date of Birth'),
    (r'\b(diagnosis|diagnoses)\b', 'diagnosis', 'Diagnosis'),
    (r'\b(treatment|medication|prescription)\b', 'treatment', 'Treatment/Medication'),
    (r'\b(address|street|city|zip)\b', 'address', 'Address'),
    (r'\b(phone|telephone|mobile|cell)\b', 'phone', 'Phone Number'),
    (r'\b(email)\b', 'email', 'Email Address'),

    # Object dumps (high risk)
    (r'(patient|member|subscriber|record)\s*[=:]\s*', 'object_dump', 'PHI Object Reference'),
    (r'\.to_dict\(\)|\.toJSON\(\)|JSON\.stringify\s*\(\s*(patient|member|record)', 'serialization', 'PHI Serialization'),

    # String interpolation with PHI
    (r'f["\'].*\{.*patient.*\}', 'f_string', 'F-string with Patient Data'),
    (r'\$\{.*patient.*\}', 'template_literal', 'Template Literal with Patient Data'),
    (r'%s.*patient|patient.*%s', 'format_string', 'Format String with Patient Data'),

    # Exception logging with PHI context
    (r'exception.*patient|patient.*exception', 'exception_phi', 'Exception with Patient Context'),
    (r'error.*patient|patient.*error', 'error_phi', 'Error with Patient Context'),
]

# Safe logging patterns (allowlist)
SAFE_PATTERNS = [
    r'patient_id\s*=\s*["\']?[a-f0-9-]+["\']?',  # Just the ID
    r'patient\.id\b',  # Just accessing ID
    r'\[REDACTED\]',
    r'\*{3,}',  # Masked values
    r'hash\(|sha256|md5',  # Hashing
    r'mask\(|redact\(',  # Masking functions
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class LogFinding:
    """Represents a PHI-in-log finding."""
    id: str
    timestamp: str
    file: str
    line: int
    language: str
    log_function: str
    phi_type: str
    phi_description: str
    risk_score: int
    severity: str
    context: str
    remediation: List[str] = field(default_factory=list)
    hipaa_sections: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.remediation = self._get_remediation()
        self.hipaa_sections = ['§164.312(b) - Audit Controls', '§164.530(c) - Safeguards']

    def _get_remediation(self) -> List[str]:
        """Get remediation steps based on PHI type."""
        common_steps = [
            'Remove PHI value from log statement',
            'Log only non-sensitive identifiers (e.g., patient_id)',
            'Implement a PHI filter for your logging framework',
        ]

        type_specific = {
            'ssn': ['CRITICAL: Never log SSN - use hash or last 4 digits only'],
            'patient_name': ['Log patient ID instead of name'],
            'object_dump': ['Select specific non-PHI fields to log instead of full object'],
            'serialization': ['Create a safe serialization method that excludes PHI fields'],
            'exception_phi': ['Sanitize exception messages before logging'],
            'f_string': ['Replace PHI variables with IDs or hashed values'],
        }

        steps = type_specific.get(self.phi_type, []) + common_steps
        return steps


@dataclass
class LogScanResult:
    """Container for log scan results."""
    findings: List[LogFinding] = field(default_factory=list)
    files_scanned: int = 0
    log_statements_analyzed: int = 0
    scan_timestamp: str = ''
    scan_duration: float = 0.0

    def add_finding(self, finding: LogFinding):
        self.findings.append(finding)

    def to_dict(self) -> dict:
        return {
            'findings': [asdict(f) for f in self.findings],
            'summary': {
                'scan_timestamp': self.scan_timestamp,
                'scan_duration_seconds': self.scan_duration,
                'files_scanned': self.files_scanned,
                'log_statements_analyzed': self.log_statements_analyzed,
                'total_findings': len(self.findings),
                'by_severity': self._count_by_severity(),
                'by_phi_type': self._count_by_phi_type(),
            }
        }

    def _count_by_severity(self) -> Dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_phi_type(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.phi_type] = counts.get(f.phi_type, 0) + 1
        return counts


# =============================================================================
# Detection Functions
# =============================================================================

def get_language(file_path: Path) -> str:
    """Determine language from file extension."""
    ext = file_path.suffix.lower()
    for lang, config in LOGGING_PATTERNS.items():
        if ext in config['extensions']:
            return lang
    return 'unknown'


def is_safe_logging(log_content: str) -> bool:
    """Check if log statement uses safe patterns."""
    for pattern in SAFE_PATTERNS:
        if re.search(pattern, log_content, re.I):
            return True
    return False


def extract_log_content(content: str, match_start: int) -> Tuple[str, int]:
    """Extract the full log statement content."""
    # Find the opening parenthesis
    paren_start = content.find('(', match_start)
    if paren_start == -1:
        return '', 0

    # Count parentheses to find the end
    depth = 1
    pos = paren_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '(':
            depth += 1
        elif content[pos] == ')':
            depth -= 1
        pos += 1

    log_content = content[paren_start + 1:pos - 1]
    return log_content, pos


def get_line_info(content: str, pos: int) -> Tuple[int, str]:
    """Get line number and context for a position."""
    line_num = content[:pos].count('\n') + 1
    line_start = content.rfind('\n', 0, pos) + 1
    line_end = content.find('\n', pos)
    if line_end == -1:
        line_end = len(content)

    context = content[line_start:line_end].strip()
    if len(context) > 150:
        context = context[:150] + '...'

    return line_num, context


def calculate_risk(phi_type: str) -> Tuple[int, str]:
    """Calculate risk score and severity for PHI type."""
    risk_scores = {
        'ssn': 100,
        'patient_name': 80,
        'mrn': 85,
        'dob': 75,
        'diagnosis': 90,
        'treatment': 85,
        'address': 70,
        'phone': 65,
        'email': 60,
        'object_dump': 95,
        'serialization': 90,
        'f_string': 80,
        'template_literal': 80,
        'format_string': 80,
        'exception_phi': 85,
        'error_phi': 80,
    }

    score = risk_scores.get(phi_type, 70)

    if score >= 90:
        severity = 'critical'
    elif score >= 70:
        severity = 'high'
    elif score >= 50:
        severity = 'medium'
    else:
        severity = 'low'

    return score, severity


def scan_file_for_log_phi(file_path: Path, finding_counter: List[int]) -> Tuple[List[LogFinding], int]:
    """Scan a file for PHI in logging statements."""
    findings = []
    log_count = 0

    language = get_language(file_path)
    if language == 'unknown':
        return findings, 0

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return findings, 0

    config = LOGGING_PATTERNS[language]

    # Find all log statements
    for log_pattern in config['log_functions']:
        for match in re.finditer(log_pattern, content, re.I):
            log_count += 1
            log_content, end_pos = extract_log_content(content, match.start())

            if not log_content:
                continue

            # Skip if using safe patterns
            if is_safe_logging(log_content):
                continue

            # Check for PHI patterns
            for phi_pattern, phi_type, phi_desc in PHI_IN_LOG_PATTERNS:
                if re.search(phi_pattern, log_content, re.I):
                    finding_counter[0] += 1
                    line_num, context = get_line_info(content, match.start())
                    risk_score, severity = calculate_risk(phi_type)

                    # Redact any actual PHI patterns in context
                    context = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN-REDACTED]', context)
                    context = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL-REDACTED]', context)

                    finding = LogFinding(
                        id=f"LOG-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                        timestamp=datetime.now().isoformat() + 'Z',
                        file=str(file_path),
                        line=line_num,
                        language=language,
                        log_function=match.group().rstrip('('),
                        phi_type=phi_type,
                        phi_description=phi_desc,
                        risk_score=risk_score,
                        severity=severity,
                        context=context,
                    )
                    findings.append(finding)
                    break  # Only report once per log statement

    return findings, log_count


def get_source_files(path: Path) -> List[Path]:
    """Get all source files to scan."""
    files = []

    all_extensions = set()
    for config in LOGGING_PATTERNS.values():
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

def output_json(result: LogScanResult) -> str:
    """Format results as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def output_markdown(result: LogScanResult) -> str:
    """Format results as Markdown."""
    lines = [
        '# Log Safety Scan Results\n',
        f'**Scan Time:** {result.scan_timestamp}',
        f'**Files Scanned:** {result.files_scanned}',
        f'**Log Statements Analyzed:** {result.log_statements_analyzed}',
        f'**PHI Leakage Findings:** {len(result.findings)}\n',
    ]

    if not result.findings:
        lines.append('No PHI detected in logging statements.\n')
        return '\n'.join(lines)

    lines.extend([
        '## Summary by Severity\n',
        '| Severity | Count |',
        '|----------|-------|',
    ])

    summary = result.to_dict()['summary']
    for sev, count in summary['by_severity'].items():
        if count > 0:
            lines.append(f'| {sev.capitalize()} | {count} |')

    lines.append('\n## PHI Types Found\n')
    lines.append('| PHI Type | Count |')
    lines.append('|----------|-------|')
    for phi_type, count in summary['by_phi_type'].items():
        lines.append(f'| {phi_type} | {count} |')

    lines.append('\n## Findings\n')

    for f in result.findings:
        lines.extend([
            f'### {f.id} - {f.phi_description}',
            f'- **Severity:** {f.severity.upper()}',
            f'- **Risk Score:** {f.risk_score}',
            f'- **Language:** {f.language}',
            f'- **File:** `{f.file}:{f.line}`',
            f'- **Log Function:** `{f.log_function}`',
            f'- **Context:** `{f.context}`',
            '',
            '**Remediation:**',
        ])
        for step in f.remediation:
            lines.append(f'- {step}')
        lines.append('')

    # Add safe logging patterns guidance
    lines.extend([
        '---\n',
        '## Safe Logging Patterns\n',
        'Use these patterns instead of logging PHI directly:\n',
        '```python',
        '# Instead of:',
        'logger.info(f"Processing patient: {patient.name}, SSN: {patient.ssn}")',
        '',
        '# Use:',
        'logger.info(f"Processing patient_id={patient.id}")',
        '',
        '# Or implement a PHI filter:',
        'class PHIFilter(logging.Filter):',
        '    def filter(self, record):',
        '        record.msg = redact_phi(str(record.msg))',
        '        return True',
        '```',
    ])

    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Scan code for PHI in logging statements')
    parser.add_argument('path', help='Directory or file to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='markdown')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    start_time = datetime.now()
    path = Path(args.path)
    result = LogScanResult()
    result.scan_timestamp = start_time.isoformat() + 'Z'
    finding_counter = [0]
    total_log_statements = 0

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    files = get_source_files(path)
    result.files_scanned = len(files)

    if args.verbose:
        print(f"Scanning {len(files)} source files...", file=sys.stderr)

    for file_path in files:
        findings, log_count = scan_file_for_log_phi(file_path, finding_counter)
        total_log_statements += log_count
        for f in findings:
            result.add_finding(f)

    result.log_statements_analyzed = total_log_statements
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
