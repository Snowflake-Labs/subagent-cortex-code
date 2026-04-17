#!/bin/bash
set -e

TARGET=~/.cursor/skills/cortex-code
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Installing Cursor skill to $TARGET"

# Create directories
mkdir -p "$TARGET/scripts" "$TARGET/security/policies"

# Copy shared components
echo "Copying shared scripts..."
cp -r "$REPO_ROOT/shared/scripts/"* "$TARGET/scripts/"
echo "Copying shared security modules..."
cp -r "$REPO_ROOT/shared/security/"* "$TARGET/security/"

# Parameterize for Cursor (replace __CODING_AGENT__ with cursor)
echo "Parameterizing for Cursor..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS (BSD sed)
    find "$TARGET" -name "*.py" -exec sed -i '' 's/__CODING_AGENT__/cursor/g' {} \;
else
    # Linux (GNU sed)
    find "$TARGET" -name "*.py" -exec sed -i 's/__CODING_AGENT__/cursor/g' {} \;
fi

# Copy Cursor specific files
echo "Copying Cursor specific files..."
cp "$REPO_ROOT/integrations/cursor/SKILL.md" "$TARGET/"

# Make scripts executable
chmod +x "$TARGET/scripts/"*.py

echo ""
echo "✓ Cursor skill installed successfully"
echo "  Location: $TARGET"
echo "  Audit log: ~/.cursor/skills/cortex-code/audit.log"
echo ""
echo "(Optional) Copy .cursorrules.template to your project root for automatic routing:"
echo "  cp $REPO_ROOT/integrations/cursor/.cursorrules.template /path/to/your/project/.cursorrules"
echo ""
echo "Test with: /cortex-code How many databases do I have?"
