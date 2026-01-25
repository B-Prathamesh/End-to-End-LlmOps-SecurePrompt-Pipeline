#!/bin/bash
set -e

echo "🔍 Running Promptfoo LLM security scan..."

unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy

npx promptfoo eval \
  -c ./promptfooconfig.yaml \
  --no-cache

./scanner/export_promptfoo.sh
python3 ./scanner/security_gate.py

echo "✅ Security scan complete"

