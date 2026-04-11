#!/bin/bash
set -e

TARGET=~/.claude/skills/cortex-code
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Installing Claude Code skill to $TARGET"

# Create directories
mkdir -p "$TARGET/scripts" "$TARGET/security/policies"

# Copy shared components
echo "Copying shared scripts..."
cp -r "$REPO_ROOT/shared/scripts/"* "$TARGET/scripts/"
echo "Copying shared security modules..."
cp -r "$REPO_ROOT/shared/security/"* "$TARGET/security/"

# Parameterize for Claude Code (replace __CODING_AGENT__ with claude)
echo "Parameterizing for Claude Code..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    find "$TARGET" -name "*.py" -exec sed -i '' 's/__CODING_AGENT__/claude/g' {} \;
else
    # Linux (GNU sed)
    find "$TARGET" -name "*.py" -exec sed -i 's/__CODING_AGENT__/claude/g' {} \;
fi

# Copy Claude Code specific files
echo "Copying Claude Code specific files..."
cp "$REPO_ROOT/integrations/claude-code/skill.md" "$TARGET/"
cp "$REPO_ROOT/integrations/claude-code/config.yaml.example" "$TARGET/"

# Copy config if not exists
if [ ! -f "$TARGET/config.yaml" ]; then
    echo "Creating default config.yaml..."
    cp "$TARGET/config.yaml.example" "$TARGET/config.yaml"
fi

# Make scripts executable
chmod +x "$TARGET/scripts/"*.py

echo ""
echo "✓ Claude Code skill installed successfully"
echo "  Location: $TARGET"
echo "  Config: $TARGET/config.yaml"
echo "  Audit log: ~/.claude/skills/cortex-code/audit.log"
echo ""
echo "Test with: /cortex-code How many databases do I have?"
