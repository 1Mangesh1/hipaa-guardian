# HIPAA Guardian Skill

HIPAA compliance skill for AI coding agents. Detects PHI/PII, maps to regulations, generates audit reports.

## Quick Start

```bash
# Install via skills.sh CLI
npx skills add 1Mangesh1/hipaa-guardian
```

> **Verification:** Before installing, review the source at
> [github.com/1Mangesh1/hipaa-guardian](https://github.com/1Mangesh1/hipaa-guardian).
> You can also verify the package integrity after install — see [SECURITY.md](SECURITY.md)
> for checksum verification instructions and the project's trust model.

## Capabilities

- **PHI Detection** - All 18 HIPAA Safe Harbor identifiers
- **Code Scanning** - Hardcoded PHI, comments, test fixtures, configs
- **Risk Scoring** - 0-100 scale with severity levels
- **HIPAA Mapping** - Privacy Rule, Security Rule, Breach Rule
- **Audit Reports** - Markdown reports with remediation playbooks

## Usage

```bash
/hipaa-guardian scan ./data          # Scan data files
/hipaa-guardian scan-code ./src      # Scan source code
/hipaa-guardian audit ./project      # Full audit report
/hipaa-guardian controls .           # Check security controls
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill instructions |
| `AGENTS.md` | Agent-specific guidance |
| `metadata.json` | Skill metadata |
| `references/` | HIPAA rules, patterns, scoring |
| `examples/` | Sample outputs |
| `scripts/` | Detection scripts |

## License

MIT

## Security

See [SECURITY.md](SECURITY.md) for:
- Vulnerability reporting process
- Trust model and verification
- Input sanitization documentation
- Script integrity checking
