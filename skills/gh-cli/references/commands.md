# gh CLI Command Reference

## Authentication

```bash
gh auth login                    # Interactive login
gh auth login --with-token < token.txt
gh auth status                   # Check auth status
gh auth refresh                  # Refresh credentials
gh auth switch                   # Switch accounts
```

## PR Commands

| Command | Description |
|---------|-------------|
| `gh pr create` | Create a pull request |
| `gh pr list` | List PRs |
| `gh pr view [number]` | View PR details |
| `gh pr checkout [number]` | Checkout PR branch |
| `gh pr merge [number]` | Merge PR |
| `gh pr close [number]` | Close PR |
| `gh pr reopen [number]` | Reopen PR |
| `gh pr review [number]` | Review PR |
| `gh pr diff [number]` | View PR diff |
| `gh pr checks [number]` | View PR checks |
| `gh pr ready [number]` | Mark as ready |
| `gh pr comment [number]` | Add comment |

### PR Create Flags

```bash
--title, -t        # PR title
--body, -b         # PR body
--base, -B         # Base branch (default: main)
--head, -H         # Head branch
--draft, -d        # Create as draft
--fill, -f         # Use commit info
--web, -w          # Open in browser
--assignee, -a     # Assign users
--label, -l        # Add labels
--reviewer, -r     # Request reviewers
--milestone, -m    # Set milestone
```

### PR Merge Flags

```bash
--merge, -m        # Merge commit
--squash, -s       # Squash and merge
--rebase, -r       # Rebase and merge
--delete-branch    # Delete branch after
--auto             # Auto-merge when checks pass
```

## Issue Commands

| Command | Description |
|---------|-------------|
| `gh issue create` | Create issue |
| `gh issue list` | List issues |
| `gh issue view [number]` | View issue |
| `gh issue close [number]` | Close issue |
| `gh issue reopen [number]` | Reopen issue |
| `gh issue comment [number]` | Add comment |
| `gh issue edit [number]` | Edit issue |
| `gh issue delete [number]` | Delete issue |
| `gh issue transfer [number]` | Transfer issue |
| `gh issue pin [number]` | Pin issue |

## Release Commands

| Command | Description |
|---------|-------------|
| `gh release create [tag]` | Create release |
| `gh release list` | List releases |
| `gh release view [tag]` | View release |
| `gh release delete [tag]` | Delete release |
| `gh release download [tag]` | Download assets |
| `gh release upload [tag]` | Upload assets |
| `gh release edit [tag]` | Edit release |

### Release Create Flags

```bash
--title, -t           # Release title
--notes, -n           # Release notes
--notes-file, -F      # Notes from file
--generate-notes      # Auto-generate notes
--draft, -d           # Create as draft
--prerelease, -p      # Mark as prerelease
--target              # Target commitish
--latest              # Mark as latest
```

## Workflow Commands

| Command | Description |
|---------|-------------|
| `gh run list` | List workflow runs |
| `gh run view [id]` | View run details |
| `gh run watch [id]` | Watch run progress |
| `gh run rerun [id]` | Rerun workflow |
| `gh run cancel [id]` | Cancel run |
| `gh run download [id]` | Download artifacts |
| `gh workflow list` | List workflows |
| `gh workflow view [name]` | View workflow |
| `gh workflow run [name]` | Trigger workflow |
| `gh workflow enable [name]` | Enable workflow |
| `gh workflow disable [name]` | Disable workflow |

## Repo Commands

| Command | Description |
|---------|-------------|
| `gh repo create` | Create repository |
| `gh repo clone` | Clone repository |
| `gh repo fork` | Fork repository |
| `gh repo view` | View repository |
| `gh repo list` | List repositories |
| `gh repo edit` | Edit repository |
| `gh repo delete` | Delete repository |
| `gh repo rename` | Rename repository |
| `gh repo archive` | Archive repository |
| `gh repo sync` | Sync fork |

## Search Commands

```bash
# Search issues/PRs
gh search issues "bug label:critical"
gh search prs "author:@me is:open"

# Search repos
gh search repos "language:python stars:>1000"

# Search code
gh search code "TODO filename:*.py"

# Search commits
gh search commits "fix bug repo:owner/repo"
```

## JSON Output

```bash
# Available for most commands
gh pr list --json number,title,state,author
gh issue list --json number,title,labels
gh run list --json status,conclusion,name

# With jq processing
gh pr list --json number,title --jq '.[0].title'
```

## Environment Variables

```bash
GH_TOKEN           # Auth token
GH_HOST            # GitHub host (for GHES)
GH_REPO            # Default repository
GH_EDITOR          # Editor for body text
GH_BROWSER         # Browser for --web
GH_PAGER           # Pager for output
NO_COLOR           # Disable colors
```

## Configuration

```bash
gh config set editor vim
gh config set git_protocol ssh
gh config set prompt disabled
gh config list
```
