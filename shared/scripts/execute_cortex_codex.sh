#!/bin/bash
# Wrapper for Codex CLI that handles backgrounding
# Waits for completion and outputs results in one go

set -e

# Parse arguments
PROMPT=""
ENVELOPE="RO"
CONNECTION=""
OUTPUT_FILE="/tmp/codex-cortex-latest.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --prompt)
            PROMPT="$2"
            shift 2
            ;;
        --envelope)
            ENVELOPE="$2"
            shift 2
            ;;
        --connection|-c)
            CONNECTION="$2"
            shift 2
            ;;
        --output-file)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Build command
CMD=("python3" "$SCRIPT_DIR/execute_cortex.py" "--prompt" "$PROMPT" "--envelope" "$ENVELOPE" "--output-file" "$OUTPUT_FILE")

if [[ -n "$CONNECTION" ]]; then
    CMD+=("--connection" "$CONNECTION")
fi

# Execute and wait for completion
"${CMD[@]}" > /dev/null 2>&1

# Wait a moment for file write to complete
sleep 1

# Read and output result
if [[ -f "$OUTPUT_FILE" ]]; then
    python3 -c "import sys, json; r=json.load(open('$OUTPUT_FILE')); print(r.get('final_result', 'No result'))"
else
    echo "Error: Output file not created"
    exit 1
fi
