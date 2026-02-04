# dev-skills

A collection of AI agent skills for development, compliance, and security workflows.

## Installation

Works with 40+ AI coding agents including Claude Code, Cursor, Windsurf, Aider, Continue, Cline, and more.

### Install All Skills

```bash
npx skills add 1Mangesh1/dev-skills
```

### Install Specific Skill

```bash
npx skills add 1Mangesh1/dev-skills --skill hipaa-guardian
npx skills add 1Mangesh1/dev-skills --skill secret-scanner
npx skills add 1Mangesh1/dev-skills --skill gh-cli
```

## Available Skills

| Skill | Description | Version |
|-------|-------------|---------|
| [hipaa-guardian](./skills/hipaa-guardian/) | HIPAA compliance, PHI/PII detection, healthcare formats | 1.2.0 |
| [secret-scanner](./skills/secret-scanner/) | Secret detection, API keys, credentials (50+ providers) | 1.0.0 |
| [gh-cli](./skills/gh-cli/) | GitHub CLI for PRs, issues, releases, actions | 1.0.0 |
| [docker-helper](./skills/docker-helper/) | Docker & Compose commands, debugging, optimization | 1.0.0 |
| [git-hooks](./skills/git-hooks/) | Pre-commit hooks with Husky, lint-staged, pre-commit | 1.0.0 |
| [mcp-setup](./skills/mcp-setup/) | MCP server configuration for Claude integration | 1.0.0 |
| [jq-yq](./skills/jq-yq/) | JSON/YAML manipulation with jq and yq | 1.0.0 |
| [curl-http](./skills/curl-http/) | API testing with curl and HTTPie | 1.0.0 |
| [ssh-config](./skills/ssh-config/) | SSH keys, config, tunnels, jump hosts | 1.0.0 |
| [npm-scripts](./skills/npm-scripts/) | npm/yarn/pnpm scripts, workspaces, publishing | 1.0.0 |
| [makefile](./skills/makefile/) | GNU Make patterns for project automation | 1.0.0 |
| [dotfiles](./skills/dotfiles/) | Dotfile management with stow, chezmoi | 1.0.0 |

## Skills by Category

### Security & Compliance
- **hipaa-guardian** - HIPAA compliance, PHI/PII detection
- **secret-scanner** - API keys, tokens, credential detection

### Developer Tools
- **gh-cli** - GitHub CLI mastery
- **docker-helper** - Container operations
- **git-hooks** - Automated code quality
- **mcp-setup** - MCP server integration

### CLI Utilities
- **jq-yq** - JSON/YAML processing
- **curl-http** - HTTP request testing
- **ssh-config** - SSH management
- **npm-scripts** - Package management
- **makefile** - Build automation
- **dotfiles** - Config management

## Compatibility

| Agent | Status |
|-------|--------|
| Claude Code | Supported |
| Cursor | Supported |
| Windsurf | Supported |
| Aider | Supported |
| Continue | Supported |
| Cline | Supported |

## License

MIT

## Author

[1mangesh1](https://github.com/1Mangesh1)
