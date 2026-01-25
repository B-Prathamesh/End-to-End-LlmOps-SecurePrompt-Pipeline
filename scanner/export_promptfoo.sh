#!/bin/bash
set -e

echo "📤 Exporting latest Promptfoo results..."

REPORT_DIR="reports"
mkdir -p "$REPORT_DIR"

STATE_FILE="$HOME/.promptfoo/evalLastWritten"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No eval state file found at $STATE_FILE"
  echo "👉 Run ./scanner/run_promptfoo.sh first"
  exit 1
fi

RAW_EVAL_ID=$(cat "$STATE_FILE" | tr -d '\n')

# FIX: Keep only the first timestamp segment
EVAL_ID=$(echo "$RAW_EVAL_ID" | awk -F':' '{print $1 ":" $2 ":" $3}')

if [ -z "$EVAL_ID" ]; then
  echo "❌ Eval ID is empty"
  exit 1
fi

echo "📌 Raw eval ID: $RAW_EVAL_ID"
echo "✅ Clean eval ID: $EVAL_ID"

npx promptfoo export eval "$EVAL_ID" --output "$REPORT_DIR/promptfoo-results.json"

echo "📦 Exported Promptfoo results to $REPORT_DIR/promptfoo-results.json"

