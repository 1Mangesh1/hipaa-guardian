# Git Recovery Techniques

## Recovery Scenarios

### Accidentally Committed to Wrong Branch

```bash
# Move last commit to correct branch
git branch correct-branch     # Create branch at current commit
git reset --hard HEAD~1       # Remove from current branch
git checkout correct-branch   # Switch to correct branch
```

### Accidentally Deleted a Branch

```bash
# Find the branch tip in reflog
git reflog | grep "branch-name"

# Or find by last known commit message
git reflog | grep "commit message"

# Recreate the branch
git checkout -b branch-name <commit-hash>
```

### Lost Commits After Hard Reset

```bash
# View all recent HEAD positions
git reflog

# Find the commit before the reset
# Example output: abc1234 HEAD@{3}: commit: Add feature X

# Recover
git reset --hard abc1234
# OR create a new branch
git checkout -b recovery abc1234
```

### Messed Up a Rebase

```bash
# Find the pre-rebase state in reflog
git reflog
# Look for: "rebase (start): checkout main"
# The entry BEFORE that is your pre-rebase state

git reset --hard HEAD@{N}  # N = position before rebase
```

### Accidentally Deleted a File

```bash
# File deleted but not committed
git checkout -- path/to/file

# File deleted and committed
git checkout HEAD~1 -- path/to/file

# Find when file was deleted
git log --all --full-history -- path/to/file
git checkout <last-commit-with-file> -- path/to/file
```

### Undo a Merge

```bash
# Merge not yet pushed
git reset --hard HEAD~1   # or ORIG_HEAD

# Merge already pushed (creates revert commit)
git revert -m 1 <merge-commit-hash>
```

### Fix Last Commit Message

```bash
# Not yet pushed
git commit --amend -m "New message"

# Already pushed (requires force push - coordinate with team!)
git commit --amend -m "New message"
git push --force-with-lease
```

### Remove Sensitive Data from History

```bash
# Using git-filter-repo (recommended)
pip install git-filter-repo

# Remove file from all history
git filter-repo --path secrets.env --invert-paths

# Replace text in all files
git filter-repo --replace-text replacements.txt
# replacements.txt format:
# SECRET_KEY=abc123==>SECRET_KEY=REDACTED
```

## Reflog Reference

```bash
# View with timestamps
git reflog --date=iso

# View for specific branch
git reflog show feature-branch

# Search reflog
git reflog | grep "pattern"

# Reflog retention (defaults)
# Reachable: 90 days
# Unreachable: 30 days

# Extend retention
git config gc.reflogExpire "180 days"
git config gc.reflogExpireUnreachable "90 days"
```

## ORIG_HEAD

```bash
# Git sets ORIG_HEAD before dangerous operations
# Available after: merge, rebase, reset

# Undo last merge
git reset --hard ORIG_HEAD

# Undo last rebase
git reset --hard ORIG_HEAD

# View what ORIG_HEAD points to
git log -1 ORIG_HEAD
```

## Dangling Objects

```bash
# Find dangling commits (not on any branch)
git fsck --no-reflogs

# Show a dangling commit
git show <dangling-commit-hash>

# Recover dangling commit
git checkout -b recovery <dangling-commit-hash>

# Find dangling blobs (deleted files)
git fsck --lost-found
# Recoverable files appear in .git/lost-found/
```

## Prevention Tips

```bash
# Always use --force-with-lease instead of --force
git push --force-with-lease

# Set up branch protection on main/production

# Create backup tags before risky operations
git tag backup-before-rebase
# After success: git tag -d backup-before-rebase

# Use worktrees for risky experiments
git worktree add ../experiment feature-branch
```
