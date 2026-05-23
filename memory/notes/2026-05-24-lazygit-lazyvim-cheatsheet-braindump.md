---
date: 2026-05-24
type: cheatsheet
tags: [lazygit, lazyvim, devtools, workflow]
related: []
---

# LazyGit + LazyVim Cheatsheet

## LazyVim

**Default leader key: `<Space>`**

### Navigation & Buffers
| Key | Action |
|-----|--------|
| `]b` / `[b` | Next / previous buffer |
| `<leader>bb` | Buffer picker |
| `<leader>bd` | Delete buffer |
| `<leader>bD` | Force-delete buffer |
| `gf` | Go to file under cursor |
| `gD` | Go to declaration |
| `<C-o>` / `<C-i>` | Jump back / forward |
| `gd` | Go to definition |

### Window Splitting & Navigation
| Key | Action |
|-----|--------|
| `<leader>wv` | Vertical split |
| `<leader>ws` | Horizontal split |
| `<C-h/j/k/l>` | Move between windows |
| `<leader>wd` | Close window |
| `<leader>w>` | Increase width |
| `<leader>w<` | Decrease width |
| `<leader>w+` | Increase height |
| `<leader>w-` | Decrease height |

### File Explorer (Neo-tree)
| Key | Action |
|-----|--------|
| `<leader>e` | Toggle neo-tree |
| `a` | Add file/folder |
| `d` | Delete |
| `r` | Rename |
| `m` | Move |
| `y` | Copy path |
| `H` / `L` | Toggle hidden / last sibling |

### Terminal
| Key | Action |
|-----|--------|
| `<C-/>` | Toggle built-in terminal (horizontal) |
| `<leader>ft` | Terminal in floating window |
| `<C-\>` | Toggle terminal (vertical split, custom) |

### Save / Quit
| Key | Action |
|-----|--------|
| `:w` | Save file |
| `:q` | Quit |
| `:q!` | Force quit (discard changes) |
| `:wq` / `:x` | Save and quit |
| `<leader>qq` | Quit all (LazyVim) |
| `<leader>qa` | Quit all without saving |

### User Shortcuts (custom)
| Key | Action |
|-----|--------|
| `Ctrl + g g` | Toggle LazyGit |
| `Ctrl + e` | Toggle file explorer |
| `Ctrl + f t` | Terminal float |

---

## LazyGit

### File Staging
| Key | Action |
|-----|--------|
| `<Space>` | Stage / unstage file or hunk |
| `a` | Stage all files |
| `1` | Files panel |
| `2` | Branches panel |
| `3` | Commits/log panel |
| `4` | Stash panel |
| `5` | Status panel |
| `Tab` | Switch between panels |
| `<Enter>` | Expand file to view hunks |
| `<Enter>` (on hunk) | Stage / unstage single line? (opens hunk detail) |
| `d` | Discard unstaged change |
| `D` | Discard staged + unstaged change |
| `z` | Undo last action |

### Committing
| Key | Action |
|-----|--------|
| `c` | Commit (opens commit message editor) |
| `C` | Commit menu (amend, signed, etc.) |
| `A` | Amend last commit (keeps old message) |
| `a` (Commit menu) | Amend with new message |
| `c` (Commit menu) | Commit without pre-commit hooks |
| `m` | Merge with selected branch |

#### CLI: Reset commit author/timestamp to now
```bash
git commit --amend --reset-author --no-edit
```
Amends the last commit, resets author + committer timestamp to the current time, keeps existing message.

### Squashing & Rebasing
| Key | Action |
|-----|--------|
| `r` | Rebase branch onto selected branch |
| `i` | Start interactive rebase (on branch commits) |
| `s` | Squash commit into previous (in rebase) |
| `f` | Fixup commit (squash, discard message) |
| `d` | Drop commit (in rebase) |
| `e` | Edit commit message (in rebase) |
| `j` / `k` | Move commit down / up (reorder) |
| `Ctrl+s` | Squash all commits above into selected |

### One-Commit PR Workflow
1. In LazyGit: `i` to enter interactive rebase on current branch
2. `Ctrl+s` to squash all commits into one
3. Edit the final commit message, confirm
4. `P` to force-push to remote (uses `--force-with-lease`)
5. Open PR via GitHub CLI or browser

### Undo / Soft Reset
| Key | Action |
|-----|--------|
| `z` | Undo last Git operation (LazyGit reflog) |
| `g` then `s` | Soft reset to selected commit (keeps changes staged) |
| `g` then `m` | Mixed reset to selected commit (keeps changes unstaged) |
| `g` then `h` | Hard reset to selected commit (discards changes) |
| `g` | Opens reset menu on selected commit |

### Force Push Safety
| Key | Action |
|-----|--------|
| `P` | Force push (uses `--force-with-lease` by default) |
| `p` | Normal push |
| **Never** use `git push --force` directly — LazyGit uses `--force-with-lease` |

### Worktree Commands
| Key | Action |
|-----|--------|
| `w` | Open worktree menu |
| `n` (in worktree menu) | Create new worktree |
| `d` (in worktree menu) | Remove worktree |
| `b` (in worktree menu) | Checkout branch in worktree |

---

## Windows / File Explorer

| Key | Action |
|-----|--------|
| `explorer .` | Open File Explorer in current directory (from terminal) |
| `ii .` | Open current dir in File Explorer (pwsh alias) |
| `start .` | Open current dir in File Explorer (cmd) |
| `Ctrl+L` | Focus address bar |
| `F2` | Rename selected file |
| `Shift + Right Click` | Copy file path |
| `Alt+D` | Focus address bar |


## Emergency Git Recovery

### Recover Lost Commits
```bash
git reflog                              # Show all HEAD movements
git checkout HEAD@{n}                   # Jump to a lost commit
git branch recovery-branch HEAD@{n}     # Create branch at lost commit
```

### Recover from Bad Rebase
```bash
git rebase --abort                      # Abort in-progress rebase
git reflog                              # Find pre-rebase HEAD
git reset --hard HEAD@{n}               # Hard-reset back to pre-rebase state
```

### Recover from Detached HEAD
```bash
git branch save-point                   # Create branch from current detached commit
git checkout save-point                 # Switch to it
# OR:
git checkout -                          # Return to previous branch
```

### Recover Stashed Changes After Drop
```bash
git fsck --unreachable | grep commit    # Find dangling commits
git show <sha>                          # Inspect each to find your stash
git stash apply <sha>                   # Recover the stash
```
