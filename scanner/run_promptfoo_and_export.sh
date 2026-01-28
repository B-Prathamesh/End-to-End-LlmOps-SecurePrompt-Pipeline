#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[+] Running Promptfoo evaluation..."

# Run Promptfoo eval (do NOT fail pipeline here)
npx promptfoo eval -c "$ROOT_DIR/promptfooconfig.yaml" --no-cache \
  || echo "⚠️ Promptfoo reported failures, continuing..."

echo "[+] Fetching latest Promptfoo eval ID..."

EVAL_ID=$(npx promptfoo eval:list --json | jq -r '.[0].id')

if [ -z "$EVAL_ID" ] || [ "$EVAL_ID" = "null" ]; then
  echo "❌ Could not determine Promptfoo eval ID"
  exit 1
fi

echo "$EVAL_ID" > "$SCRIPT_DIR/eval_id.txt"
echo "✅ eval_id.txt created: $EVAL_ID"

echo "[+] Exporting Promptfoo results..."

npx promptfoo export \
  --eval-id "$EVAL_ID" \
  --format json \
  --output "$SCRIPT_DIR/promptfoo_results.json"

echo "✅ Promptfoo evaluation & export completed"

