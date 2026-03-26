#!/usr/bin/env python3
"""
Reads recent Cortex Code session files for context enrichment.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime


def find_recent_sessions(limit=3):
    """Find the most recent Cortex session files."""
    sessions_dir = Path.home() / ".local/share/cortex/sessions"

    if not sessions_dir.exists():
        print(f"Sessions directory not found: {sessions_dir}", file=sys.stderr)
        return []

    # Find all .jsonl session files
    session_files = sorted(
        [f for f in sessions_dir.glob("**/*.jsonl")],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    return session_files[:limit]


def parse_session_file(session_path):
    """Parse a session JSONL file and extract key information."""
    try:
        with open(session_path, 'r') as f:
            lines = f.readlines()

        session_data = {
            "session_id": None,
            "timestamp": session_path.stat().st_mtime,
            "user_prompts": [],
            "assistant_responses": [],
            "tools_used": [],
            "result": None
        }

        for line in lines:
            if not line.strip():
                continue

            try:
                event = json.loads(line)
                event_type = event.get("type")

                if event_type == "system" and event.get("subtype") == "init":
                    session_data["session_id"] = event.get("session_id")

                elif event_type == "user":
                    # Check if this is a tool result or user message
                    message = event.get("message", {})
                    content = message.get("content", [])

                    # Extract user text if present
                    for item in content:
                        if item.get("type") == "text":
                            session_data["user_prompts"].append(item.get("text", ""))

                elif event_type == "assistant":
                    message = event.get("message", {})
                    content = message.get("content", [])

                    for item in content:
                        if item.get("type") == "text":
                            session_data["assistant_responses"].append(item.get("text", ""))
                        elif item.get("type") == "tool_use":
                            tool_name = item.get("name")
                            if tool_name:
                                session_data["tools_used"].append(tool_name)

                elif event_type == "result":
                    session_data["result"] = event.get("result")

            except json.JSONDecodeError:
                continue

        return session_data

    except Exception as e:
        print(f"Error parsing session {session_path}: {e}", file=sys.stderr)
        return None


def summarize_sessions(session_files):
    """Summarize recent Cortex sessions."""
    summaries = []

    for session_path in session_files:
        session_data = parse_session_file(session_path)

        if not session_data:
            continue

        # Create a concise summary
        summary = {
            "file": session_path.name,
            "session_id": session_data["session_id"],
            "time": datetime.fromtimestamp(session_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
            "prompts_count": len(session_data["user_prompts"]),
            "tools_used": list(set(session_data["tools_used"])),
            "last_prompt": session_data["user_prompts"][-1] if session_data["user_prompts"] else None,
            "result_type": type(session_data["result"]).__name__ if session_data["result"] else None
        }

        summaries.append(summary)

    return summaries


def main():
    """Main function to read and summarize recent Cortex sessions."""
    parser = argparse.ArgumentParser(description="Read recent Cortex sessions")
    parser.add_argument("--limit", type=int, default=3, help="Number of recent sessions to read")
    parser.add_argument("--verbose", action="store_true", help="Include full session details")
    args = parser.parse_args()

    # Find recent sessions
    session_files = find_recent_sessions(args.limit)

    if not session_files:
        print("No recent Cortex sessions found", file=sys.stderr)
        return 0

    print(f"Found {len(session_files)} recent sessions", file=sys.stderr)

    # Summarize sessions
    summaries = summarize_sessions(session_files)

    # Output JSON
    print(json.dumps(summaries, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
