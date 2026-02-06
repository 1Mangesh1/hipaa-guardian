---
name: tmux
description: Terminal multiplexer mastery for sessions, windows, panes, and scripting. Use when user asks to "set up tmux", "split terminal", "tmux keybindings", "create tmux session", "tmux config", "tmux script", or any terminal multiplexing tasks.
---

# tmux

Terminal multiplexing for sessions, windows, and panes.

## Sessions

```bash
# New session
tmux new -s dev
tmux new-session -s dev

# Detach from session
# Prefix + d (Ctrl-b, then d)

# List sessions
tmux ls
tmux list-sessions

# Attach to session
tmux attach -t dev
tmux a -t dev

# Kill session
tmux kill-session -t dev

# Rename session
# Prefix + $
tmux rename-session -t old new

# Switch between sessions
# Prefix + s (session list)
# Prefix + ( (previous session)
# Prefix + ) (next session)
```

## Windows (Tabs)

```bash
# Prefix = Ctrl-b (default)

# New window
# Prefix + c

# Switch windows
# Prefix + 0-9    (by number)
# Prefix + n      (next)
# Prefix + p      (previous)
# Prefix + w      (window list)
# Prefix + l      (last window)

# Rename window
# Prefix + ,

# Close window
# Prefix + &
# Or: exit

# Move window
# Prefix + .  (move to number)
```

## Panes (Splits)

```bash
# Split horizontal
# Prefix + "

# Split vertical
# Prefix + %

# Navigate panes
# Prefix + arrow keys
# Prefix + o      (cycle)
# Prefix + q      (show numbers, then press number)

# Resize panes
# Prefix + Ctrl-arrow   (resize by 1)
# Prefix + Alt-arrow    (resize by 5)

# Zoom pane (toggle fullscreen)
# Prefix + z

# Close pane
# Prefix + x
# Or: exit

# Convert pane to window
# Prefix + !

# Swap panes
# Prefix + {    (swap with previous)
# Prefix + }    (swap with next)

# Toggle layouts
# Prefix + Space
```

## Copy Mode

```bash
# Enter copy mode
# Prefix + [

# Navigation (vi mode)
# h j k l     - Move
# w b         - Word forward/back
# / ?         - Search forward/back
# n N         - Next/prev search result
# g G         - Top/bottom

# Selection (vi mode)
# Space       - Start selection
# Enter       - Copy and exit
# v           - Toggle rectangle selection

# Paste
# Prefix + ]

# Enable vi mode in .tmux.conf:
# set-window-option -g mode-keys vi
```

## Command Mode

```bash
# Enter command mode
# Prefix + :

# Common commands
:new-window -n "editor"
:split-window -h
:resize-pane -D 10
:swap-pane -D
:setw synchronize-panes on   # Type in all panes
:setw synchronize-panes off
```

## Scripting

```bash
#!/bin/bash
# dev-setup.sh - Create development workspace

SESSION="dev"

# Create session with first window
tmux new-session -d -s $SESSION -n "editor"
tmux send-keys -t $SESSION:editor "vim ." Enter

# Second window: server
tmux new-window -t $SESSION -n "server"
tmux send-keys -t $SESSION:server "npm run dev" Enter

# Third window: split for tests and logs
tmux new-window -t $SESSION -n "test"
tmux split-window -h -t $SESSION:test
tmux send-keys -t $SESSION:test.0 "npm test -- --watch" Enter
tmux send-keys -t $SESSION:test.1 "tail -f logs/app.log" Enter

# Fourth window: git
tmux new-window -t $SESSION -n "git"
tmux send-keys -t $SESSION:git "git status" Enter

# Focus first window
tmux select-window -t $SESSION:editor

# Attach
tmux attach -t $SESSION
```

## .tmux.conf

```bash
# ~/.tmux.conf

# Change prefix to Ctrl-a
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Enable mouse
set -g mouse on

# Start windows at 1 (not 0)
set -g base-index 1
setw -g pane-base-index 1

# Vi mode
setw -g mode-keys vi

# Vi copy mode
bind -T copy-mode-vi v send -X begin-selection
bind -T copy-mode-vi y send -X copy-pipe-and-cancel "pbcopy"

# Better splits (use | and -)
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"

# New window in current path
bind c new-window -c "#{pane_current_path}"

# Resize panes with vim keys
bind -r H resize-pane -L 5
bind -r J resize-pane -D 5
bind -r K resize-pane -U 5
bind -r L resize-pane -R 5

# Switch panes with vim keys
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R

# Reload config
bind r source-file ~/.tmux.conf \; display "Reloaded!"

# Status bar
set -g status-style 'bg=#333333 fg=#ffffff'
set -g status-left ' #S '
set -g status-right ' %H:%M '

# History limit
set -g history-limit 50000

# No delay for escape
set -sg escape-time 0

# 256 colors
set -g default-terminal "screen-256color"
set -ga terminal-overrides ",*256col*:Tc"

# Auto rename windows
setw -g automatic-rename on
set -g renumber-windows on
```

## Quick Reference

```
Prefix = Ctrl-b (default) or Ctrl-a (if remapped)

Sessions:  d=detach  s=list  $=rename  (/)=prev/next
Windows:   c=new  ,=rename  n/p=next/prev  0-9=switch  &=kill
Panes:     "=hsplit  %=vsplit  arrows=navigate  z=zoom  x=kill
Copy:      [=enter  Space=select  Enter=copy  ]=paste
Command:   :=prompt
```

## Reference

For .tmux.conf customization: `references/config.md`
