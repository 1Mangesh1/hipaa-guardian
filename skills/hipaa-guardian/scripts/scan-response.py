#!/usr/bin/env python3
"""
HIPAA Guardian - API Response Scanner

Scans source code for API responses that may expose unmasked PHI.

Usage:
    python scan-response.py <path> [options]

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
# API Response Detection Patterns
# =============================================================================

RESPONSE_PATTERNS = {
    'python': {
        'extensions': ['.py'],
        'response_patterns': [
            # Flask/FastAPI JSON responses
            (r'return\s+jsonify\s*\(\s*([^)]+)\s*\)', 'flask_jsonify'),
            (r'return\s+JSONResponse\s*\(\s*content\s*=\s*([^)]+)\s*\)', 'fastapi_json'),
            (r'return\s+\{[^}]*patient[^}]*\}', 'dict_return'),
            (r'\.to_dict\s*\(\s*\)', 'to_dict'),
            (r'\.model_dump\s*\(\s*\)', 'pydantic_dump'),
            (r'\.dict\s*\(\s*\)', 'pydantic_dict'),
        ],
        'phi_fields': [
            r'\bssn\b', r'\bsocial_security\b',
            r'\bpatient\.name\b', r'\bpatient\.ssn\b', r'\bpatient\.dob\b',
            r'\bmrn\b', r'\bmedical_record\b',
            r'\bdiagnosis\b', r'\bdiagnoses\b',
            r'\bmedication\b', r'\bprescription\b',
            r'\bdate_of_birth\b', r'\bbirth_date\b',
        ],
    },
    'javascript': {
        'extensions': ['.js', '.ts', '.jsx', '.tsx'],
        'response_patterns': [
            # Express/Node responses
            (r'res\.json\s*\(\s*([^)]+)\s*\)', 'express_json'),
            (r'res\.send\s*\(\s*JSON\.stringify\s*\(\s*([^)]+)\s*\)\s*\)', 'express_send'),
            (r'return\s+NextResponse\.json\s*\(\s*([^)]+)\s*\)', 'nextjs_response'),
            (r'ctx\.body\s*=\s*([^;]+)', 'koa_body'),
            # GraphQL resolvers
            (r'resolve[r]?\s*:\s*\([^)]*\)\s*=>\s*\{[^}]*patient[^}]*\}', 'graphql_resolver'),
        ],
        'phi_fields': [
            r'\bssn\b', r'\bsocialSecurity\b',
            r'\bpatient\.name\b', r'\bpatient\.ssn\b', r'\bpatient\.dob\b',
            r'\bpatientName\b', r'\bdateOfBirth\b',
            r'\bmrn\b', r'\bmedicalRecord\b',
            r'\bdiagnosis\b', r'\bmedication\b',
        ],
    },
    'java': {
        'extensions': ['.java'],
        'response_patterns': [
            (r'ResponseEntity\.ok\s*\(\s*([^)]+)\s*\)', 'spring_response'),
            (r'return\s+new\s+ResponseEntity\s*<[^>]*>\s*\(\s*([^)]+)\s*,', 'response_entity'),
            (r'return\s+patient\s*;', 'direct_return'),
        ],
        'phi_fields': [
            r'\.getSsn\(\)', r'\.getSSN\(\)',
            r'\.getName\(\)', r'\.getPatientName\(\)',
            r'\.getDateOfBirth\(\)', r'\.getDob\(\)',
            r'\.getDiagnosis\(\)', r'\.getMedication\(\)',
            r'\.getMrn\(\)', r'\.getMedicalRecordNumber\(\)',
        ],
    },
    'csharp': {
        'extensions': ['.cs'],
        'response_patterns': [
            (r'return\s+Ok\s*\(\s*([^)]+)\s*\)', 'aspnet_ok'),
            (r'return\s+Json\s*\(\s*([^)]+)\s*\)', 'aspnet_json'),
            (r'return\s+new\s+JsonResult\s*\(\s*([^)]+)\s*\)', 'json_result'),
        ],
        'phi_fields': [
            r'\.Ssn\b', r'\.SSN\b',
            r'\.Name\b', r'\.PatientName\b',
            r'\.DateOfBirth\b', r'\.Dob\b',
            r'\.Diagnosis\b', r'\.Medication\b',
            r'\.Mrn\b', r'\.MedicalRecordNumber\b',
        ],
    },
    'go': {
        'extensions': ['.go'],
        'response_patterns': [
            (r'json\.NewEncoder\([^)]+\)\.Encode\s*\(\s*([^)]+)\s*\)', 'go_encode'),
            (r'c\.JSON\s*\([^,]+,\s*([^)]+)\s*\)', 'gin_json'),
            (r'json\.Marshal\s*\(\s*([^)]+)\s*\)', 'marshal'),
        ],
        'phi_fields': [
            r'\.SSN\b', r'\.Ssn\b',
            r'\.Name\b', r'\.PatientName\b',
            r'\.DOB\b', r'\.DateOfBirth\b',
            r'\.Diagnosis\b', r'\.Medication\b',
            r'\.MRN\b', r'\.MedicalRecordNumber\b',
        ],
    },
}

# Masking patterns (safe)
MASKING_PATTERNS = [
    r'mask\w*\s*\(',
    r'redact\w*\s*\(',
    r'sanitize\w*\s*\(',
    r'filter\w*PHI\s*\(',
    r'\.select\s*\(',  # Selecting specific fields
    r'exclude\s*=',
    r'\.only\s*\(',
    r'toSafeJson',
    r'safeSerialize',
]


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ResponseFinding:
    """Represents an API response PHI exposure finding."""
    id: str
    timestamp: str
    file: str
    line: int
    language: str
    response_type: str
    phi_fields_exposed: List[str]
    risk_score: int
    severity: str
    context: str
    remediation: List[str] = field(default_factory=list)
    hipaa_sections: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.remediation = self._get_remediation()
        self.hipaa_sections = [
            '§164.502(b) - Minimum Necessary',
            '§164.312(a)(1) - Access Control',
            '§164.312(e)(1) - Transmission Security',
        ]

    def _get_remediation(self) -> List[str]:
        """Get remediation steps."""
        return [
            'Apply field-level masking before returning response',
            'Use DTOs/View Models that exclude PHI fields',
            'Implement role-based field visibility',
            'Return only minimum necessary data',
            'Add field-level audit logging',
            f'Exposed fields to address: {", ".join(self.phi_fields_exposed)}',
        ]


@dataclass
class ResponseScanResult:
    """Container for API response scan results."""
    findings: List[ResponseFinding] = field(default_factory=list)
    files_scanned: int = 0
    responses_analyzed: int = 0
    scan_timestamp: str = ''
    scan_duration: float = 0.0

    def add_finding(self, finding: ResponseFinding):
        self.findings.append(finding)

    def to_dict(self) -> dict:
        return {
            'findings': [asdict(f) for f in self.findings],
            'summary': {
                'scan_timestamp': self.scan_timestamp,
                'scan_duration_seconds': self.scan_duration,
                'files_scanned': self.files_scanned,
                'responses_analyzed': self.responses_analyzed,
                'total_findings': len(self.findings),
                'by_severity': self._count_by_severity(),
                'by_language': self._count_by_language(),
            }
        }

    def _count_by_severity(self) -> Dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_language(self) -> Dict:
        counts = {}
        for f in self.findings:
            counts[f.language] = counts.get(f.language, 0) + 1
        return counts


# =============================================================================
# Detection Functions
# =============================================================================

def get_language(file_path: Path) -> str:
    """Determine language from file extension."""
    ext = file_path.suffix.lower()
    for lang, config in RESPONSE_PATTERNS.items():
        if ext in config['extensions']:
            return lang
    return 'unknown'


def has_masking(content: str, start: int, end: int) -> bool:
    """Check if response has masking applied."""
    # Check a window around the response
    window_start = max(0, start - 200)
    window_end = min(len(content), end + 100)
    window = content[window_start:window_end]

    for pattern in MASKING_PATTERNS:
        if re.search(pattern, window, re.I):
            return True
    return False


def find_phi_fields(content: str, phi_patterns: List[str]) -> List[str]:
    """Find PHI fields in response content."""
    found = []
    for pattern in phi_patterns:
        if re.search(pattern, content, re.I):
            # Extract field name
            match = re.search(pattern, content, re.I)
            if match:
                found.append(match.group().strip('.()'))
    return list(set(found))


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

    # Redact any PHI patterns
    context = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', context)

    return line_num, context


def calculate_risk(phi_fields: List[str]) -> Tuple[int, str]:
    """Calculate risk score based on PHI fields exposed."""
    high_risk_fields = ['ssn', 'social_security', 'socialSecurity', 'getSsn']
    medium_risk_fields = ['name', 'dob', 'dateOfBirth', 'diagnosis', 'medication', 'mrn']

    score = 50  # Base score for any response

    for field in phi_fields:
        field_lower = field.lower()
        if any(h in field_lower for h in ['ssn', 'social']):
            score += 30
        elif any(m in field_lower for m in ['name', 'dob', 'birth', 'diagnosis', 'medication', 'mrn']):
            score += 15
        else:
            score += 10

    score = min(100, score)

    if score >= 90:
        severity = 'critical'
    elif score >= 70:
        severity = 'high'
    elif score >= 50:
        severity = 'medium'
    else:
        severity = 'low'

    return score, severity


def scan_file_for_response_phi(file_path: Path, finding_counter: List[int]) -> Tuple[List[ResponseFinding], int]:
    """Scan a file for PHI exposure in API responses."""
    findings = []
    response_count = 0

    language = get_language(file_path)
    if language == 'unknown':
        return findings, 0

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return findings, 0

    config = RESPONSE_PATTERNS[language]

    for pattern, response_type in config['response_patterns']:
        for match in re.finditer(pattern, content, re.I | re.M):
            response_count += 1

            # Get the response content
            response_content = match.group(1) if match.lastindex else match.group()

            # Check if masking is applied
            if has_masking(content, match.start(), match.end()):
                continue

            # Find PHI fields
            phi_fields = find_phi_fields(response_content, config['phi_fields'])

            # Also check surrounding context for PHI fields
            context_start = max(0, match.start() - 500)
            context_end = min(len(content), match.end() + 200)
            context_content = content[context_start:context_end]
            phi_fields.extend(find_phi_fields(context_content, config['phi_fields']))
            phi_fields = list(set(phi_fields))

            if phi_fields:
                finding_counter[0] += 1
                line_num, context = get_line_info(content, match.start())
                risk_score, severity = calculate_risk(phi_fields)

                finding = ResponseFinding(
                    id=f"RESP-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}",
                    timestamp=datetime.now().isoformat() + 'Z',
                    file=str(file_path),
                    line=line_num,
                    language=language,
                    response_type=response_type,
                    phi_fields_exposed=phi_fields,
                    risk_score=risk_score,
                    severity=severity,
                    context=context,
                )
                findings.append(finding)

    return findings, response_count


def get_source_files(path: Path) -> List[Path]:
    """Get all source files to scan."""
    files = []

    all_extensions = set()
    for config in RESPONSE_PATTERNS.values():
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

def output_json(result: ResponseScanResult) -> str:
    """Format results as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def output_markdown(result: ResponseScanResult) -> str:
    """Format results as Markdown."""
    lines = [
        '# API Response PHI Exposure Scan\n',
        f'**Scan Time:** {result.scan_timestamp}',
        f'**Files Scanned:** {result.files_scanned}',
        f'**API Responses Analyzed:** {result.responses_analyzed}',
        f'**PHI Exposure Findings:** {len(result.findings)}\n',
    ]

    if not result.findings:
        lines.append('No unmasked PHI detected in API responses.\n')
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

    lines.append('\n## Findings\n')

    for f in result.findings:
        lines.extend([
            f'### {f.id} - {f.response_type}',
            f'- **Severity:** {f.severity.upper()}',
            f'- **Risk Score:** {f.risk_score}',
            f'- **Language:** {f.language}',
            f'- **File:** `{f.file}:{f.line}`',
            f'- **PHI Fields:** `{", ".join(f.phi_fields_exposed)}`',
            f'- **Context:** `{f.context}`',
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

    # Add safe response patterns
    lines.extend([
        '---\n',
        '## Safe Response Patterns\n',
        '```python',
        '# Use field selection',
        'return jsonify({',
        '    "id": patient.id,',
        '    "name": mask_name(patient.name),',
        '    "dob": None  # Exclude sensitive fields',
        '})',
        '',
        '# Use DTOs/View Models',
        'return PatientSummaryDTO.from_orm(patient)',
        '',
        '# Apply role-based visibility',
        'return jsonify(patient.to_safe_dict(user_role=current_user.role))',
        '```',
    ])

    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Scan API responses for PHI exposure')
    parser.add_argument('path', help='Directory or file to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='markdown')
    parser.add_argument('--verbose', '-v', action='store_true')

    args = parser.parse_args()

    start_time = datetime.now()
    path = Path(args.path)
    result = ResponseScanResult()
    result.scan_timestamp = start_time.isoformat() + 'Z'
    finding_counter = [0]
    total_responses = 0

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    files = get_source_files(path)
    result.files_scanned = len(files)

    if args.verbose:
        print(f"Scanning {len(files)} source files...", file=sys.stderr)

    for file_path in files:
        findings, response_count = scan_file_for_response_phi(file_path, finding_counter)
        total_responses += response_count
        for f in findings:
            result.add_finding(f)

    result.responses_analyzed = total_responses
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
