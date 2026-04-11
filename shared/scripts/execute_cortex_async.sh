#!/bin/bash
# Async wrapper for Codex CLI - starts job and returns immediately
# User can check results later with read_cortex_result.sh

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

# Write timestamp to output file to show we started
echo '{"status":"running","started":"'$(date +%s)'"}' > "$OUTPUT_FILE"

# Start job in background and detach completely
nohup "${CMD[@]}" </dev/null >/dev/null 2>&1 &
JOB_PID=$!
disown

# Return immediately with status
echo "⏳ Cortex query started (PID: $JOB_PID)"
echo "📁 Results will be written to: $OUTPUT_FILE"
echo "⏱️  Expected completion: 15-20 seconds"
echo ""
echo "To check results, run:"
echo "  cat $OUTPUT_FILE | python3 -c \"import sys, json; r=json.load(sys.stdin); print(r.get('final_result', 'Still running...'))\""
