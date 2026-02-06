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
npx skills add 1Mangesh1/dev-skills --skill pytest
```

## Available Skills (32)

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
| [pytest](./skills/pytest/) | Python testing with fixtures, mocking, coverage | 1.0.0 |
| [jest-vitest](./skills/jest-vitest/) | JavaScript/TypeScript testing with Jest and Vitest | 1.0.0 |
| [github-actions](./skills/github-actions/) | CI/CD workflows, matrix builds, caching, secrets | 1.0.0 |
| [sql-migrations](./skills/sql-migrations/) | Database migrations with Prisma, Drizzle, raw SQL | 1.0.0 |
| [aws-cli](./skills/aws-cli/) | AWS CLI mastery, profiles, S3, EC2, Lambda | 1.0.0 |
| [kubernetes](./skills/kubernetes/) | kubectl, deployments, services, pod debugging | 1.0.0 |
| [terraform](./skills/terraform/) | Infrastructure as code, modules, state management | 1.0.0 |
| [python-env](./skills/python-env/) | Poetry, Pipenv, venv, pyenv, uv environment management | 1.0.0 |
| [regex](./skills/regex/) | Regular expression patterns, testing, common recipes | 1.0.0 |
| [git-advanced](./skills/git-advanced/) | Rebase, cherry-pick, bisect, reflog, recovery | 1.0.0 |
| [nginx](./skills/nginx/) | Web server config, reverse proxy, SSL/TLS | 1.0.0 |
| [redis](./skills/redis/) | Caching patterns, CLI, data structures, pub/sub | 1.0.0 |
| [graphql](./skills/graphql/) | Schema design, queries, mutations, tooling | 1.0.0 |
| [tmux](./skills/tmux/) | Terminal multiplexing, sessions, scripting | 1.0.0 |
| [vim-motions](./skills/vim-motions/) | Vim keybindings, motions, text objects for editors | 1.0.0 |
| [changelog](./skills/changelog/) | Changelogs, release notes, semantic versioning | 1.0.0 |
| [code-review](./skills/code-review/) | Code review checklists, PR review patterns | 1.0.0 |
| [dependency-audit](./skills/dependency-audit/) | Auditing & updating dependencies safely | 1.0.0 |
| [lint-format](./skills/lint-format/) | ESLint, Prettier, Ruff, Black, editorconfig setup | 1.0.0 |
| [env-debug](./skills/env-debug/) | Debugging PATH, permissions, env vars, configs | 1.0.0 |

## Skills by Category

### Security & Compliance
- **hipaa-guardian** - HIPAA compliance, PHI/PII detection
- **secret-scanner** - API keys, tokens, credential detection

### Testing
- **pytest** - Python testing with pytest
- **jest-vitest** - JavaScript/TypeScript testing

### CI/CD & Infrastructure
- **github-actions** - GitHub Actions workflows
- **kubernetes** - Kubernetes cluster management
- **terraform** - Infrastructure as code
- **aws-cli** - AWS CLI operations
- **nginx** - Web server configuration

### Database
- **sql-migrations** - Database migrations (Prisma, Drizzle, SQL)
- **redis** - Caching and data structures

### Developer Tools
- **gh-cli** - GitHub CLI mastery
- **docker-helper** - Container operations
- **git-hooks** - Automated code quality
- **git-advanced** - Advanced Git operations
- **mcp-setup** - MCP server integration
- **graphql** - GraphQL schema and queries

### CLI Utilities
- **jq-yq** - JSON/YAML processing
- **curl-http** - HTTP request testing
- **ssh-config** - SSH management
- **npm-scripts** - Package management
- **makefile** - Build automation
- **dotfiles** - Config management
- **tmux** - Terminal multiplexing
- **vim-motions** - Vim keybindings

### Language & Environment
- **python-env** - Python environment management
- **regex** - Regular expressions

### Boring Tasks Devs Hate (Automated!)
- **changelog** - Writing changelogs and release notes
- **code-review** - Code review checklists and feedback
- **dependency-audit** - Auditing and updating dependencies
- **lint-format** - Setting up linting and formatting
- **env-debug** - Debugging environment issues

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
