# Claude Code Setup

Personal Claude Code configuration backup for easy transfer between machines.

## Quick Start

```bash
# Clone this repo
git clone https://github.com/TaoXieSZ/claude-code-setup.git
cd claude-code-setup

# Run the setup script
./setup.sh
```

## What's Included

### Configuration Files
- `settings.json` - Global settings (permissions, model, etc.)
- `settings.local.json` - Local overrides (hooks, plugins, etc.)

### Hooks System
- Audio feedback hooks for all 23 Claude Code events
- Configurable enable/disable per hook
- Cross-platform support (macOS, Linux, Windows)

### Skills
Skills are symlinked from two sources:
1. `.claude/skills/gstack/` - GStack workflow skills
2. `.agents/skills/` - Custom skills collection

### Plugins
- **claude-hud** - Status line HUD display

## Directory Structure

```
~/.claude/
├── settings.json          # Global permissions
├── settings.local.json    # Local settings (hooks, model, plugins)
├── skills/                # Skill symlinks
│   ├── gstack/           # Cloned gstack repo
│   └── *.symlinks        # Custom skill symlinks
├── hooks/
│   ├── scripts/hooks.py  # Main hook handler
│   ├── config/           # Hook configuration
│   └── sounds/           # Audio files
├── plugins/              # Plugin cache
└── memory/               # Project memory files

~/.agents/
└── skills/               # Custom skills source
```

## Transfer Instructions for Agents

To transfer this setup to another machine, read the following files:

1. **Settings**: `settings.json` and `settings.local.json`
2. **Hooks**: Copy `hooks/` directory entirely
3. **Skills**: Check `skills/skills-list.txt` for required skills
4. **GStack**: Clone from https://github.com/gdbc/gstack to `~/.claude/skills/gstack/`

## Custom Skills

Custom skills are stored in `~/.agents/skills/` and symlinked to `~/.claude/skills/`.

See `skills/skills-list.txt` for the complete list of custom skills.

## Hooks Configuration

Hooks can be toggled in `hooks/config/hooks-config.json`:

```json
{
  "disableSessionStartHook": false,
  "disablePostToolUseHook": false,
  ...
}
```

Create `hooks/config/hooks-config.local.json` for personal overrides.

## Plugins

### claude-hud

Status line HUD that shows context in the terminal.

Install: `/claude-hud:setup`

## Version

- Claude Code: v2.1.78+
- Last Updated: 2026-03-24
