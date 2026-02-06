# Environment Troubleshooting Guide

## Common Error Messages

### "EACCES: permission denied"

```bash
# npm global installs
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Alternative: use nvm (manages its own directory)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
```

### "ENOSPC: System limit for file watchers reached"

```bash
# Linux: increase inotify watchers
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### "error:0308010C:digital envelope routines::unsupported"

```bash
# Node.js 17+ with older webpack/tools
export NODE_OPTIONS=--openssl-legacy-provider

# Better fix: update webpack and dependencies
```

### "SSL: CERTIFICATE_VERIFY_FAILED" (Python)

```bash
# macOS: Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or install certifi
pip install certifi

# Environment variable workaround (not recommended for production)
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
```

### "gyp ERR! build error" (node-gyp)

```bash
# macOS
xcode-select --install

# Ubuntu
sudo apt install build-essential python3

# Windows
npm install --global windows-build-tools
```

## Tool-Specific Debugging

### nvm Issues

```bash
# nvm not found after install
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Node version resets between terminals
nvm alias default 20    # Set persistent default

# .nvmrc not auto-switching
# Add to ~/.zshrc:
autoload -U add-zsh-hook
load-nvmrc() {
  if [[ -f .nvmrc && -r .nvmrc ]]; then
    nvm use
  fi
}
add-zsh-hook chpwd load-nvmrc
load-nvmrc
```

### pyenv Issues

```bash
# Python build fails
# macOS
brew install openssl readline sqlite3 xz zlib
CFLAGS="-I$(brew --prefix openssl)/include" \
LDFLAGS="-L$(brew --prefix openssl)/lib" \
pyenv install 3.12.1

# Ubuntu
sudo apt install build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev libffi-dev

# pyenv not in PATH
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

### Docker Issues

```bash
# Docker daemon not running
# macOS: Open Docker Desktop
# Linux:
sudo systemctl start docker
sudo systemctl enable docker

# Permission denied
sudo usermod -aG docker $USER
newgrp docker  # Apply without logout

# No space left on device
docker system prune -a --volumes
docker builder prune

# DNS resolution fails in container
# Docker Desktop → Settings → Docker Engine:
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

### Git Issues

```bash
# SSL certificate problem
git config --global http.sslVerify false  # Temporary!
# Better: install proper CA certificates

# Authentication failed
# Use SSH key instead of password
gh auth login
# Or: git credential-store

# Line ending issues (Windows/Mac)
git config --global core.autocrlf input   # Mac/Linux
git config --global core.autocrlf true    # Windows
```

## System-Level Debugging

### macOS

```bash
# Xcode command line tools
xcode-select --install

# Homebrew doctor
brew doctor
brew update && brew upgrade

# Reset Homebrew
brew cleanup -s
```

### Linux (Ubuntu/Debian)

```bash
# Fix broken packages
sudo apt --fix-broken install
sudo dpkg --configure -a

# Update package index
sudo apt update

# Install build essentials
sudo apt install build-essential curl git
```

### WSL (Windows Subsystem for Linux)

```bash
# Network issues
# In PowerShell (admin):
wsl --shutdown
# Restart WSL

# File system slow
# Use /home/user/ for projects, not /mnt/c/

# systemd not available (WSL1)
# Use WSL2: wsl --set-version <distro> 2
```

## Health Check Script

```bash
#!/bin/bash
echo "=== Environment Health Check ==="
echo ""

# Shell
echo "Shell: $SHELL"
echo "Terminal: $TERM"
echo ""

# Tools
tools=("git" "node" "npm" "python3" "pip3" "docker" "curl" "ssh")
for tool in "${tools[@]}"; do
  if command -v "$tool" &>/dev/null; then
    ver=$("$tool" --version 2>&1 | head -1)
    printf "✓ %-10s %s\n" "$tool" "$ver"
  else
    printf "✗ %-10s NOT FOUND\n" "$tool"
  fi
done
echo ""

# Disk
echo "Disk Usage:"
df -h / | tail -1 | awk '{print "  Used: "$3" / "$2" ("$5")"}'
echo ""

# Memory
if [[ "$(uname)" == "Darwin" ]]; then
  echo "Memory: $(sysctl -n hw.memsize | awk '{print $1/1024/1024/1024" GB"}')"
else
  free -h | awk '/Mem:/{print "Memory: "$3" / "$2}'
fi
```
