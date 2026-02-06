# tmux Configuration Reference

## Minimal Config

```bash
# ~/.tmux.conf

# Remap prefix to Ctrl-a
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# Mouse support
set -g mouse on

# Vi mode
setw -g mode-keys vi

# Better splits
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# Reload
bind r source-file ~/.tmux.conf \; display "Reloaded"
```

## Full Config

```bash
# ~/.tmux.conf

# ---- General ----
set -g default-terminal "tmux-256color"
set -ga terminal-overrides ",*256col*:Tc"
set -g history-limit 50000
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
set -sg escape-time 0
set -g focus-events on
set -g set-clipboard on

# ---- Prefix ----
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# ---- Mouse ----
set -g mouse on

# ---- Vi Mode ----
setw -g mode-keys vi
bind -T copy-mode-vi v send -X begin-selection
bind -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"
bind -T copy-mode-vi MouseDragEnd1Pane send -X copy-pipe-and-cancel "pbcopy"

# ---- Navigation ----
# Split panes
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
unbind '"'
unbind %

# New window in current path
bind c new-window -c "#{pane_current_path}"

# Vim-style pane switching
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Vim-style pane resizing
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

# Alt-arrow pane switching (no prefix)
bind -n M-Left select-pane -L
bind -n M-Right select-pane -R
bind -n M-Up select-pane -U
bind -n M-Down select-pane -D

# Shift-arrow window switching (no prefix)
bind -n S-Left previous-window
bind -n S-Right next-window

# ---- Status Bar ----
set -g status-position bottom
set -g status-interval 5
set -g status-style "bg=#1a1b26 fg=#a9b1d6"
set -g status-left-length 30
set -g status-right-length 50
set -g status-left "#[fg=#7aa2f7,bold] #S #[fg=#565f89]| "
set -g status-right "#[fg=#565f89]| #[fg=#a9b1d6]%H:%M #[fg=#565f89]| #[fg=#a9b1d6]%d-%b "

# Window status
setw -g window-status-format "#[fg=#565f89] #I:#W "
setw -g window-status-current-format "#[fg=#7aa2f7,bold] #I:#W "

# ---- Pane Borders ----
set -g pane-border-style "fg=#565f89"
set -g pane-active-border-style "fg=#7aa2f7"

# ---- Messages ----
set -g message-style "bg=#1a1b26 fg=#7aa2f7"

# ---- Misc ----
bind r source-file ~/.tmux.conf \; display "Config reloaded"
bind S command-prompt -p "New session:" "new-session -s '%%'"
bind K confirm-before -p "Kill session? (y/n)" kill-session

# Synchronize panes toggle
bind Y setw synchronize-panes \; display "Sync #{?pane_synchronized,ON,OFF}"
```

## Plugin Manager (TPM)

```bash
# Install TPM
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

# Add to .tmux.conf
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-sensible'
set -g @plugin 'tmux-plugins/tmux-resurrect'
set -g @plugin 'tmux-plugins/tmux-continuum'
set -g @plugin 'tmux-plugins/tmux-yank'

# Initialize (keep at bottom of .tmux.conf)
run '~/.tmux/plugins/tpm/tpm'

# Install plugins: Prefix + I
# Update plugins: Prefix + U
```

## Popular Plugins

| Plugin | Purpose |
|--------|---------|
| tmux-sensible | Sensible defaults |
| tmux-resurrect | Save/restore sessions |
| tmux-continuum | Auto-save sessions |
| tmux-yank | System clipboard |
| tmux-fzf | Fuzzy finder integration |
| tmux-thumbs | Copy text with hints |

## Session Templates

```bash
# Project template script
#!/bin/bash
tmux has-session -t myproject 2>/dev/null
if [ $? != 0 ]; then
  tmux new-session -d -s myproject -n editor -c ~/projects/myproject
  tmux send-keys -t myproject:editor "nvim ." Enter

  tmux new-window -t myproject -n server -c ~/projects/myproject
  tmux send-keys -t myproject:server "npm run dev" Enter

  tmux new-window -t myproject -n term -c ~/projects/myproject

  tmux select-window -t myproject:editor
fi
tmux attach -t myproject
```
