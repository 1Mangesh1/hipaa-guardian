---
name: changelog
description: Changelog generation, release notes, and semantic versioning. Use when user asks to "write a changelog", "generate release notes", "bump version", "follow conventional commits", "create a release", "update CHANGELOG.md", or any versioning and release documentation tasks.
---

# Changelog & Release Notes

Changelog generation, semantic versioning, and release management.

## Conventional Commits

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

```
feat:     New feature (bumps MINOR)
fix:      Bug fix (bumps PATCH)
docs:     Documentation only
style:    Formatting, no code change
refactor: Code change, no feature/fix
perf:     Performance improvement
test:     Adding/fixing tests
build:    Build system, dependencies
ci:       CI configuration
chore:    Other changes (no src/test)

BREAKING CHANGE: in footer (bumps MAJOR)
feat!: or fix!: breaking change shorthand
```

### Examples

```
feat(auth): add OAuth2 login flow
fix(api): handle null response from payment gateway
docs: update API authentication guide
refactor(db): extract connection pooling to module
perf: optimize image loading with lazy load

feat!: redesign user API endpoints

BREAKING CHANGE: /api/users now returns paginated results
```

## Semantic Versioning

```
MAJOR.MINOR.PATCH

1.0.0 → 1.0.1  (fix: patch)
1.0.1 → 1.1.0  (feat: minor)
1.1.0 → 2.0.0  (BREAKING CHANGE: major)

Pre-release: 1.0.0-alpha.1, 1.0.0-beta.2, 1.0.0-rc.1
```

### Version Bump Commands

```bash
# npm
npm version patch   # 1.0.0 → 1.0.1
npm version minor   # 1.0.0 → 1.1.0
npm version major   # 1.0.0 → 2.0.0
npm version prerelease --preid=beta  # 1.0.0 → 1.0.1-beta.0

# Python (bump2version)
pip install bump2version
bump2version patch
bump2version minor
bump2version major
```

## CHANGELOG.md Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New user dashboard with analytics

### Changed
- Updated password requirements to 12 characters minimum

### Fixed
- Fix memory leak in WebSocket handler

## [2.1.0] - 2024-03-15

### Added
- OAuth2 login with Google and GitHub
- Rate limiting on API endpoints
- Export data to CSV

### Changed
- Upgrade Node.js to v20 LTS
- Migrate from Express to Fastify

### Deprecated
- Legacy /api/v1 endpoints (use /api/v2)

### Fixed
- Fix race condition in concurrent file uploads
- Fix incorrect timezone in scheduled reports

### Security
- Update jsonwebtoken to fix CVE-2024-XXXX

## [2.0.0] - 2024-02-01

### Changed
- **BREAKING**: Redesign API response format
- **BREAKING**: Require Node.js 18+

### Removed
- **BREAKING**: Remove XML response format
```

## Automated Changelog Tools

### conventional-changelog

```bash
npm install -D conventional-changelog-cli

# Generate changelog
npx conventional-changelog -p angular -i CHANGELOG.md -s

# First release (rewrite entire changelog)
npx conventional-changelog -p angular -i CHANGELOG.md -s -r 0
```

### standard-version / release-please

```bash
# standard-version
npm install -D standard-version
npx standard-version                # Auto bump + changelog
npx standard-version --first-release
npx standard-version --prerelease beta
npx standard-version --dry-run      # Preview

# Google release-please (GitHub Action)
# .github/workflows/release.yml
# Uses commits to auto-create release PRs
```

### Release Please GitHub Action

```yaml
name: Release
on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          release-type: node
```

### git-cliff

```bash
# Install
cargo install git-cliff

# Generate changelog
git cliff -o CHANGELOG.md

# Since last tag
git cliff --latest -o CHANGELOG.md

# Custom template
git cliff --config cliff.toml
```

## Release Notes Template

```markdown
## v2.1.0 Release Notes

### Highlights
- **OAuth2 Support**: Login with Google and GitHub accounts
- **Performance**: 40% faster API response times

### What's New
- OAuth2 login flow with Google and GitHub providers
- Rate limiting (100 req/min for API, 1000 for authenticated)
- CSV data export for all report types

### Bug Fixes
- Fixed memory leak in WebSocket connection handler
- Fixed incorrect timezone display in scheduled reports
- Fixed file upload race condition with concurrent requests

### Breaking Changes
None in this release.

### Upgrade Guide
```bash
npm install myapp@2.1.0
npx myapp migrate
```

### Contributors
@alice, @bob, @charlie
```

## Reference

For automated tooling and CI integration: `references/tools.md`
