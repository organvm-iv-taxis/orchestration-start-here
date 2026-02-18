#!/usr/bin/env bash
set -euo pipefail

# Fetch registry-v2.json from the canonical source (organvm-corpvs-testamentvm).
# Falls back to local copy if fetch fails after retries.
# Usage: ./scripts/fetch-registry.sh [output-path]

REGISTRY_URL="https://raw.githubusercontent.com/meta-organvm/organvm-corpvs-testamentvm/main/registry-v2.json"
OUTPUT="${1:-registry-v2.json}"
MAX_RETRIES=3
RETRY_DELAY=5

fetch_with_retry() {
    local attempt=1
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "Fetching registry-v2.json (attempt $attempt/$MAX_RETRIES)..."
        if curl -sSfL "$REGISTRY_URL" -o "$OUTPUT.tmp"; then
            # Validate: must be valid JSON and not a redirect stub
            if python3 -c "
import json, sys
with open('$OUTPUT.tmp') as f:
    data = json.load(f)
if '_redirect' in data:
    print('ERROR: Fetched file is a redirect stub, not the real registry', file=sys.stderr)
    sys.exit(1)
if 'organs' not in data:
    print('ERROR: Fetched file missing organs key — not a valid registry', file=sys.stderr)
    sys.exit(1)
print(f'Validated: {data.get(\"summary\", {}).get(\"total_repos\", \"?\")} repos')
"; then
                mv "$OUTPUT.tmp" "$OUTPUT"
                echo "Registry written to $OUTPUT"
                return 0
            fi
        fi
        echo "Fetch failed. Retrying in ${RETRY_DELAY}s..."
        rm -f "$OUTPUT.tmp"
        sleep "$RETRY_DELAY"
        attempt=$((attempt + 1))
    done

    echo "::error::Failed to fetch registry after $MAX_RETRIES attempts"
    return 1
}

fetch_with_retry
