#!/usr/bin/env python3
"""
HIPAA Guardian - Report Generation Script

Generates human-readable audit reports from PHI detection findings.

Usage:
    python generate-report.py <findings.json> [options]

Options:
    --output, -o     Output file path (default: audit_report.md)
    --format, -f     Output format: markdown, html (default: markdown)
    --title          Report title
    --org            Organization name
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def load_findings(path: str) -> Dict:
    """Load findings from JSON file."""
    with open(path) as f:
        return json.load(f)


def generate_executive_summary(data: Dict) -> List[str]:
    """Generate executive summary section."""
    summary = data.get('summary', {})
    findings = data.get('findings', [])

    total = summary.get('total_findings', len(findings))
    by_severity = summary.get('by_severity', {})

    critical = by_severity.get('critical', 0)
    high = by_severity.get('high', 0)

    # Determine overall status
    if critical > 0:
        status = 'CRITICAL - Immediate Action Required'
        status_emoji = '🔴'
    elif high > 0:
        status = 'AT RISK - Prompt Remediation Needed'
        status_emoji = '🟠'
    elif total > 0:
        status = 'NEEDS ATTENTION - Review Recommended'
        status_emoji = '🟡'
    else:
        status = 'COMPLIANT - No PHI Detected'
        status_emoji = '🟢'

    lines = [
        '## Executive Summary\n',
        f'**Overall Status:** {status_emoji} {status}\n',
        f'This audit identified **{total} findings** requiring review.\n',
        '### Risk Overview\n',
        '| Severity | Count | Action Required |',
        '|----------|-------|-----------------|',
        f'| Critical | {by_severity.get("critical", 0)} | Immediate |',
        f'| High | {by_severity.get("high", 0)} | Within 24 hours |',
        f'| Medium | {by_severity.get("medium", 0)} | Within 1 week |',
        f'| Low | {by_severity.get("low", 0)} | Within 1 month |',
        f'| Informational | {by_severity.get("informational", 0)} | As needed |',
        '',
    ]

    return lines


def generate_findings_section(findings: List[Dict]) -> List[str]:
    """Generate detailed findings section."""
    lines = ['## Detailed Findings\n']

    # Group by severity
    severity_order = ['critical', 'high', 'medium', 'low', 'informational']

    for severity in severity_order:
        severity_findings = [f for f in findings if f.get('severity') == severity]
        if not severity_findings:
            continue

        lines.append(f'### {severity.upper()} Severity ({len(severity_findings)})\n')

        for finding in severity_findings:
            finding_id = finding.get('id', 'Unknown')
            identifier_name = finding.get('identifier_name', finding.get('finding_type', 'Unknown'))
            file_path = finding.get('file', 'Unknown')
            line = finding.get('line', 0)
            risk_score = finding.get('risk_score', finding.get('risk_assessment', {}).get('overall_score', 0))
            context = finding.get('context', '')

            lines.extend([
                f'#### {finding_id}: {identifier_name}',
                '',
                '| Attribute | Value |',
                '|-----------|-------|',
                f'| Risk Score | {risk_score}/100 |',
                f'| File | `{file_path}:{line}` |',
                f'| Classification | {finding.get("classification", "N/A")} |',
                '',
                '**Context:**',
                f'```',
                f'{context}',
                f'```',
                '',
            ])

            # HIPAA rules
            hipaa_rules = finding.get('hipaa_rules', finding.get('hipaa_mapping', []))
            if hipaa_rules:
                lines.append('**HIPAA Rules:**')
                for rule in hipaa_rules:
                    rule_name = rule.get('rule', '')
                    section = rule.get('section', '')
                    desc = rule.get('description', '')
                    lines.append(f'- **{rule_name} {section}**: {desc}')
                lines.append('')

            # Remediation
            remediation = finding.get('remediation_steps', finding.get('remediation', []))
            if remediation:
                lines.append('**Remediation Steps:**')
                for i, step in enumerate(remediation, 1):
                    if isinstance(step, dict):
                        lines.append(f'{i}. {step.get("action", step)}')
                    else:
                        lines.append(f'{i}. {step}')
                lines.append('')

            lines.append('---\n')

    return lines


def generate_compliance_section(data: Dict) -> List[str]:
    """Generate HIPAA compliance status section."""
    findings = data.get('findings', [])

    # Analyze findings for compliance
    has_phi = any(f.get('classification') == 'PHI' for f in findings)
    has_unencrypted = any('encrypt' in str(f.get('remediation_steps', [])).lower() for f in findings)
    has_access_control_issues = any('access' in str(f.get('remediation_steps', [])).lower() for f in findings)

    lines = [
        '## HIPAA Compliance Summary\n',
        '### Privacy Rule (45 CFR 164.500-534)\n',
        '| Requirement | Status | Notes |',
        '|-------------|--------|-------|',
    ]

    if has_phi:
        lines.append('| PHI Protection | ⚠️ Needs Review | Unprotected PHI detected |')
        lines.append('| De-identification | ❌ Failed | PHI identifiers present |')
    else:
        lines.append('| PHI Protection | ✓ Pass | No unprotected PHI detected |')
        lines.append('| De-identification | ✓ Pass | Data appears de-identified |')

    lines.extend([
        '',
        '### Security Rule (45 CFR 164.302-318)\n',
        '| Requirement | Status | Notes |',
        '|-------------|--------|-------|',
    ])

    if has_access_control_issues:
        lines.append('| Access Control | ⚠️ Review | Access control improvements recommended |')
    else:
        lines.append('| Access Control | ✓ Pass | No access control issues detected |')

    if has_unencrypted:
        lines.append('| Encryption | ❌ Failed | Unencrypted PHI detected |')
    else:
        lines.append('| Encryption | ✓ Pass | No unencrypted PHI detected |')

    lines.append('')
    return lines


def generate_playbook_section(findings: List[Dict]) -> List[str]:
    """Generate remediation playbook section."""
    lines = [
        '## Remediation Playbook\n',
        'Prioritized actions to address findings:\n',
    ]

    # Group by priority
    critical_actions = []
    high_actions = []
    medium_actions = []

    for finding in findings:
        severity = finding.get('severity', 'medium')
        finding_id = finding.get('id', 'Unknown')
        file_path = finding.get('file', 'Unknown')

        remediation = finding.get('remediation_steps', finding.get('remediation', []))
        if remediation:
            first_action = remediation[0]
            if isinstance(first_action, dict):
                action = first_action.get('action', str(first_action))
            else:
                action = first_action

            item = f'[ ] {action} ({finding_id} in `{file_path}`)'

            if severity == 'critical':
                critical_actions.append(item)
            elif severity == 'high':
                high_actions.append(item)
            else:
                medium_actions.append(item)

    if critical_actions:
        lines.append('### Priority 1: Critical (Immediate)\n')
        lines.extend(critical_actions)
        lines.append('')

    if high_actions:
        lines.append('### Priority 2: High (24 hours)\n')
        lines.extend(high_actions)
        lines.append('')

    if medium_actions:
        lines.append('### Priority 3: Medium (1 week)\n')
        lines.extend(medium_actions)
        lines.append('')

    return lines


def generate_markdown_report(data: Dict, title: str, org: str) -> str:
    """Generate complete Markdown report."""
    lines = [
        f'# {title}\n',
        f'**Organization:** {org}',
        f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'**Scanner Version:** HIPAA Guardian v1.0.0\n',
        '---\n',
    ]

    # Add sections
    lines.extend(generate_executive_summary(data))
    lines.extend(generate_compliance_section(data))
    lines.extend(generate_findings_section(data.get('findings', [])))
    lines.extend(generate_playbook_section(data.get('findings', [])))

    # Footer
    lines.extend([
        '---\n',
        '## Disclaimer\n',
        'This automated scan assists with HIPAA compliance but does not constitute legal advice.',
        'Organizations should work with qualified compliance professionals for complete HIPAA compliance programs.\n',
        f'*Report generated by HIPAA Guardian*',
    ])

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Generate HIPAA audit report from findings')
    parser.add_argument('findings', help='Path to findings JSON file')
    parser.add_argument('--output', '-o', default='audit_report.md', help='Output file path')
    parser.add_argument('--format', '-f', choices=['markdown', 'html'], default='markdown')
    parser.add_argument('--title', default='HIPAA Compliance Audit Report')
    parser.add_argument('--org', default='Organization')

    args = parser.parse_args()

    # Load findings
    try:
        data = load_findings(args.findings)
    except FileNotFoundError:
        print(f"Error: Findings file not found: {args.findings}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in findings file: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate report
    if args.format == 'markdown':
        report = generate_markdown_report(data, args.title, args.org)
    else:
        # HTML format - wrap markdown in basic HTML
        md_content = generate_markdown_report(data, args.title, args.org)
        report = f'''<!DOCTYPE html>
<html>
<head>
    <title>{args.title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        h1, h2, h3, h4 {{ color: #333; }}
    </style>
</head>
<body>
<pre>{md_content}</pre>
</body>
</html>'''

    # Write output
    Path(args.output).write_text(report)
    print(f"Report generated: {args.output}")


if __name__ == '__main__':
    main()
