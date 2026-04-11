#!/bin/bash
set -e

TARGET=~/.codex/skills/cortex-code
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Installing Codex skill to $TARGET"

# Create minimal directory structure (no scripts needed - using cortexcode-tool CLI)
mkdir -p "$TARGET"

# Copy Codex specific files
echo "Copying Codex specific files..."
cp "$REPO_ROOT/integrations/codex/SKILL.md" "$TARGET/"
cp "$REPO_ROOT/integrations/codex/README.md" "$TARGET/" 2>/dev/null || true
cp "$REPO_ROOT/integrations/codex/SECURITY.md" "$TARGET/" 2>/dev/null || true
cp "$REPO_ROOT/integrations/codex/SECURITY_GUIDE.md" "$TARGET/" 2>/dev/null || true
cp "$REPO_ROOT/integrations/codex/config.yaml.example" "$TARGET/" 2>/dev/null || true
cp "$REPO_ROOT/integrations/codex/config.yaml" "$TARGET/" 2>/dev/null || true
cp "$REPO_ROOT/integrations/codex/setup_guidance.md" "$TARGET/" 2>/dev/null || true

# Copy cortexcode-tool config to /tmp for sandbox compatibility
echo "Setting up cortexcode-tool config for Codex sandbox..."
cp "$REPO_ROOT/integrations/codex/cortexcode-tool-codex.yaml" "/tmp/cortexcode-tool-codex.yaml"
chmod 644 "/tmp/cortexcode-tool-codex.yaml"

echo ""
echo "✓ Codex skill installed successfully"
echo "  Location: $TARGET"
echo "  Uses: cortexcode-tool CLI (no Python scripts needed)"
echo "  Config: /tmp/cortexcode-tool-codex.yaml"
echo ""
echo "Requirements:"
echo "  - cortexcode-tool CLI must be installed"
echo "  - Run: which cortexcode-tool (to verify)"
echo ""
echo "See SKILL.md for usage instructions"
