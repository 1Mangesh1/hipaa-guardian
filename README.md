# HIPAA Guardian

PHI/PII detection and HIPAA compliance skills for Claude, Cursor, Windsurf, and other AI coding agents.

HIPAA Guardian scans source code, data files, logs, and API responses for the 18 HIPAA Safe Harbor identifiers, scores the risk of each finding, maps it to the relevant HIPAA rule, and writes an audit report you can hand to a reviewer. The detection engine is plain Python with no runtime dependencies, so it also drops into a pre-commit hook or a CI job.

It is built for the place most PHI actually leaks: developer artifacts. Seed scripts with real patient rows, a debug log that prints an SSN, a test fixture copied from production, an endpoint that returns a full `Patient` resource without an auth check.

## What it is not

This is detection and triage, not certification. It catches the obvious and semi-obvious leaks fast, and it gives you confidence scores so you can tell a likely SSN from a phone number that happens to look like one. It does not prove you are HIPAA compliant, and it does not replace a human review or a Business Associate Agreement. Treat a clean scan as "nothing obvious found," not "safe to ship."

## What gets detected

All 18 HIPAA Safe Harbor identifiers, with a confidence score (0-100%) per match:

| Identifier | Examples | Default risk |
|------------|----------|--------------|
| Names | Patient, provider, relatives | High |
| SSN | Social Security Numbers (validated against never-issued ranges) | Critical |
| MRN | Medical Record Numbers | Critical |
| Dates | DOB, admission, discharge, death | High |
| Phone / Fax | Most US formats | Medium |
| Email | Any address | Medium |
| Address | Street, city, ZIP | Medium |
| Health plan ID | Insurance, policy numbers | High |
| Account / license / vehicle / device IDs | Financial, DL, VIN, UDI | Medium |
| Biometric / photos | Fingerprint, retinal, voice, full-face | Critical |
| URLs / IPs | Web and network identifiers (public IPs only) | Low-Medium |

SSNs in federally never-issued ranges (area `000`, `666`, `9xx`; group `00`; serial `0000`) are excluded, as are documentation values like `555-01xx` phone numbers, `example.com` emails, and private/loopback IPs. That keeps the false-positive rate down on real codebases.

## Install

```bash
# All three skills
npx skills add 1Mangesh1/hipaa-guardian

# Just the core detection skill
npx skills add 1Mangesh1/hipaa-guardian --skill hipaa-guardian
```

Once installed, the skill activates when you ask Claude (or another agent) to scan for PHI, run a HIPAA check, or audit a codebase. You can also run the scanners directly.

## The skills

| Skill | What it does | Ships scripts? | Version |
|-------|--------------|----------------|---------|
| [hipaa-guardian](./skills/hipaa-guardian/) | PHI/PII detection, code/log/auth/response scanning, risk scoring, audit reports | Yes (8 scripts) | 1.2.0 |
| [fhir-hl7-validator](./skills/fhir-hl7-validator/) | FHIR R5 and HL7 v2 structure/PHI review | No, instruction-based | 1.0.0 |
| [healthcare-audit-logger](./skills/healthcare-audit-logger/) | HIPAA-compliant audit-trail entry design | No, instruction-based | 1.0.0 |

`hipaa-guardian` is the one with executable tooling. The other two are prompt skills: they give the agent the rules and patterns to do the work itself, with no bundled scripts to run.

## Running the scanners directly

Every scanner is a standalone script. They take a path, print to stdout (or a file with `-o`), and use exit codes so CI can gate on them: `0` clean, `1` high-severity findings, `2` critical findings.

```bash
cd skills/hipaa-guardian

# Scan data files for PHI (JSON, CSV, FHIR, HL7, CDA, ...)
python3 scripts/detect-phi.py path/to/data -f markdown -o phi-report.md

# Scan source code for hardcoded PHI, fixtures, and config leaks
python3 scripts/scan-code.py path/to/repo -f json -o code-findings.json

# Find PHI endpoints with no auth gate
python3 scripts/scan-auth.py path/to/api

# Find PHI in log statements, and in API responses
python3 scripts/scan-logs.py path/to/src
python3 scripts/scan-response.py path/to/src

# Turn a findings file into a human-readable audit report
python3 scripts/generate-report.py code-findings.json -o audit.md

# Check project security controls (.gitignore, pre-commit, secrets, perms)
bash scripts/validate-controls.sh path/to/repo
```

Detected values are never printed. Each finding stores a SHA-256 hash and a redacted context snippet, so the report itself is safe to commit or paste into a ticket.

## Examples

### Scan code for hardcoded patient data

Ask the agent, or run `scan-code.py`. A seeder full of real-looking patient rows comes back as:

```json
{
  "id": "CF-20260623-0007",
  "file": "database/seeders/PatientSeeder.js",
  "line": 42,
  "identifier_type": "ssn",
  "pattern_name": "phi_assignment",
  "value_hash": "sha256:9f86d081884c7d65",
  "context": "ssn: \"[REDACTED-SSN]\",",
  "severity": "critical",
  "risk_score": 95,
  "remediation": [
    "Remove the hardcoded value",
    "Generate test data with a faker library instead",
    "Move any real credentials to environment variables"
  ]
}
```

The fix is the boring one: replace the literal with generated data.

```js
// Before
const mockPatient = { name: "John Doe", ssn: "...", mrn: "...", dob: "..." };

// After
const { faker } = require('@faker-js/faker');
const mockPatient = {
  name: faker.person.fullName(),
  ssn: faker.string.numeric(9),
  mrn: `MRN-${faker.string.uuid()}`,
  dob: faker.date.birthdate(),
};
```

### Catch PHI in logs

A log line like `ERROR: query failed for patient John Doe (SSN: ...)` is a reportable disclosure sitting in plaintext. `scan-logs.py` flags it and points at the safe pattern: log the internal ID, never the identifiers.

```js
logger.error(`query failed for patient: ${patient.id}`);  // ok
// never log name, SSN, DOB, MRN
```

### Review a FHIR response

For a `Patient` resource served from your API, the `fhir-hl7-validator` skill checks the structure and confirms that the PHI present (name, birthDate, identifiers) is expected for the endpoint and that the response is going to an authorized caller. PHI in a clinical exchange is the point; PHI leaking to an unauthenticated route is the bug. The skill is there to tell the two apart.

### Generate a compliance report

Point `generate-report.py` at a findings file and it produces an audit report: an executive summary with an overall status, a severity breakdown, per-finding detail with HIPAA rule mappings, and a prioritized remediation playbook (critical first). Feed it the output of `detect-phi.py` or `scan-code.py`.

## CI and pre-commit

Block commits that introduce PHI:

```bash
cp skills/hipaa-guardian/scripts/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

The hook scans staged content and blocks the commit on critical (and, by default, high) findings. Configure it with `HIPAA_BLOCK_ON_CRITICAL`, `HIPAA_BLOCK_ON_HIGH`, `HIPAA_SCAN_DATA`, and `HIPAA_SCAN_CODE`. For GitHub Actions and the `pre-commit` framework wiring, see [skills/hipaa-guardian/SKILL.md](./skills/hipaa-guardian/SKILL.md).

## Healthcare formats

| Format | Extensions | Detected on |
|--------|------------|-------------|
| FHIR R4/R5 | `.fhir.json`, `.fhir.xml` | Resource type, identifiers |
| HL7 v2.x | `.hl7`, `.hl7v2` | MSH, PID (SSN in PID-19, DOB in PID-7), DG1, OBX, IN1 |
| CDA / C-CDA | `.cda`, `.ccda`, `.ccd` | ClinicalDocument, patientRole |
| X12 EDI | `.x12`, `.edi`, `.837` | Transaction set headers |

## Regulatory references

HIPAA rules are cited inline in findings and documented under [references/](./references/) and [skills/hipaa-guardian/references/](./skills/hipaa-guardian/references/):

- Privacy Rule (45 CFR 164.500-534)
- Security Rule (45 CFR 164.302-318)
- Breach Notification Rule (45 CFR 164.400-414)
- Safe Harbor de-identification (45 CFR 164.514(b))

External standards used for the format and risk references: [HL7 FHIR R5](https://www.hl7.org/fhir/R5/), [NIST CSF 2.0](https://www.nist.gov/cyberframework), [NIST SP 800-66r2](https://csrc.nist.gov/pubs/sp/800/66/r2/final), and [NIST SP 800-188](https://csrc.nist.gov/pubs/sp/800/188/final) on de-identification.

## FAQ

**Can I use this in production?**
For detection and triage, yes. For compliance sign-off, no tool substitutes for a security review, your compliance team, and a signed BAA with any provider that touches PHI.

**Does it find all PHI?**
It finds the 18 Safe Harbor identifiers with good precision. Free-text PHI (a diagnosis written into a comment, a name embedded in prose) still needs human review. Pair the scan with one.

**What about false positives?**
Every finding has a confidence score. Low-confidence matches are worth a look before you act on them, and the never-issued-range and documentation-value exclusions cut most of the noise.

**How do I report a security issue?**
Privately, please. See [skills/hipaa-guardian/SECURITY.md](./skills/hipaa-guardian/SECURITY.md). Do not open a public issue for a vulnerability.

## Troubleshooting

**A scan finds nothing on a large repo.** Confirm the file types are in scope (`scan-code.py` only reads source/config extensions) and that you are not pointing at a single file when you meant a directory. Excluded dirs (`.git`, `node_modules`, `dist`, `build`, `venv`) are skipped on purpose.

**Detection misses an SSN you expected.** Check the format (`123-45-6789` vs `123456789`) and whether the value falls in an excluded never-issued range, which is treated as test data by design.

## Contributing

Useful contributions: new healthcare-format coverage, additional HIPAA rule mappings, language-specific detection patterns, and pre-commit/CI integrations. See the per-skill docs under [skills/](./skills/).

## License

MIT. See [LICENSE](./LICENSE).

Repository: [github.com/1Mangesh1/hipaa-guardian](https://github.com/1Mangesh1/hipaa-guardian)
