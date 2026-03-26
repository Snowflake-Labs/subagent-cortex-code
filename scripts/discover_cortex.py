#!/usr/bin/env python3
"""
Discovers Cortex Code capabilities by listing skills and parsing their metadata.
Caches results for the current Claude Code session.
"""

import json
import subprocess
import sys
from pathlib import Path
import re


def run_command(cmd):
    """Run shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1


def discover_cortex_skills():
    """Discover all available Cortex Code skills."""
    print("Discovering Cortex Code capabilities...", file=sys.stderr)

    # Run cortex skill list
    stdout, stderr, code = run_command("cortex skill list")

    if code != 0:
        print(f"Error running cortex skill list: {stderr}", file=sys.stderr)
        return {}

    # Parse skill list output
    skills = {}

    # Expected format: skill lines with name and path
    for line in stdout.strip().split('\n'):
        if not line.strip():
            continue

        # Try to extract skill name (usually first word or before colon)
        parts = line.split()
        if parts:
            skill_name = parts[0].strip(':').strip()

            # Read the skill's SKILL.md to get description and triggers
            skill_info = read_skill_metadata(skill_name)
            if skill_info:
                skills[skill_name] = skill_info

    return skills


def read_skill_metadata(skill_name):
    """Read SKILL.md frontmatter for a specific skill."""
    # Cortex bundled skills are typically in ~/.local/share/cortex/{version}/bundled_skills/
    cortex_share = Path.home() / ".local/share/cortex"

    # Find the most recent version directory
    if not cortex_share.exists():
        return None

    version_dirs = sorted([d for d in cortex_share.iterdir() if d.is_dir()], reverse=True)

    for version_dir in version_dirs:
        bundled_skills = version_dir / "bundled_skills"
        if not bundled_skills.exists():
            continue

        # Look for skill directory
        skill_path = bundled_skills / skill_name / "SKILL.md"
        if skill_path.exists():
            return parse_skill_md(skill_path)

    return None


def parse_skill_md(skill_path):
    """Parse SKILL.md file and extract frontmatter."""
    try:
        with open(skill_path, 'r') as f:
            content = f.read()

        # Extract YAML frontmatter
        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return None

        frontmatter = frontmatter_match.group(1)

        # Simple YAML parsing for name and description
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        desc_match = re.search(r'description:\s*["\']?(.+?)["\']?$', frontmatter, re.MULTILINE | re.DOTALL)

        if name_match and desc_match:
            name = name_match.group(1).strip().strip('"\'')
            description = desc_match.group(1).strip().strip('"\'')

            # Extract "Use when" trigger patterns from body
            triggers = extract_triggers(content)

            return {
                "name": name,
                "description": description,
                "triggers": triggers
            }
    except Exception as e:
        print(f"Error parsing {skill_path}: {e}", file=sys.stderr)
        return None


def extract_triggers(content):
    """Extract trigger phrases from skill content."""
    triggers = []

    # Look for "Use when", "Trigger", "When to use" sections
    trigger_patterns = [
        r'(?:Use when|When to use|Trigger).*?:\s*(.+?)(?=\n\n|\#\#)',
        r'- Use (?:when|for|if):\s*(.+?)$'
    ]

    for pattern in trigger_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            trigger_text = match.group(1).strip()
            # Clean up and split by common separators
            phrases = re.split(r'[,;]|\n-', trigger_text)
            triggers.extend([p.strip() for p in phrases if p.strip()])

    return triggers[:10]  # Limit to 10 most relevant triggers


def main():
    """Main discovery function."""
    capabilities = discover_cortex_skills()

    # Cache to /tmp for session duration
    cache_path = Path("/tmp/cortex-capabilities.json")

    with open(cache_path, 'w') as f:
        json.dump(capabilities, f, indent=2)

    print(f"Discovered {len(capabilities)} Cortex skills", file=sys.stderr)
    print(f"Cached to: {cache_path}", file=sys.stderr)

    # Output the capabilities
    print(json.dumps(capabilities, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
