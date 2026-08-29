#!/usr/bin/env bash
set -euo pipefail

# Fetch repo-registry.json from the canonical source.
#
# The canonical repository is private, so callers should pass a token with
# read access via GH_TOKEN.  The script deliberately fails closed: it never
# substitutes registry.json or another local compatibility file.
# Usage: ./scripts/fetch-registry.sh [output-path]

REGISTRY_URL="${REGISTRY_URL:-https://api.github.com/repos/organvm/organvm-corpvs-testamentvm/contents/repo-registry.json?ref=main}"
OUTPUT="${1:-repo-registry.json}"
MAX_RETRIES="${REGISTRY_FETCH_MAX_RETRIES:-3}"
RETRY_DELAY="${REGISTRY_FETCH_RETRY_DELAY:-5}"
MIN_REPO_COUNT="${REGISTRY_MIN_REPOS:-100}"

curl_args=(
    --silent
    --show-error
    --fail
    --location
    --header "Accept: application/vnd.github.raw+json"
    --header "X-GitHub-Api-Version: 2022-11-28"
)
if [[ -n "${GH_TOKEN:-}" ]]; then
    curl_args+=(--header "Authorization: Bearer ${GH_TOKEN}")
fi

fetch_with_retry() {
    local attempt=1
    while [ "$attempt" -le "$MAX_RETRIES" ]; do
        echo "Fetching repo-registry.json (attempt $attempt/$MAX_RETRIES)..."
        if curl "${curl_args[@]}" "$REGISTRY_URL" -o "$OUTPUT.tmp"; then
            if REGISTRY_PATH="$OUTPUT.tmp" REGISTRY_MIN_REPOS="$MIN_REPO_COUNT" python3 - <<'PYEOF'
import json
import os
import sys
from pathlib import Path

path = Path(os.environ["REGISTRY_PATH"])
minimum = int(os.environ["REGISTRY_MIN_REPOS"])

try:
    data = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(f"ERROR: canonical registry is not valid JSON: {exc}") from exc

if not isinstance(data, dict):
    raise SystemExit("ERROR: canonical registry root must be a JSON object")
if "_redirect" in data:
    raise SystemExit("ERROR: fetched a redirect stub instead of repo-registry.json")

organs = data.get("organs")
if not isinstance(organs, dict) or not organs:
    raise SystemExit("ERROR: canonical registry has no non-empty organs object")

actual = sum(
    len(organ.get("repositories", []))
    for organ in organs.values()
    if isinstance(organ, dict)
)
if actual < minimum:
    raise SystemExit(
        f"ERROR: canonical registry contains only {actual} repos; minimum is {minimum}"
    )

declared = data.get("summary", {}).get("total_repos")
if not isinstance(declared, int):
    raise SystemExit("ERROR: summary.total_repos must be an integer")
if declared != actual:
    raise SystemExit(
        f"ERROR: summary.total_repos={declared}, but organ arrays contain {actual} repos"
    )

print(f"Validated canonical registry: {actual} repos across {len(organs)} organs")
PYEOF
            then
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
