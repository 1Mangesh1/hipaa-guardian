# Changelog Tools Reference

## Tool Comparison

| Tool | Type | Auto-bump | Lock to Conventional Commits | Platform |
|------|------|-----------|------------------------------|----------|
| conventional-changelog | CLI | No | Yes | Any |
| standard-version | CLI | Yes | Yes | Any |
| release-please | GitHub Action | Yes | Yes | GitHub |
| git-cliff | CLI | No | No (flexible) | Any |
| changesets | CLI | Yes | No (manual) | Any |
| semantic-release | CI | Yes | Yes | Any CI |

## Changesets (Monorepo-Friendly)

```bash
# Setup
npm install -D @changesets/cli
npx changeset init

# Create changeset
npx changeset
# Interactive prompt:
# - Which packages changed?
# - Semver bump type?
# - Summary of changes?

# Creates: .changeset/<random-name>.md

# Apply changesets (CI)
npx changeset version    # Update versions + CHANGELOG
npx changeset publish    # Publish to npm
```

### Changeset File

```markdown
---
"@myorg/package-a": minor
"@myorg/package-b": patch
---

Add new authentication flow with OAuth2 support.
Fix token refresh race condition.
```

## semantic-release

```bash
npm install -D semantic-release

# .releaserc.json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/npm",
    "@semantic-release/github",
    "@semantic-release/git"
  ]
}
```

```yaml
# GitHub Action
name: Release
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

## git-cliff Configuration

```toml
# cliff.toml
[changelog]
header = "# Changelog\n"
body = """
{% for group, commits in commits | group_by(attribute="group") %}
### {{ group | upper_first }}
{% for commit in commits %}
- {{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end="") }})
{% endfor %}
{% endfor %}
"""
trim = true

[git]
conventional_commits = true
filter_unconventional = true
commit_parsers = [
    { message = "^feat", group = "Features" },
    { message = "^fix", group = "Bug Fixes" },
    { message = "^doc", group = "Documentation" },
    { message = "^perf", group = "Performance" },
    { message = "^refactor", group = "Refactoring" },
    { message = "^style", skip = true },
    { message = "^test", group = "Testing" },
    { message = "^chore", skip = true },
]
```

## Commit Linting

```bash
# Install commitlint
npm install -D @commitlint/cli @commitlint/config-conventional

# commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
};

# With husky
echo "npx --no -- commitlint --edit \$1" > .husky/commit-msg
```
