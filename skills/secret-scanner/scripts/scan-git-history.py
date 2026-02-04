#!/usr/bin/env python3
"""
Git History Secret Scanner - Scan git commit history for leaked secrets.

Searches through all commits, branches, and diffs for secrets that may have
been committed and later removed. Critical for finding secrets that are
technically "deleted" but still exist in git history.

Usage:
    python scan-git-history.py <repo-path> [options]
    python scan-git-history.py ./repo --depth 100 --branch main
    python scan-git-history.py . --all-branches --format json
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class GitFinding:
    """A secret found in git history."""
    id: str
    commit_hash: str
    commit_short: str
    author: str
    author_email: str
    commit_date: str
    commit_message: str
    file_path: str
    line_number: int
    secret_type: str
    provider: str
    value_preview: str
    value_hash: str
    severity: str
    still_present: bool
    removed_in_commit: Optional[str]
    branch: str


# Secret patterns (subset of main scanner for git history)
GIT_SECRET_PATTERNS = [
    # AWS
    (r'(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}', 'aws_access_key', 'AWS', 'critical'),
    (r'(?i)aws[_\-\.]?secret[_\-\.]?(?:access)?[_\-\.]?key[\'"\s]*[:=]\s*[\'"][A-Za-z0-9/+=]{40}[\'"]', 'aws_secret_key', 'AWS', 'critical'),

    # GitHub
    (r'ghp_[A-Za-z0-9_]{36,255}', 'github_token', 'GitHub', 'critical'),
    (r'gho_[A-Za-z0-9_]{36,255}', 'github_oauth', 'GitHub', 'critical'),
    (r'github_pat_[A-Za-z0-9_]{22,255}', 'github_fine_grained', 'GitHub', 'critical'),

    # GitLab
    (r'glpat-[A-Za-z0-9_-]{20,}', 'gitlab_token', 'GitLab', 'critical'),

    # Stripe
    (r'sk_live_[A-Za-z0-9]{24,}', 'stripe_secret_key', 'Stripe', 'critical'),
    (r'sk_test_[A-Za-z0-9]{24,}', 'stripe_test_key', 'Stripe', 'medium'),
    (r'rk_live_[A-Za-z0-9]{24,}', 'stripe_restricted_key', 'Stripe', 'high'),

    # Slack
    (r'xoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24}', 'slack_bot_token', 'Slack', 'critical'),
    (r'xoxp-[0-9]{10,13}-[0-9]{10,13}-[0-9]{10,13}-[a-f0-9]{32}', 'slack_user_token', 'Slack', 'critical'),

    # Twilio
    (r'SK[a-f0-9]{32}', 'twilio_api_key', 'Twilio', 'high'),

    # SendGrid
    (r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}', 'sendgrid_api_key', 'SendGrid', 'critical'),

    # OpenAI
    (r'sk-[A-Za-z0-9]{20}T3BlbkFJ[A-Za-z0-9]{20}', 'openai_api_key', 'OpenAI', 'critical'),
    (r'sk-proj-[A-Za-z0-9_-]{48,}', 'openai_project_key', 'OpenAI', 'critical'),

    # Private Keys
    (r'-----BEGIN RSA PRIVATE KEY-----', 'rsa_private_key', 'Cryptographic', 'critical'),
    (r'-----BEGIN OPENSSH PRIVATE KEY-----', 'openssh_private_key', 'Cryptographic', 'critical'),
    (r'-----BEGIN EC PRIVATE KEY-----', 'ec_private_key', 'Cryptographic', 'critical'),
    (r'-----BEGIN PGP PRIVATE KEY BLOCK-----', 'pgp_private_key', 'Cryptographic', 'critical'),

    # Database URIs
    (r'mongodb(?:\+srv)?://[^:]+:[^@]+@[^/\s]+', 'mongodb_uri', 'MongoDB', 'critical'),
    (r'postgres(?:ql)?://[^:]+:[^@]+@[^/\s]+', 'postgres_uri', 'PostgreSQL', 'critical'),
    (r'mysql://[^:]+:[^@]+@[^/\s]+', 'mysql_uri', 'MySQL', 'critical'),

    # npm/PyPI
    (r'npm_[A-Za-z0-9]{36}', 'npm_token', 'npm', 'critical'),
    (r'pypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{50,}', 'pypi_token', 'PyPI', 'critical'),

    # GCP
    (r'AIza[0-9A-Za-z_-]{35}', 'gcp_api_key', 'GCP', 'high'),

    # DigitalOcean
    (r'dop_v1_[a-f0-9]{64}', 'digitalocean_token', 'DigitalOcean', 'critical'),

    # Generic patterns
    (r'(?i)(?:password|passwd|pwd)[\'"\s]*[:=]\s*[\'"][^\'"]{8,}[\'"]', 'generic_password', 'Generic', 'high'),
]

# Known false positives
FALSE_POSITIVES = [
    'AKIAIOSFODNN7EXAMPLE',
    'sk_test_PLACEHOLDER_VALUE_HERE',
    'xoxb-PLACEHOLDER-EXAMPLE-TOKEN',
    'EXAMPLE',
    'example',
    'YOUR_API_KEY',
    'your_api_key',
    'REPLACE_ME',
    'TODO',
    'PLACEHOLDER',
]


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}...{value[-show_chars:]}"


def hash_value(value: str) -> str:
    """Generate SHA256 hash of a value."""
    return f"sha256:{hashlib.sha256(value.encode()).hexdigest()[:16]}"


def is_false_positive(value: str) -> bool:
    """Check if value is a known false positive."""
    for fp in FALSE_POSITIVES:
        if fp in value:
            return True
    return False


def run_git_command(cmd: List[str], cwd: str) -> Tuple[bool, str]:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return True, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def get_commits(repo_path: str, depth: Optional[int] = None, branch: Optional[str] = None) -> List[Dict]:
    """Get list of commits to scan."""
    cmd = ['git', 'log', '--format=%H|%h|%an|%ae|%aI|%s']

    if depth:
        cmd.extend(['-n', str(depth)])

    if branch:
        cmd.append(branch)
    else:
        cmd.append('--all')

    success, output = run_git_command(cmd, repo_path)
    if not success:
        print(f"Error getting commits: {output}", file=sys.stderr)
        return []

    commits = []
    for line in output.strip().split('\n'):
        if not line:
            continue
        parts = line.split('|', 5)
        if len(parts) >= 6:
            commits.append({
                'hash': parts[0],
                'short': parts[1],
                'author': parts[2],
                'email': parts[3],
                'date': parts[4],
                'message': parts[5][:100],
            })

    return commits


def get_commit_diff(repo_path: str, commit_hash: str) -> str:
    """Get the diff for a specific commit."""
    cmd = ['git', 'show', '--format=', '-p', commit_hash]
    success, output = run_git_command(cmd, repo_path)
    return output if success else ""


def get_file_at_commit(repo_path: str, commit_hash: str, file_path: str) -> str:
    """Get file contents at a specific commit."""
    cmd = ['git', 'show', f'{commit_hash}:{file_path}']
    success, output = run_git_command(cmd, repo_path)
    return output if success else ""


def check_if_still_present(repo_path: str, file_path: str, secret_value: str) -> Tuple[bool, Optional[str]]:
    """Check if a secret is still present in the current HEAD."""
    cmd = ['git', 'show', f'HEAD:{file_path}']
    success, output = run_git_command(cmd, repo_path)

    if not success:
        # File might have been deleted
        return False, None

    if secret_value in output:
        return True, None

    # Try to find when it was removed
    cmd = ['git', 'log', '--oneline', '-S', secret_value, '--', file_path]
    success, output = run_git_command(cmd, repo_path)

    if success and output.strip():
        lines = output.strip().split('\n')
        if len(lines) > 1:
            # Last commit that modified this value is likely when it was removed
            return False, lines[0].split()[0]

    return False, None


def get_current_branch(repo_path: str) -> str:
    """Get the current branch name."""
    cmd = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    success, output = run_git_command(cmd, repo_path)
    return output.strip() if success else "unknown"


def scan_diff_for_secrets(
    diff_content: str,
    commit: Dict,
    repo_path: str,
    branch: str
) -> List[GitFinding]:
    """Scan a diff for secrets."""
    findings = []

    current_file = None
    line_number = 0

    for line in diff_content.split('\n'):
        # Track current file
        if line.startswith('+++ b/'):
            current_file = line[6:]
            line_number = 0
            continue

        if line.startswith('@@'):
            # Parse line number from hunk header
            match = re.search(r'\+(\d+)', line)
            if match:
                line_number = int(match.group(1)) - 1
            continue

        if line.startswith('+') and not line.startswith('+++'):
            line_number += 1
            content = line[1:]  # Remove the + prefix

            # Skip empty lines
            if not content.strip():
                continue

            # Scan for secrets
            for pattern, secret_type, provider, severity in GIT_SECRET_PATTERNS:
                for match in re.finditer(pattern, content):
                    value = match.group(0)

                    # Skip false positives
                    if is_false_positive(value):
                        continue

                    # Check if still present
                    still_present = False
                    removed_in = None
                    if current_file:
                        still_present, removed_in = check_if_still_present(
                            repo_path, current_file, value
                        )

                    finding = GitFinding(
                        id=f"GS-{commit['short']}-{len(findings)+1:04d}",
                        commit_hash=commit['hash'],
                        commit_short=commit['short'],
                        author=commit['author'],
                        author_email=commit['email'],
                        commit_date=commit['date'],
                        commit_message=commit['message'],
                        file_path=current_file or "unknown",
                        line_number=line_number,
                        secret_type=secret_type,
                        provider=provider,
                        value_preview=mask_secret(value),
                        value_hash=hash_value(value),
                        severity=severity,
                        still_present=still_present,
                        removed_in_commit=removed_in,
                        branch=branch,
                    )
                    findings.append(finding)

        elif not line.startswith('-'):
            line_number += 1

    return findings


def scan_git_history(
    repo_path: str,
    depth: Optional[int] = None,
    branch: Optional[str] = None,
    all_branches: bool = False
) -> List[GitFinding]:
    """Scan git history for secrets."""
    all_findings = []
    seen_hashes: Set[str] = set()

    # Get current branch
    current_branch = branch or get_current_branch(repo_path)

    # Get commits
    commits = get_commits(repo_path, depth, None if all_branches else branch)

    print(f"Scanning {len(commits)} commits...", file=sys.stderr)

    for i, commit in enumerate(commits):
        if (i + 1) % 50 == 0:
            print(f"  Processed {i + 1}/{len(commits)} commits...", file=sys.stderr)

        diff = get_commit_diff(repo_path, commit['hash'])
        findings = scan_diff_for_secrets(diff, commit, repo_path, current_branch)

        # Deduplicate by value hash
        for finding in findings:
            if finding.value_hash not in seen_hashes:
                seen_hashes.add(finding.value_hash)
                all_findings.append(finding)

    return all_findings


def format_json(findings: List[GitFinding]) -> str:
    """Format findings as JSON."""
    output = {
        "scan_timestamp": datetime.now().isoformat(),
        "total_findings": len(findings),
        "still_present": len([f for f in findings if f.still_present]),
        "removed": len([f for f in findings if not f.still_present]),
        "findings": [asdict(f) for f in findings]
    }
    return json.dumps(output, indent=2)


def format_markdown(findings: List[GitFinding]) -> str:
    """Format findings as Markdown."""
    lines = [
        "# Git History Secret Scan Report",
        "",
        f"**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Summary",
        "",
        f"- **Total Secrets Found:** {len(findings)}",
        f"- **Still Present in HEAD:** {len([f for f in findings if f.still_present])}",
        f"- **Removed (but in history):** {len([f for f in findings if not f.still_present])}",
        "",
    ]

    # Severity breakdown
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1

    lines.extend([
        "### By Severity",
        "",
    ])
    for sev in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(sev, 0)
        if count > 0:
            lines.append(f"- **{sev.upper()}:** {count}")

    # Still present (urgent)
    still_present = [f for f in findings if f.still_present]
    if still_present:
        lines.extend([
            "",
            "---",
            "",
            "## URGENT: Secrets Still Present",
            "",
            "These secrets are still in the current codebase and must be rotated immediately!",
            "",
        ])
        for f in still_present:
            lines.extend([
                f"### {f.id}: {f.secret_type}",
                "",
                f"- **Provider:** {f.provider}",
                f"- **File:** `{f.file_path}`",
                f"- **Line:** {f.line_number}",
                f"- **Value:** `{f.value_preview}`",
                f"- **Severity:** {f.severity.upper()}",
                f"- **First Committed:** {f.commit_date} by {f.author}",
                f"- **Commit:** `{f.commit_short}` - {f.commit_message}",
                "",
            ])

    # Removed but in history
    removed = [f for f in findings if not f.still_present]
    if removed:
        lines.extend([
            "",
            "---",
            "",
            "## Secrets in Git History (Removed from HEAD)",
            "",
            "These secrets have been removed but still exist in git history.",
            "Consider cleaning git history with BFG or git filter-branch.",
            "",
        ])
        for f in removed:
            lines.extend([
                f"### {f.id}: {f.secret_type}",
                "",
                f"- **Provider:** {f.provider}",
                f"- **File:** `{f.file_path}`",
                f"- **Value:** `{f.value_preview}`",
                f"- **Severity:** {f.severity.upper()}",
                f"- **Committed:** {f.commit_date} by {f.author}",
                f"- **Commit:** `{f.commit_short}` - {f.commit_message}",
            ])
            if f.removed_in_commit:
                lines.append(f"- **Removed in:** `{f.removed_in_commit}`")
            lines.append("")

    lines.extend([
        "---",
        "",
        "## Remediation",
        "",
        "### For secrets still present:",
        "1. Immediately rotate the credential",
        "2. Remove from code and use environment variables",
        "3. Clean git history",
        "",
        "### For secrets in history only:",
        "1. Rotate the credential (it may have been compromised)",
        "2. Clean git history using BFG Repo-Cleaner:",
        "   ```bash",
        "   bfg --replace-text secrets.txt repo.git",
        "   git reflog expire --expire=now --all",
        "   git gc --prune=now --aggressive",
        "   git push --force",
        "   ```",
        "",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan git history for leaked secrets"
    )
    parser.add_argument(
        "repo_path",
        help="Path to git repository"
    )
    parser.add_argument(
        "--depth", "-n",
        type=int,
        help="Number of commits to scan (default: all)"
    )
    parser.add_argument(
        "--branch", "-b",
        help="Branch to scan (default: current)"
    )
    parser.add_argument(
        "--all-branches",
        action="store_true",
        help="Scan all branches"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write output to file"
    )

    args = parser.parse_args()

    # Verify it's a git repo
    if not Path(args.repo_path).joinpath('.git').exists():
        print(f"Error: {args.repo_path} is not a git repository", file=sys.stderr)
        sys.exit(1)

    # Run scan
    findings = scan_git_history(
        args.repo_path,
        depth=args.depth,
        branch=args.branch,
        all_branches=args.all_branches
    )

    print(f"\nFound {len(findings)} secrets in git history", file=sys.stderr)

    # Format output
    if args.format == "json":
        output = format_json(findings)
    else:
        output = format_markdown(findings)

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with error code if critical/high findings still present
    urgent = [f for f in findings if f.still_present and f.severity in ['critical', 'high']]
    if urgent:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
