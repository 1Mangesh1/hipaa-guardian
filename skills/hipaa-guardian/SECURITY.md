# Security Policy

## Reporting Vulnerabilities

To report a security vulnerability, please open a GitHub issue at
[github.com/1Mangesh1/hipaa-guardian/issues](https://github.com/1Mangesh1/hipaa-guardian/issues)
with the label `security`. For sensitive disclosures, contact the maintainer directly.

---

## Trust Model & Verification

### Source Verification

This skill is published by **1Mangesh1** on GitHub. Before installing:

1. Review the source code at [github.com/1Mangesh1/hipaa-guardian](https://github.com/1Mangesh1/hipaa-guardian)
2. Inspect all scripts in `scripts/` before execution
3. Verify the repository's commit history and contributor list

### Package Integrity

After installing, verify file integrity using SHA-256 checksums:

```bash
# Generate checksums for installed scripts
shasum -a 256 scripts/*.py scripts/*.sh
```

You can compare against the checksums published in the repository's
`scripts/.checksums` file (when available) or against the source on GitHub.

### Script Integrity Checking

The pre-commit hook supports optional SHA-256 integrity verification.
To enable it, create a `scripts/.checksums` manifest:

```bash
cd skills/hipaa-guardian
shasum -a 256 scripts/*.py > scripts/.checksums
```

When the manifest exists, the pre-commit hook will verify each scanner script's
checksum before execution and refuse to run scripts that have been tampered with.

---

## Input Sanitization

### Indirect Prompt Injection Mitigation

This skill processes untrusted inputs (source code, data files, logs, healthcare
formats). The following safeguards are implemented to mitigate Indirect Prompt
Injection (Category 8) risks:

#### File Size Limits
All scanner scripts enforce a **10 MB maximum file size** (`MAX_FILE_SIZE_BYTES`).
Files exceeding this limit are silently skipped to prevent memory exhaustion and
output flooding attacks.

#### Finding Limits
- **Per-file limit:** 500 findings maximum (`MAX_FINDINGS_PER_FILE`)
- **Total limit:** 5,000 findings maximum (`MAX_TOTAL_FINDINGS`)

These caps prevent adversarial inputs from generating excessive output that could
overwhelm downstream consumers (including LLMs).

#### Output Boundary Markers
All scanner scripts wrap their stdout output in boundary markers:

```
--- HIPAA_GUARDIAN_SCAN_BEGIN ---
{ ... scan results ... }
--- HIPAA_GUARDIAN_SCAN_END ---
```

Downstream LLM consumers should only process content between these markers.
Content outside the markers is not part of the scan output.

#### Control Character Sanitization
All output strings are sanitized to strip control characters (`\x00`–`\x08`,
`\x0b`, `\x0c`, `\x0e`–`\x1f`) that could be used for injection when results
are consumed by LLMs or other agents. This applies to:
- File path strings in findings
- Context snippets around detections
- All user-facing output text

#### Path Sanitization
Input paths are resolved to absolute paths and stripped of null bytes and control
characters before processing. Symlinks are resolved to their real targets.

#### Safe File Validation
Before reading any file, scanners verify:
- The target is a regular file (not a device, pipe, symlink to device, etc.)
- The resolved path points to a real file
- The file size is within limits
- The file is readable

---

## Command Execution Controls

### Pre-Commit Hook Security

The `pre-commit-hook.sh` script executes Python scanner scripts from the skill
bundle. The following hardening measures are in place:

1. **Path Validation:** Scripts must pass `validate_script_path()` which checks:
   - Target is a regular file (not a symlink to arbitrary location)
   - Target has a `.py` extension (rejects non-Python executables)
   - Target is readable
   - Warns if the script is world-writable

2. **Integrity Verification:** When a `scripts/.checksums` manifest exists,
   `verify_script_integrity()` compares SHA-256 hashes before execution.
   Mismatches block execution entirely.

3. **Restricted Search Paths:** The hook searches for scanner scripts only in:
   - `$SCRIPT_DIR/` (same directory as the hook)
   - `$(dirname "$SCRIPT_DIR")/scripts/`
   - `$HOME/.claude/skills/hipaa-guardian/scripts/`
   - `./scripts/`

4. **No Arbitrary Execution:** The hook only invokes known scanner scripts
   (`detect-phi.py`, `scan-code.py`) via `python3` — it does not execute
   arbitrary commands or user-supplied scripts.

---

## Capability Inventory

This skill uses the following system capabilities:

| Capability | Usage | Scope |
|------------|-------|-------|
| File system read | Scanning source code, data files, configs | User-specified paths only |
| File system write | Writing scan reports to `--output` path | Only when explicitly requested |
| Shell execution | Pre-commit hook runs Python scanners | Restricted to known scripts |
| Glob/pattern matching | File discovery for scanning | Bounded by excluded directories |

### What This Skill Does NOT Do
- Does not make network requests
- Does not install packages or modify system state
- Does not access environment variables (except `HIPAA_*` config vars)
- Does not store PHI — only SHA-256 hashes of detected values
- Does not exfiltrate data

---

## PHI Handling Guardrails

1. **No PHI Storage:** Detected values are immediately hashed (`sha256:`); raw
   values are never stored or included in output.
2. **Redaction:** Context snippets redact detected values with `[REDACTED-SSN]`,
   `[REDACTED-PHONE]`, etc.
3. **Default Synthetic Mode:** The `--synthetic` flag treats all findings as test
   data. This is the recommended default.
4. **Temporary File Cleanup:** The pre-commit hook uses `trap` to ensure temp
   directories are always cleaned up, even on failure.
