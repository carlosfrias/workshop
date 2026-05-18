# Zellij: Terminal Multiplexer for pi

**Zellij** is a modern terminal multiplexer written in Rust, designed as an easier-to-use alternative to tmux. It provides discoverable keybindings, visual session management, and works seamlessly with pi.

---

## Quick Start

### Installation (macOS)

```bash
# Homebrew (easiest)
brew install zellij

# Or try without installing first
bash <(curl -L zellij.dev/launch)

# Or download pre-built binary
curl -LO https://github.com/zellij-org/zellij/releases/latest/download/zellij-aarch64-apple-darwin.tar.gz
tar -xvf zellij*.tar.gz
./zellij
```

### First Run

```bash
# Start zellij
zellij

# Or start with welcome screen (visual session selector)
zellij -l welcome
```

---

## Why Zellij for pi?

| Feature | tmux | Zellij |
|---------|------|--------|
| **Learning curve** | 2-4 weeks | Minutes to hours |
| **Keybinding hints** | ❌ Must memorize | ✅ Press `Ctrl+?` to see all |
| **Default panes** | Manual splits | `Alt+n`, `Alt+-`, `Alt+%` |
| **Mouse support** | Basic | Full (drag resize, click URLs) |
| **Configuration** | Complex `.tmux.conf` | Simpler `config.kdl` |
| **Session UI** | Command-line | Visual selector |
| **Memory usage** | ~6MB | ~80MB |

**Best for:** Users who want tmux functionality without the steep learning curve.

---

## Essential Keybindings

Press **`Ctrl + ?`** inside Zellij to see all keybindings.

### Modes (Zellij uses modes instead of prefix keys)

| Mode | Enter | Purpose |
|------|-------|---------|
| **Normal** | `Esc` | Default mode |
| **Pane** | `Ctrl+p` | Pane operations |
| **Tab** | `Ctrl+t` | Tab operations |
| **Resize** | `Ctrl+n` | Resize panes |
| **Scroll** | `Ctrl+s` | Scrollback |
| **Locked** | `Ctrl+g` | Lock session |

### Most Useful for pi

```
Alt + n          New pane (side-by-side)
Alt + -          New pane horizontal split
Alt + %          New pane vertical split
Alt + ←/→/↑/↓    Move focus between panes
Alt + w          Session selector (visual)
Alt + f          Toggle floating panes
Ctrl + p, then h/j/k/l  Move focus (vim-style)
Ctrl + s, then e        Edit scrollback in $EDITOR
Ctrl + ?         Show all keybindings
```

---

## pi Compatibility

### ✅ Works Out-of-the-Box

Zellij forwards extended key sequences by default, so pi's keybindings work without configuration:

- `Shift+Enter` (multi-line input)
- `Ctrl+Enter` (alternate newline)
- `Ctrl+L` (model selector)
- `Ctrl+P` (cycle models)
- All pi keybindings

### ⚠️ Potential Conflict: `Ctrl+P`

Zellij uses `Ctrl+p` to enter **Pane mode**, but pi uses `Ctrl+p` to cycle models.

**Solutions:**

1. **Use pi's alternative**: `Shift+Ctrl+P` cycles models backward
2. **Rebind Zellij's pane mode** (see configuration below)
3. **Use Zellij's mouse/Alt bindings** for pane operations instead

---

## Configuration (Optional)

Config location: `~/.config/zellij/config.kdl`

### Generate Default Config

```bash
zellij setup --dump-config > ~/.config/zellij/config.kdl
```

### Recommended pi-Friendly Config

```kdl
// ~/.config/zellij/config.kdl

// Simplified theme
theme "dracula"  // or "default", "light", etc.

// Simplified keybindings - move pane mode to avoid Ctrl+p conflict
keybinds {
    normal {
        bind "Ctrl p" { SwitchToMode "pane"; }  // Change to something else if needed
        bind "Alt n" { NewPane; }
        bind "Alt -" { NewPane "down"; }
        bind "Alt %" { NewPane "right"; }
        bind "Alt w" { ToggleFloatingPanes; }
        bind "Ctrl ?" { ToggleHelp; }
    }
    
    pane {
        bind "h" "Left" { MoveFocus "Left"; }
        bind "j" "Down" { MoveFocus "Down"; }
        bind "k" "Up" { MoveFocus "Up"; }
        bind "l" "Right" { MoveFocus "Right"; }
        bind "n" { NewPane; }
        bind "d" { MoveFocusOrTab "Down"; }
        bind "x" { CloseFocus; }
        bind "f" { ToggleFloatingPanes; }
    }
}

// Enable mouse (default: true)
mouse_mode true

// Copy command (for pi's Ctrl+V paste)
copy_command "pbcopy"  // macOS
// copy_command "xclip -selection clipboard"  // Linux
```

---

## Workflows for pi

### 1. Multiple pi Sessions (Parallel Agents)

```bash
# Start zellij
zellij

# Create pi session in pane 1
pi "Work on feature A"

# Alt+n to create new pane
pi "Work on feature B"

# Alt+←/→ to switch between them
```

### 2. pi + Monitoring

```bash
# Pane 1: pi working
pi "Refactor the authentication module"

# Pane 2: Monitor logs
tail -f logs/app.log

# Pane 3: Run tests
npm test -- --watch
```

### 3. Session Persistence

```bash
# Detach (session keeps running)
Ctrl+o, then select "Detach"

# Reattach later
zellij attach

# Or with visual selector
zellij -l welcome
```

### 4. Layouts for pi Workflows

Create `~/.config/zellij/layouts/pi-dev.kdl`:

```kdl
layout {
    tab name="pi-workspace" {
        pane {
            plugin location="zellij:tab-bar"
        }
        pane {
            run "pi"
            name "pi-agent"
        }
        pane {
            run "bash"
            name "terminal"
        }
        pane {
            run "bash"
            name "logs"
        }
    }
}
```

Start with: `zellij -l pi-dev`

---

## Advanced Features

### Floating Panes (`Alt+f`)

Perfect for temporary monitoring:

```
# Toggle floating pane
Alt + f

# Run a quick command
watch -n 5 'git status'

# Hide it (keeps running)
Alt + f

# Show again
Alt + f
```

### Edit Scrollback in Editor (`Ctrl+s`, then `e`)

```
# In any pane with output
Ctrl + s  # Enter scroll mode
e         # Open in $EDITOR

# Save output to file, search, copy, etc.
```

### Click-to-Open Files

Click any file path in terminal output → opens in your `$EDITOR` in a floating pane.

### Session Sharing

```bash
# Start with web server
zellij --server

# Share URL with teammate
# They can view or interact based on permissions
```

---

## Migration from tmux

| tmux Command | Zellij Equivalent |
|--------------|-------------------|
| `Ctrl+b c` (new window) | `Alt+n` (new pane) or `Ctrl+t, n` (new tab) |
| `Ctrl+b %` (vertical split) | `Alt+%` |
| `Ctrl+b "` (horizontal split) | `Alt+-` |
| `Ctrl+b o` (cycle panes) | `Alt+←/→/↑/↓` or `Ctrl+p, h/j/k/l` |
| `Ctrl+b d` (detach) | `Ctrl+o`, then "Detach" |
| `tmux attach` | `zellij attach` |
| `tmux ls` | `zellij list-sessions` or `Ctrl+o, w` |
| `Ctrl+b ?` (help) | `Ctrl+?` (always shows current mode's bindings) |

---

## Comparison: Zellij vs Chloe

**Chloe** is another alternative designed specifically for AI coding agents:

| Feature | Zellij | Chloe |
|---------|--------|-------|
| **Purpose** | General terminal multiplexer | AI agent workflow manager |
| **Language** | Rust | Rust |
| **Memory** | ~80MB | ~5MB |
| **Key feature** | Floating panes, layouts | Kanban board, task management |
| **AI integration** | Run any terminal AI agent | Built-in multi-agent orchestration |
| **Maturity** | Stable (1.0+) | Early (beta) |
| **pi compatibility** | ✅ Tested | ⚠️ Unknown |

**Recommendation:** Use **Zellij** for general pi workflows. Consider **Chloe** if you need built-in Kanban task management for AI agents (but test pi compatibility first).

---

## Resources

- **Official Site:** https://zellij.dev
- **Documentation:** https://zellij.dev/documentation
- **GitHub:** https://github.com/zellij-org/zellij
- **Keybindings Reference:** https://zellij.dev/documentation/keybindings
- **Configuration Guide:** https://zellij.dev/documentation/configuration

---

## Navigation

- **[← Back to Tools](README.md)**
- **[← Back to Technical Infrastructure Wiki](../README.md)**
- **[pi tmux docs](https://github.com/badlogic/pi-mono/blob/main/docs/tmux.md)** — Official pi tmux configuration
