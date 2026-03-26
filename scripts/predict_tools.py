#!/usr/bin/env python3
"""
Predicts which Cortex tools will be needed based on the user prompt and capabilities.
"""

import json
import sys
import argparse
from pathlib import Path


# Tool prediction mappings
TOOL_PATTERNS = {
    "snowflake_sql_execute": [
        "select", "insert", "update", "delete", "query", "sql",
        "table", "database", "data"
    ],
    "bash": [
        "run", "execute", "command", "script", "install"
    ],
    "read": [
        "read", "show", "display", "view", "check", "inspect"
    ],
    "write": [
        "create", "write", "generate", "save"
    ],
    "glob": [
        "find", "search", "list", "files", "directory"
    ],
    "grep": [
        "search", "find", "pattern", "match"
    ]
}


# Always include these base tools for Snowflake operations
BASE_SNOWFLAKE_TOOLS = ["snowflake_sql_execute", "bash", "read"]


def load_capabilities():
    """Load cached Cortex capabilities."""
    cache_path = Path("/tmp/cortex-capabilities.json")

    if not cache_path.exists():
        return {}

    with open(cache_path, 'r') as f:
        return json.load(f)


def predict_tools(prompt, capabilities):
    """Predict required tools based on prompt analysis."""
    prompt_lower = prompt.lower()
    predicted = set(BASE_SNOWFLAKE_TOOLS)

    # Check each tool pattern
    for tool, patterns in TOOL_PATTERNS.items():
        for pattern in patterns:
            if pattern in prompt_lower:
                predicted.add(tool)
                break

    # Check if specific skills might need additional tools
    for skill_name, skill_info in capabilities.items():
        description = skill_info.get("description", "").lower()

        # If skill description matches prompt, assume it needs its common tools
        if any(word in description for word in prompt_lower.split()):
            # Data quality skills typically need more tools
            if "quality" in skill_name or "governance" in skill_name:
                predicted.update(["glob", "grep", "write"])

            # ML skills need bash for model operations
            if "ml" in skill_name or "machine" in skill_name or "forecast" in skill_name:
                predicted.add("bash")

    return list(predicted)


def main():
    """Main tool prediction function."""
    parser = argparse.ArgumentParser(description="Predict required Cortex tools")
    parser.add_argument("--prompt", required=True, help="User prompt to analyze")
    parser.add_argument("--capabilities", help="Path to capabilities JSON", default="/tmp/cortex-capabilities.json")
    args = parser.parse_args()

    # Load capabilities
    capabilities = load_capabilities()

    # Predict tools
    tools = predict_tools(args.prompt, capabilities)

    # Output as JSON
    result = {
        "predicted_tools": tools,
        "count": len(tools)
    }

    print(json.dumps(result, indent=2))

    print(f"\nPredicted {len(tools)} tools: {', '.join(tools)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
