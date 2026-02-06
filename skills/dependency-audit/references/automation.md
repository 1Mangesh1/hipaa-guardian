# Dependency Audit Automation

## CI/CD Integration

### npm Audit in CI

```yaml
# .github/workflows/audit.yml
name: Security Audit
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 8 * * 1"  # Weekly Monday 8am

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm audit --audit-level=moderate
      - run: npx license-checker --onlyAllow "MIT;ISC;BSD-3-Clause;Apache-2.0"
```

### Python Audit in CI

```yaml
name: Python Security
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt
```

## Automated Update Strategies

### Safe Auto-Merge Rules

```yaml
# .github/workflows/auto-merge-deps.yml
name: Auto-merge Dependency Updates
on: pull_request

permissions:
  contents: write
  pull-requests: write

jobs:
  auto-merge:
    if: |
      github.actor == 'dependabot[bot]' ||
      github.actor == 'renovate[bot]'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm test
      - uses: dependabot/fetch-metadata@v2
        id: metadata
        if: github.actor == 'dependabot[bot]'
      - if: |
          steps.metadata.outputs.update-type == 'version-update:semver-patch' ||
          steps.metadata.outputs.update-type == 'version-update:semver-minor'
        run: gh pr merge --auto --squash "$PR_URL"
        env:
          PR_URL: ${{ github.event.pull_request.html_url }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Grouped Updates

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      # Group all dev dependencies together
      dev-dependencies:
        dependency-type: "development"
      # Group linting tools
      linting:
        patterns:
          - "eslint*"
          - "prettier*"
          - "@typescript-eslint/*"
      # Group testing tools
      testing:
        patterns:
          - "jest*"
          - "@testing-library/*"
          - "vitest*"
      # Group AWS SDK
      aws:
        patterns:
          - "@aws-sdk/*"
```

## Monitoring Dashboards

### Socket.dev

```
- Integrates with GitHub
- Detects supply chain attacks
- Monitors for suspicious package behavior
- Free for open source
```

### Snyk

```bash
# CLI usage
npm install -g snyk
snyk auth
snyk test
snyk monitor  # Continuous monitoring
```

### GitHub Security Features

```
1. Dependabot alerts (auto-enabled)
2. Dependabot security updates (auto PRs for vulns)
3. Code scanning (CodeQL)
4. Secret scanning

Settings → Security → Enable all
```

## Slack/Email Notifications

```yaml
# Add to audit workflow
- if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {"text": "Security audit failed in ${{ github.repository }}"}
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```
