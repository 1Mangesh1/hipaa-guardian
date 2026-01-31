#!/usr/bin/env python3
"""
HIPAA Guardian - PHI Detection Script

Scans files for Protected Health Information (PHI) and Personally Identifiable
Information (PII) based on the 18 HIPAA Safe Harbor identifiers.

Usage:
    python detect-phi.py <path> [options]

Options:
    --output, -o     Output file path (default: stdout)
    --format, -f     Output format: json, csv, markdown (default: json)
    --severity, -s   Minimum severity: low, medium, high, critical
    --include        File patterns to include (glob)
    --exclude        File patterns to exclude (glob)
    --synthetic      Treat all findings as synthetic/test data
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
from typing import Optional


# =============================================================================
# Detection Patterns
# =============================================================================

PATTERNS = {
    'ssn': {
        'name': 'Social Security Number',
        'patterns': [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'standard'),
            (r'\b\d{3}\s\d{2}\s\d{4}\b', 'spaces'),
            (r'(?i)\b(SSN|Social\s*Security)\s*[:#]?\s*\d{3}[-\s]?\d{2}[-\s]?\d{4}\b', 'labeled'),
        ],
        'sensitivity': 100,
        'classification': 'PHI',
    },
    'mrn': {
        'name': 'Medical Record Number',
        'patterns': [
            (r'(?i)\b(MRN|MR#?|Medical\s*Record)\s*[:#]?\s*[A-Z]?\d{5,12}\b', 'labeled'),
            (r'(?i)\b(Patient\s*ID|PID|PAT#?)\s*[:#]?\s*[A-Z]?\d{5,12}\b', 'patient_id'),
        ],
        'sensitivity': 80,
        'classification': 'PHI',
    },
    'dob': {
        'name': 'Date of Birth',
        'patterns': [
            (r'(?i)\b(DOB|Date\s*of\s*Birth|Birth\s*Date)\s*[:#]?\s*[\d/\-]+\b', 'labeled'),
            (r'\b(0?[1-9]|1[0-2])[-/](0?[1-9]|[12]\d|3[01])[-/](19|20)\d{2}\b', 'mm_dd_yyyy'),
            (r'\b(19|20)\d{2}-(0?[1-9]|1[0-2])-(0?[1-9]|[12]\d|3[01])\b', 'iso'),
        ],
        'sensitivity': 85,
        'classification': 'PHI',
    },
    'phone': {
        'name': 'Phone Number',
        'patterns': [
            (r'\b\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b', 'parentheses'),
            (r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', 'dashes'),
            (r'(?i)\b(Phone|Tel|Mobile|Cell)\s*[:#]?\s*[\d\s\-().+]{10,}\b', 'labeled'),
        ],
        'sensitivity': 60,
        'classification': 'PII',
    },
    'fax': {
        'name': 'Fax Number',
        'patterns': [
            (r'(?i)\b(Fax|Facsimile)\s*[:#]?\s*[\d\s\-().+]{10,}\b', 'labeled'),
        ],
        'sensitivity': 60,
        'classification': 'PII',
    },
    'email': {
        'name': 'Email Address',
        'patterns': [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', 'standard'),
        ],
        'sensitivity': 55,
        'classification': 'PII',
    },
    'address': {
        'name': 'Physical Address',
        'patterns': [
            (r'\b\d+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)*\s+(Street|St\.?|Avenue|Ave\.?|Road|Rd\.?|Boulevard|Blvd\.?|Drive|Dr\.?|Lane|Ln\.?|Way|Court|Ct\.?)\b', 'street'),
            (r'(?i)\b(P\.?\s*O\.?\s*Box)\s*\d+\b', 'po_box'),
        ],
        'sensitivity': 70,
        'classification': 'PII',
    },
    'zip': {
        'name': 'ZIP Code',
        'patterns': [
            (r'\b\d{5}-\d{4}\b', 'zip_plus_4'),
            (r'(?i)\b(ZIP|Zip\s*Code)\s*[:#]?\s*\d{5}(-\d{4})?\b', 'labeled'),
        ],
        'sensitivity': 35,
        'classification': 'PII',
    },
    'health_plan_id': {
        'name': 'Health Plan ID',
        'patterns': [
            (r'(?i)\b(Member|Subscriber|Insurance|Policy)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{6,15}\b', 'labeled'),
            (r'(?i)\b(Medicare|Medicaid)\s*(ID|#|Number)\s*[:#]?\s*[A-Z0-9]{8,12}\b', 'government'),
        ],
        'sensitivity': 75,
        'classification': 'PHI',
    },
    'account_number': {
        'name': 'Account Number',
        'patterns': [
            (r'(?i)\b(Account|Acct)\s*(#|Number)?\s*[:#]?\s*\d{8,17}\b', 'generic'),
            (r'\b4[0-9]{12}(?:[0-9]{3})?\b', 'visa'),
            (r'\b5[1-5][0-9]{14}\b', 'mastercard'),
            (r'\b3[47][0-9]{13}\b', 'amex'),
        ],
        'sensitivity': 95,
        'classification': 'PII',
    },
    'license': {
        'name': 'License Number',
        'patterns': [
            (r"(?i)\b(Driver'?s?\s*License|DL|DLN)\s*[:#]?\s*[A-Z0-9]{5,15}\b", 'drivers'),
            (r'(?i)\b(DEA)\s*[:#]?\s*[A-Z]{2}\d{7}\b', 'dea'),
            (r'(?i)\b(NPI)\s*[:#]?\s*\d{10}\b', 'npi'),
        ],
        'sensitivity': 70,
        'classification': 'PII',
    },
    'device_id': {
        'name': 'Device Identifier',
        'patterns': [
            (r'(?i)\b(Serial|SN|S/N)\s*[:#]?\s*[A-Z0-9]{6,20}\b', 'serial'),
            (r'\b[A-HJ-NPR-Z0-9]{17}\b', 'vin'),
        ],
        'sensitivity': 65,
        'classification': 'PII',
    },
    'ip_address': {
        'name': 'IP Address',
        'patterns': [
            (r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', 'ipv4'),
        ],
        'sensitivity': 50,
        'classification': 'PII',
    },
    'url': {
        'name': 'URL',
        'patterns': [
            (r'\bhttps?://[A-Za-z0-9.-]+/(?:patient|member|user|account)/[A-Za-z0-9]+\b', 'with_id'),
        ],
        'sensitivity': 40,
        'classification': 'PII',
    },
    'biometric': {
        'name': 'Biometric Identifier',
        'patterns': [
            (r'(?i)\b(Fingerprint|Biometric)\s*(ID|Template|Data)\s*[:#]?\s*[A-Z0-9-]+\b', 'labeled'),
        ],
        'sensitivity': 95,
        'classification': 'PHI',
    },
}

# Exclusion patterns to reduce false positives
EXCLUSIONS = {
    'ssn': [
        r'000-\d{2}-\d{4}',  # Invalid area
        r'666-\d{2}-\d{4}',  # Invalid area
        r'9\d{2}-\d{2}-\d{4}',  # Invalid area
        r'\d{3}-00-\d{4}',  # Invalid group
        r'\d{3}-\d{2}-0000',  # Invalid serial
    ],
    'phone': [
        r'555-01\d{2}',  # Fictional numbers
        r'1-800-',
        r'1-888-',
        r'1-877-',
    ],
    'email': [
        r'@example\.com$',
        r'@test\.com$',
        r'@localhost$',
        r'^noreply@',
        r'^no-reply@',
    ],
    'ip_address': [
        r'^127\.',  # Localhost
        r'^0\.0\.0\.0$',
        r'^192\.168\.',  # Private (may still want to flag)
        r'^10\.',  # Private
    ],
}


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Finding:
    """Represents a single PHI/PII finding."""
    id: str
    timestamp: str
    file: str
    line: int
    column: int
    identifier_type: str
    identifier_name: str
    pattern_name: str
    value_hash: str
    context: str
    classification: str
    confidence: float
    sensitivity: int
    risk_score: int = 0
    severity: str = ''
    hipaa_rules: list = field(default_factory=list)
    remediation_steps: list = field(default_factory=list)
    status: str = 'open'

    def __post_init__(self):
        self.risk_score = self._calculate_risk()
        self.severity = self._get_severity()
        self.hipaa_rules = self._get_hipaa_rules()
        self.remediation_steps = self._get_remediation()

    def _calculate_risk(self) -> int:
        """Calculate risk score based on sensitivity and confidence."""
        # Simplified risk calculation
        base = self.sensitivity * self.confidence
        return min(100, int(base))

    def _get_severity(self) -> str:
        """Map risk score to severity level."""
        if self.risk_score >= 90:
            return 'critical'
        elif self.risk_score >= 70:
            return 'high'
        elif self.risk_score >= 50:
            return 'medium'
        elif self.risk_score >= 25:
            return 'low'
        return 'informational'

    def _get_hipaa_rules(self) -> list:
        """Get applicable HIPAA rules for this finding."""
        rules = []
        if self.classification == 'PHI':
            rules.append({
                'rule': 'Privacy Rule',
                'section': '164.514(b)(2)',
                'description': f'{self.identifier_name} is a HIPAA identifier requiring protection'
            })
            rules.append({
                'rule': 'Security Rule',
                'section': '164.312(a)(1)',
                'description': 'Access controls required for ePHI'
            })
        return rules

    def _get_remediation(self) -> list:
        """Get remediation steps for this finding."""
        steps = [
            f'Remove or encrypt the {self.identifier_name}',
            'Implement access controls',
            'Add audit logging for access',
        ]
        if self.identifier_type == 'ssn':
            steps.insert(0, 'URGENT: SSN requires immediate remediation')
        return steps


@dataclass
class ScanResult:
    """Container for scan results."""
    findings: list = field(default_factory=list)
    files_scanned: int = 0
    scan_timestamp: str = ''
    scan_duration: float = 0.0
    errors: list = field(default_factory=list)

    def add_finding(self, finding: Finding):
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
                'by_classification': self._count_by_classification(),
            },
            'errors': self.errors,
        }

    def _count_by_severity(self) -> dict:
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'informational': 0}
        for f in self.findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_type(self) -> dict:
        counts = {}
        for f in self.findings:
            counts[f.identifier_type] = counts.get(f.identifier_type, 0) + 1
        return counts

    def _count_by_classification(self) -> dict:
        counts = {'PHI': 0, 'PII': 0, 'sensitive_nonPHI': 0}
        for f in self.findings:
            counts[f.classification] = counts.get(f.classification, 0) + 1
        return counts


# =============================================================================
# Detection Functions
# =============================================================================

def hash_value(value: str) -> str:
    """Create SHA-256 hash of detected value."""
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]}"


def redact_value(value: str, show_chars: int = 4) -> str:
    """Redact sensitive value, keeping last N characters."""
    if len(value) <= show_chars:
        return '[REDACTED]'
    return f"[REDACTED]...{value[-show_chars:]}"


def get_context(content: str, match_start: int, match_end: int, context_chars: int = 30) -> str:
    """Extract context around a match with redacted value."""
    start = max(0, match_start - context_chars)
    end = min(len(content), match_end + context_chars)

    before = content[start:match_start]
    matched = content[match_start:match_end]
    after = content[match_end:end]

    # Redact the matched value in context
    redacted = redact_value(matched)
    return f"...{before}{redacted}{after}..."


def is_excluded(value: str, identifier_type: str) -> bool:
    """Check if value matches an exclusion pattern."""
    exclusions = EXCLUSIONS.get(identifier_type, [])
    for pattern in exclusions:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False


def calculate_confidence(pattern_name: str, has_label: bool, context: str) -> float:
    """Calculate confidence score for a detection."""
    base = 0.70

    # Boost for labeled patterns
    if has_label or 'labeled' in pattern_name:
        base += 0.20

    # Boost for healthcare context
    healthcare_keywords = ['patient', 'medical', 'health', 'hospital', 'clinic', 'diagnosis']
    for keyword in healthcare_keywords:
        if keyword in context.lower():
            base += 0.05
            break

    return min(0.99, base)


def scan_content(content: str, file_path: str, finding_counter: list) -> list:
    """Scan content for PHI/PII patterns."""
    findings = []
    lines = content.split('\n')

    for identifier_type, config in PATTERNS.items():
        for pattern, pattern_name in config['patterns']:
            for match in re.finditer(pattern, content):
                value = match.group()

                # Check exclusions
                if is_excluded(value, identifier_type):
                    continue

                # Calculate position
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                column = match.start() - line_start + 1

                # Generate finding
                finding_counter[0] += 1
                finding_id = f"F-{datetime.now().strftime('%Y%m%d')}-{finding_counter[0]:04d}"

                context = get_context(content, match.start(), match.end())
                confidence = calculate_confidence(pattern_name, 'labeled' in pattern_name, context)

                finding = Finding(
                    id=finding_id,
                    timestamp=datetime.now().isoformat() + 'Z',
                    file=file_path,
                    line=line_num,
                    column=column,
                    identifier_type=identifier_type,
                    identifier_name=config['name'],
                    pattern_name=pattern_name,
                    value_hash=hash_value(value),
                    context=context,
                    classification=config['classification'],
                    confidence=confidence,
                    sensitivity=config['sensitivity'],
                )

                findings.append(finding)

    return findings


def scan_file(file_path: Path, finding_counter: list) -> list:
    """Scan a single file for PHI/PII."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        return scan_content(content, str(file_path), finding_counter)
    except Exception as e:
        return []


def get_files_to_scan(path: Path, include: Optional[list], exclude: Optional[list]) -> list:
    """Get list of files to scan based on patterns."""
    files = []

    # Default patterns
    default_include = ['**/*.py', '**/*.js', '**/*.ts', '**/*.json', '**/*.yaml',
                       '**/*.yml', '**/*.xml', '**/*.csv', '**/*.txt', '**/*.log',
                       '**/*.env', '**/*.sql', '**/*.md']
    default_exclude = ['**/node_modules/**', '**/.git/**', '**/venv/**',
                       '**/__pycache__/**', '**/vendor/**', '**/.idea/**']

    include_patterns = include or default_include
    exclude_patterns = exclude or default_exclude

    if path.is_file():
        return [path]

    for pattern in include_patterns:
        for file_path in path.glob(pattern):
            if file_path.is_file():
                # Check exclusions
                excluded = False
                for exc_pattern in exclude_patterns:
                    if file_path.match(exc_pattern):
                        excluded = True
                        break
                if not excluded:
                    files.append(file_path)

    return list(set(files))


# =============================================================================
# Output Functions
# =============================================================================

def output_json(result: ScanResult) -> str:
    """Format results as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def output_markdown(result: ScanResult) -> str:
    """Format results as Markdown."""
    lines = [
        '# PHI/PII Detection Results\n',
        f'**Scan Time:** {result.scan_timestamp}',
        f'**Files Scanned:** {result.files_scanned}',
        f'**Total Findings:** {len(result.findings)}\n',
        '## Summary by Severity\n',
        '| Severity | Count |',
        '|----------|-------|',
    ]

    for sev, count in result.to_dict()['summary']['by_severity'].items():
        lines.append(f'| {sev.capitalize()} | {count} |')

    lines.append('\n## Findings\n')

    for f in result.findings:
        lines.extend([
            f'### {f.id} - {f.identifier_name}',
            f'- **Severity:** {f.severity.upper()}',
            f'- **Risk Score:** {f.risk_score}',
            f'- **File:** {f.file}:{f.line}',
            f'- **Context:** `{f.context}`',
            '',
        ])

    return '\n'.join(lines)


def output_csv(result: ScanResult) -> str:
    """Format results as CSV."""
    lines = ['id,severity,risk_score,file,line,type,classification']
    for f in result.findings:
        lines.append(f'{f.id},{f.severity},{f.risk_score},{f.file},{f.line},{f.identifier_type},{f.classification}')
    return '\n'.join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Scan files for PHI/PII')
    parser.add_argument('path', help='File or directory to scan')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'csv'],
                        default='json', help='Output format')
    parser.add_argument('--severity', '-s', choices=['low', 'medium', 'high', 'critical'],
                        help='Minimum severity to report')
    parser.add_argument('--include', nargs='+', help='File patterns to include')
    parser.add_argument('--exclude', nargs='+', help='File patterns to exclude')
    parser.add_argument('--synthetic', action='store_true',
                        help='Treat findings as synthetic test data')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Initialize
    start_time = datetime.now()
    path = Path(args.path)
    result = ScanResult()
    result.scan_timestamp = start_time.isoformat() + 'Z'
    finding_counter = [0]

    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    # Get files
    files = get_files_to_scan(path, args.include, args.exclude)
    result.files_scanned = len(files)

    if args.verbose:
        print(f"Scanning {len(files)} files...", file=sys.stderr)

    # Scan files
    for file_path in files:
        findings = scan_file(file_path, finding_counter)
        for f in findings:
            # Filter by severity if specified
            if args.severity:
                severity_order = {'informational': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                if severity_order.get(f.severity, 0) < severity_order.get(args.severity, 0):
                    continue
            result.add_finding(f)

    # Calculate duration
    result.scan_duration = (datetime.now() - start_time).total_seconds()

    # Format output
    if args.format == 'json':
        output = output_json(result)
    elif args.format == 'markdown':
        output = output_markdown(result)
    else:
        output = output_csv(result)

    # Write output
    if args.output:
        Path(args.output).write_text(output)
        if args.verbose:
            print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with error code if critical findings
    if any(f.severity == 'critical' for f in result.findings):
        sys.exit(2)
    elif any(f.severity == 'high' for f in result.findings):
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
