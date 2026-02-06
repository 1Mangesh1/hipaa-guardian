# Popular GitHub Actions Reference

## Official Actions

| Action | Purpose | Example |
|--------|---------|---------|
| `actions/checkout@v4` | Clone repository | `uses: actions/checkout@v4` |
| `actions/setup-node@v4` | Setup Node.js | `with: { node-version: 20, cache: npm }` |
| `actions/setup-python@v5` | Setup Python | `with: { python-version: "3.12", cache: pip }` |
| `actions/setup-go@v5` | Setup Go | `with: { go-version: "1.22" }` |
| `actions/cache@v4` | Cache dependencies | `with: { path: ..., key: ... }` |
| `actions/upload-artifact@v4` | Upload build artifact | `with: { name: build, path: dist/ }` |
| `actions/download-artifact@v4` | Download artifact | `with: { name: build }` |

## Community Actions

| Action | Purpose |
|--------|---------|
| `docker/build-push-action@v5` | Build & push Docker images |
| `docker/login-action@v3` | Login to container registry |
| `softprops/action-gh-release@v1` | Create GitHub releases |
| `peaceiris/actions-gh-pages@v3` | Deploy to GitHub Pages |
| `aws-actions/configure-aws-credentials@v4` | Configure AWS credentials |
| `google-github-actions/auth@v2` | Authenticate to Google Cloud |
| `azure/login@v1` | Login to Azure |
| `hashicorp/setup-terraform@v3` | Setup Terraform |
| `superfly/flyctl-actions/setup-flyctl@master` | Setup Fly.io CLI |
| `vercel/actions/cli@v2` | Deploy to Vercel |

## Action Patterns

### Composite Action

```yaml
# .github/actions/setup/action.yml
name: "Setup Project"
description: "Install dependencies and build"
inputs:
  node-version:
    description: "Node.js version"
    default: "20"
runs:
  using: "composite"
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - run: npm ci
      shell: bash
    - run: npm run build
      shell: bash

# Usage in workflow
- uses: ./.github/actions/setup
  with:
    node-version: "20"
```

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel previous runs on same branch
```

### Path Filtering

```yaml
on:
  push:
    paths:
      - "src/**"
      - "package.json"
    paths-ignore:
      - "**.md"
      - ".github/**"
```

### Status Checks

```yaml
# Required status check names should match job names
jobs:
  lint:       # ← This name appears in branch protection
    runs-on: ubuntu-latest
    steps: [...]
  test:       # ← This name appears in branch protection
    runs-on: ubuntu-latest
    steps: [...]
```
