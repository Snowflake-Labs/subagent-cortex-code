#!/bin/bash
set -e

TARGET=~/.codex/skills/cortex-code
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Installing Codex skill to $TARGET"

# Create directories
mkdir -p "$TARGET/scripts" "$TARGET/security/policies"

# Copy shared components
echo "Copying shared scripts..."
cp -r "$REPO_ROOT/shared/scripts/"* "$TARGET/scripts/"
echo "Copying shared security modules..."
cp -r "$REPO_ROOT/shared/security/"* "$TARGET/security/"

# Parameterize for Codex (replace __CODING_AGENT__ with codex)
echo "Parameterizing for Codex..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    find "$TARGET" -name "*.py" -exec sed -i '' 's/__CODING_AGENT__/codex/g' {} \;
else
    # Linux (GNU sed)
    find "$TARGET" -name "*.py" -exec sed -i 's/__CODING_AGENT__/codex/g' {} \;
fi

# Copy Codex specific files
echo "Copying Codex specific files..."
cp "$REPO_ROOT/integrations/codex/SKILL.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/config.yaml.example" "$TARGET/"

# Copy config if not exists
if [ ! -f "$TARGET/config.yaml" ]; then
    echo "Creating default config.yaml..."
    cp "$TARGET/config.yaml.example" "$TARGET/config.yaml"
fi

# Make scripts executable
chmod +x "$TARGET/scripts/"*.py

echo ""
echo "✓ Codex skill installed successfully"
echo "  Location: $TARGET"
echo "  Config: $TARGET/config.yaml"
echo "  Audit log: ~/.codex/skills/cortex-code/audit.log"
echo ""
echo "See setup_guidance.md for usage instructions"
