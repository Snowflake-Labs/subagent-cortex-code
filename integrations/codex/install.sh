#!/bin/bash
set -e

TARGET=~/.codex/skills/cortex-code
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Installing Codex skill to $TARGET"

# Create directories
mkdir -p "$TARGET/scripts" "$TARGET/security/policies" "$TARGET/references" "$TARGET/tests"

# Copy shared components
echo "Copying shared scripts..."
cp -r "$REPO_ROOT/shared/scripts/"* "$TARGET/scripts/"
echo "Copying shared security modules..."
cp -r "$REPO_ROOT/shared/security/"* "$TARGET/security/"

# Copy references directory
echo "Copying reference documentation..."
cp -r "$REPO_ROOT/references/"* "$TARGET/references/"

# Copy tests directory
echo "Copying test suite..."
cp -r "$REPO_ROOT/tests/"* "$TARGET/tests/"

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
cp "$REPO_ROOT/integrations/codex/README.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/SECURITY.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/SECURITY_GUIDE.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/config.yaml.example" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/config.yaml" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/setup_guidance.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/setup_guidance.md" "$TARGET/setup_guidance_codex_coco_skill.md"

# Copy cortexcode-tool config to /tmp for sandbox compatibility
echo "Setting up cortexcode-tool config for Codex sandbox..."
cp "$REPO_ROOT/integrations/codex/cortexcode-tool-codex.yaml" "/tmp/cortexcode-tool-codex.yaml"
chmod 644 "/tmp/cortexcode-tool-codex.yaml"

# Note: config.yaml with approval_mode: "auto" is created for non-interactive CLI usage
# Uses /tmp/ paths for audit and cache to avoid Codex sandbox restrictions

# Make scripts executable
chmod +x "$TARGET/scripts/"*.py

echo ""
echo "✓ Codex skill installed successfully"
echo "  Location: $TARGET"
echo "  Config: $TARGET/config.yaml (approval_mode: auto)"
echo "  To customize further: edit config.yaml or see config.yaml.example"
echo ""
echo "See setup_guidance.md for usage instructions"
