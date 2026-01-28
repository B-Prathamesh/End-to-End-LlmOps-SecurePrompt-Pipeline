#!/bin/bash
set -e

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

if [ ! -f eval_id.txt ]; then
  echo "❌ eval_id.txt not found"
  exit 1
fi

EVAL_ID=$(cat eval_id.txt)

echo "📤 Exporting Promptfoo results for $EVAL_ID..."

npx promptfoo export eval "$EVAL_ID" \
  --output "$REPORT_DIR/promptfoo-results.json"

echo "📦 Export completed"

