#!/bin/bash
# Claude Code Setup Script
# Run this to set up your Claude Code configuration

set -e

CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$HOME/.agents"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔧 Claude Code Setup"
echo "===================="

# Create directories
echo "📁 Creating directories..."
mkdir -p "$CLAUDE_DIR"/{skills,hooks/{scripts,config,sounds},plugins,memory}
mkdir -p "$AGENTS_DIR/skills"

# Backup existing settings
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    echo "💾 Backing up existing settings.json..."
    cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.bak"
fi

if [ -f "$CLAUDE_DIR/settings.local.json" ]; then
    echo "💾 Backing up existing settings.local.json..."
    cp "$CLAUDE_DIR/settings.local.json" "$CLAUDE_DIR/settings.local.json.bak"
fi

# Copy settings files
echo "📋 Copying settings..."
cp "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"
cp "$SCRIPT_DIR/settings.local.json" "$CLAUDE_DIR/settings.local.json"

# Copy hooks
echo "🪝 Setting up hooks..."
cp "$SCRIPT_DIR/hooks/scripts/hooks.py" "$CLAUDE_DIR/hooks/scripts/hooks.py"
cp "$SCRIPT_DIR/hooks/config/hooks-config.json" "$CLAUDE_DIR/hooks/config/hooks-config.json"
cp "$SCRIPT_DIR/hooks/HOOKS-README.md" "$CLAUDE_DIR/hooks/HOOKS-README.md"

# Copy sounds (if they exist in the repo)
if [ -d "$SCRIPT_DIR/hooks/sounds" ] && [ "$(ls -A $SCRIPT_DIR/hooks/sounds 2>/dev/null)" ]; then
    echo "🔊 Copying sound files..."
    cp -r "$SCRIPT_DIR/hooks/sounds/"* "$CLAUDE_DIR/hooks/sounds/" 2>/dev/null || true
fi

# Clone or update gstack
echo "📦 Setting up gstack skills..."
if [ -d "$CLAUDE_DIR/skills/gstack/.git" ]; then
    echo "   Updating existing gstack..."
    cd "$CLAUDE_DIR/skills/gstack" && git pull
else
    echo "   Cloning gstack..."
    rm -rf "$CLAUDE_DIR/skills/gstack"
    git clone https://github.com/gdbc/gstack.git "$CLAUDE_DIR/skills/gstack"
fi

# Create skill symlinks
echo "🔗 Creating skill symlinks..."
while IFS= read -r line; do
    if [ -n "$line" ] && [[ ! "$line" =~ ^# ]]; then
        skill_name=$(echo "$line" | cut -d':' -f1)
        skill_source=$(echo "$line" | cut -d':' -f2)

        # Create source directory if it's a custom skill
        if [[ "$skill_source" == ".agents/skills/"* ]]; then
            mkdir -p "$AGENTS_DIR/skills/$skill_name"
        fi

        # Create symlink
        ln -sf "$HOME/$skill_source" "$CLAUDE_DIR/skills/$skill_name" 2>/dev/null || true
    fi
done < "$SCRIPT_DIR/skills/skills-list.txt"

# Install claude-hud plugin
echo "🔌 Installing claude-hud plugin..."
claude /claude-hud:setup 2>/dev/null || echo "   (Install manually with: /claude-hud:setup)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Restart Claude Code"
echo "2. Verify hooks work: You should hear sounds on events"
echo "3. Check skills: ls ~/.claude/skills/"
echo ""
echo "To customize hooks, edit: ~/.claude/hooks/config/hooks-config.local.json"
