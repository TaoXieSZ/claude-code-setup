# Agent Transfer Instructions

This file contains instructions for AI agents to read and transfer this Claude Code setup to another machine or context.

## Files to Read

1. **`settings.json`** - Global permissions and settings
2. **`settings.local.json`** - Local overrides including hooks configuration
3. **`hooks/scripts/hooks.py`** - Main hook handler script
4. **`hooks/config/hooks-config.json`** - Hook enable/disable configuration
5. **`skills/skills-list.txt`** - List of all skills with their source paths

## Setup Steps

### Step 1: Create Directory Structure
```bash
mkdir -p ~/.claude/{skills,hooks/{scripts,config,sounds},plugins,memory}
mkdir -p ~/.agents/skills
```

### Step 2: Copy Settings
```bash
cp settings.json ~/.claude/settings.json
cp settings.local.json ~/.claude/settings.local.json
```

### Step 3: Copy Hooks
```bash
cp hooks/scripts/hooks.py ~/.claude/hooks/scripts/hooks.py
cp hooks/config/hooks-config.json ~/.claude/hooks/config/hooks-config.json
```

### Step 4: Clone GStack
```bash
git clone https://github.com/gdbc/gstack.git ~/.claude/skills/gstack
```

### Step 5: Create Skill Symlinks
Read `skills/skills-list.txt` and create symlinks for each skill:

For gstack skills:
```bash
ln -sf gstack/autoplan ~/.claude/skills/autoplan
ln -sf gstack/browse ~/.claude/skills/browse
# ... etc
```

For custom skills in .agents:
```bash
ln -sf ../../.agents/skills/xiaohongshu ~/.claude/skills/xiaohongshu
# ... etc
```

### Step 6: Install claude-hud Plugin
Run in Claude Code:
```
/claude-hud:setup
```

## Key Settings

### Model
- Default: `opus[1m]` (Claude Opus 4.6 with 1M context)

### Permissions
Pre-approved commands include:
- `WebSearch`
- `Bash(python*)`, `Bash(python3*)`
- `Bash(pip*)`
- `Bash(curl*)`
- `Bash(ls*)`
- `Bash(git*)`
- etc.

### Hooks
- All 23 hooks are configured
- Hooks play sounds on events
- Logging is disabled by default

## Skills Categories

### Development Workflow (GStack)
- `browse` - Headless browser QA
- `review` - PR code review
- `ship` - Create PR workflow
- `qa` - Test and fix bugs
- `investigate` - Debug issues

### Content Creation (XHS/小红书)
- `xiaohongshu` - XHS content tools
- `xhs-note-creator` - Create XHS notes
- `xiaohongshu-images` - Generate images
- `write-xiaohongshu` - Write XHS content

### Development Tools
- `golang-pro` - Go patterns
- `k8s-manifest-generator` - Kubernetes manifests
- `terraform-style-guide` - Terraform best practices
- `monitoring-observability` - Setup monitoring

### Resume/Career
- `resume-generator` - Generate resumes
- `resume-writer` - Write resumes
- `job-application-optimizer` - Optimize job applications

## Notes

1. Sound files are not included in this repo due to size. The hooks will silently skip if sounds are missing.

2. Custom skills in `~/.agents/skills/` need to be sourced separately or copied manually.

3. The `settings.local.json` uses `${CLAUDE_PROJECT_DIR}` for hooks, which requires project-level `.claude/hooks/` directory.

4. For global hooks (no project), modify the hook paths to use absolute paths like:
   ```json
   "command": "python3 /Users/USERNAME/.claude/hooks/scripts/hooks.py"
   ```
