#!/bin/bash
set -e

echo "🚀 Running Promptfoo evaluation..."

EVAL_OUTPUT=$(npx promptfoo eval --no-view)

echo "$EVAL_OUTPUT"

EVAL_ID=$(echo "$EVAL_OUTPUT" | grep -oE 'eval-[a-z0-9\-:T]+' | head -n 1)

if [ -z "$EVAL_ID" ]; then
  echo "❌ Failed to extract Eval ID"
  exit 1
fi

echo "$EVAL_ID" > eval_id.txt
echo "📌 Eval ID saved: $EVAL_ID"
