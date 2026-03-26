#!/usr/bin/env python3
"""
LLM-based routing logic to determine if request should go to Cortex Code or Claude Code.
Uses semantic understanding rather than simple keyword matching.
"""

import json
import sys
import argparse
from pathlib import Path


# Snowflake/Cortex indicators
SNOWFLAKE_INDICATORS = [
    "snowflake", "cortex", "warehouse", "snowpark", "data warehouse",
    "cortex ai", "cortex search", "cortex analyst", "dynamic table",
    "snowflake database", "snowflake schema", "snowflake table",
    "data governance", "data quality", "trust my data",
    "ml function", "classification", "forecasting",
    "stream", "task", "stage", "pipe"
]

# Non-Snowflake indicators (route to Claude Code)
CLAUDE_CODE_INDICATORS = [
    "local file", "git", "github", "commit", "push", "pull request",
    "python script", "javascript", "react", "frontend", "backend",
    "postgres", "mysql", "mongodb", "redis",
    "docker", "kubernetes", "infrastructure",
    "read file", "write file", "edit file", "create file"
]


def load_cortex_capabilities():
    """Load cached Cortex capabilities."""
    cache_path = Path("/tmp/cortex-capabilities.json")

    if not cache_path.exists():
        print("Warning: Cortex capabilities not cached. Run discover_cortex.py first.", file=sys.stderr)
        return {}

    with open(cache_path, 'r') as f:
        return json.load(f)


def analyze_with_llm_logic(prompt, capabilities):
    """
    Analyze prompt using LLM-inspired logic.
    This is a deterministic approximation of what an LLM would consider.
    """
    prompt_lower = prompt.lower()

    # Score based on indicators
    snowflake_score = 0
    claude_score = 0

    # Check for explicit Snowflake/Cortex mentions
    for indicator in SNOWFLAKE_INDICATORS:
        if indicator in prompt_lower:
            snowflake_score += 3 if indicator in ["snowflake", "cortex"] else 1

    # Check for non-Snowflake indicators
    for indicator in CLAUDE_CODE_INDICATORS:
        if indicator in prompt_lower:
            claude_score += 2

    # Check against Cortex skill triggers
    for skill_name, skill_info in capabilities.items():
        for trigger in skill_info.get("triggers", []):
            trigger_lower = trigger.lower()
            if trigger_lower in prompt_lower or any(word in prompt_lower for word in trigger_lower.split()):
                snowflake_score += 2
                break

    # SQL query detection
    sql_keywords = ["select", "insert", "update", "delete", "create table", "alter", "drop"]
    if any(kw in prompt_lower for kw in sql_keywords):
        # Could be any database, but check for Snowflake context
        if any(ind in prompt_lower for ind in ["snowflake", "warehouse", "cortex"]):
            snowflake_score += 3
        else:
            # Generic SQL, likely not Snowflake
            claude_score += 1

    # Data-related terms (ambiguous, need context)
    data_terms = ["data quality", "schema", "table", "database", "query"]
    data_term_count = sum(1 for term in data_terms if term in prompt_lower)
    if data_term_count >= 2:
        # Multiple data terms suggest database work
        # Check if Snowflake context exists
        if snowflake_score > 0:
            snowflake_score += 2

    # Calculate confidence
    total_score = snowflake_score + claude_score
    if total_score == 0:
        # No strong indicators, default to Claude Code for safety
        return "claude", 0.5

    confidence = max(snowflake_score, claude_score) / total_score

    if snowflake_score > claude_score:
        return "cortex", confidence
    else:
        return "claude", confidence


def main():
    """Main routing function."""
    parser = argparse.ArgumentParser(description="Route request to Cortex or Claude Code")
    parser.add_argument("--prompt", required=True, help="User prompt to analyze")
    args = parser.parse_args()

    # Load Cortex capabilities
    capabilities = load_cortex_capabilities()

    # Analyze prompt
    route, confidence = analyze_with_llm_logic(args.prompt, capabilities)

    # Output decision
    result = {
        "route": route,
        "confidence": confidence,
        "reasoning": f"Routed to {route} with {confidence:.2%} confidence"
    }

    print(json.dumps(result, indent=2))

    print(f"\n→ Route to: {route.upper()}", file=sys.stderr)
    print(f"   Confidence: {confidence:.2%}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
