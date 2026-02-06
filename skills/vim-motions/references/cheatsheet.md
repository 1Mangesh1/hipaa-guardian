# Vim Motions Cheat Sheet

## Movement

```
         gg (file top)
          |
     H ---+--- (screen top)
          |
0 ^ --h--+--l-- $ (line)
          |
     L ---+--- (screen bottom)
          |
         G (file bottom)

   k
 h   l
   j
```

## The Vim Language

```
[count] [operator] [motion/text-object]

Examples:
  3dw     = delete 3 words
  ci"     = change inside quotes
  y2j     = yank 2 lines down
  >ap     = indent around paragraph
  gUiw    = uppercase inner word
```

## Essential Combos

### Navigation
```
w/b         → Word forward/back
0/$         → Line start/end
gg/G        → File start/end
Ctrl-d/u    → Half page down/up
f{c}/F{c}   → Find char on line
*/#         → Search word under cursor
%           → Matching bracket
```

### Editing
```
ciw         → Change inner word
ci"/ci'     → Change inside quotes
ci(/ci{     → Change inside parens/braces
dit         → Delete inside HTML tag
yap         → Yank around paragraph
dd/yy       → Delete/yank line
D/C         → Delete/change to line end
o/O         → New line below/above
J           → Join lines
u / Ctrl-r  → Undo/redo
.           → Repeat last change
```

### Visual Mode
```
viw         → Select word
vi"         → Select inside quotes
vip         → Select paragraph
V           → Select line
Ctrl-v      → Column select
```

### Search & Replace
```
/pattern    → Search forward
?pattern    → Search backward
n/N         → Next/prev match
:%s/a/b/g   → Replace all in file
:s/a/b/g    → Replace all in line
:%s/a/b/gc  → Replace with confirm
```

### Multi-cursor (Visual Block)
```
Ctrl-v → select rows → I → type → ESC    (insert)
Ctrl-v → select rows → A → type → ESC    (append)
Ctrl-v → select rows → c → type → ESC    (change)
```

### Macros
```
qa          → Record macro 'a'
q           → Stop recording
@a          → Play macro 'a'
@@          → Replay last
10@a        → Play 10 times
```

## Surround (vim-surround / mini.surround)

```
cs"'        → Change surrounding " to '
ds"         → Delete surrounding "
ysiw"       → Add " around word
yss(        → Surround entire line with ()
S"          → Surround selection with " (visual mode)
```

## Comment (vim-commentary / Comment.nvim)

```
gcc         → Toggle comment line
gc          → Toggle comment (motion)
gcap        → Comment paragraph
gc          → Comment selection (visual)
```

## Most Used (Top 20)

```
 1. ciw    Change word
 2. ci"    Change inside quotes
 3. dd     Delete line
 4. yy     Yank line
 5. p/P    Paste after/before
 6. o/O    New line below/above
 7. w/b    Word forward/back
 8. f{c}   Find char
 9. /      Search
10. .      Repeat last change
11. u      Undo
12. gg/G   Top/bottom
13. 0/$    Line start/end
14. *      Search word
15. di"    Delete inside quotes
16. v/V    Visual select
17. >>     Indent
18. J      Join lines
19. A      Append at end
20. ~      Toggle case
```
