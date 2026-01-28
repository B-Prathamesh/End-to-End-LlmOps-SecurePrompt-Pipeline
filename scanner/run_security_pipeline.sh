#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 🔐 Fail fast if secrets are missing (prevents silent CI crash)
: "${APP_API_KEY:?❌ APP_API_KEY is not set}"
: "${JWT_SECRET:?❌ JWT_SECRET is not set}"
: "${HF_TOKEN:?❌ HF_TOKEN is not set}"

echo "🚀 Starting LLM Security Pipeline..."

# 1️⃣ Build image
echo "[1] Building llm-api image..."
docker build -t llm-api -f docker/Dockerfile .

# 2️⃣ Run API container
echo "[2] Starting API container..."
docker rm -f llm-api-container >/dev/null 2>&1 || true

API_PORT=8000

# ✅ Inject GitHub secrets into container (CI-safe)
docker run -d -p $API_PORT:8000 \
  --network llmops-net \
  -e APP_API_KEY="${APP_API_KEY}" \
  -e JWT_SECRET="${JWT_SECRET}" \
  -e HF_TOKEN="${HF_TOKEN}" \
  --name llm-api-container \
  llm-api

echo "⏳ Waiting for API to be ready..."

#for i in {1..20}; do
#  if curl -s http://127.0.0.1:$API_PORT/health >/dev/null; then
#    echo "✅ API is ready"
#    break
#  fi
#  echo "⏳ API not ready yet... ($i)"
#  sleep 2
#done
API_READY=0

for i in {1..20}; do
  if curl -sf http://127.0.0.1:$API_PORT/health >/dev/null; then
    echo "✅ API is ready"
    API_READY=1
    break
  fi
  echo "⏳ API not ready yet... ($i)"
  sleep 2
done

if [ "$API_READY" -ne 1 ]; then
  echo "❌ API never became ready"
  docker logs llm-api-container
  exit 1
fi


# 3️⃣ Run Promptfoo scan
echo "[3] Running Promptfoo LLM scan..."
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy

echo "[+] Fetching runtime JWT token..."
#./scanner/get_jwt_token.sh
"$SCRIPT_DIR/get_jwt_token.sh"

set -a
source /tmp/jwt.env
set +a

echo "DEBUG PIPELINE: RUNTIME_JWT_TOKEN=$RUNTIME_JWT_TOKEN"
echo "DEBUG PIPELINE: APP_API_KEY=$APP_API_KEY"

#npx promptfoo eval -c promptfooconfig.yaml --no-cache || echo "⚠️ Promptfoo reported failures, continuing to export..."
npx promptfoo eval -c "$ROOT_DIR/promptfooconfig.yaml" --no-cache \
  || echo "⚠️ Promptfoo reported failures, continuing to export..."

# 4️⃣ Export results
echo "[4] Exporting results..."
#./scanner/export_promptfoo.sh
"$SCRIPT_DIR/export_promptfoo.sh"

PIPELINE_FAILED=0

echo "[5] Running security gate..."
#if ! python3 scanner/security_gate.py; then
if ! python3 "$SCRIPT_DIR/security_gate.py"; then
  echo "❌ Security gate failed"
  PIPELINE_FAILED=1
fi

echo "[6] Running Trivy container scan..."
#if ! ./scanner/run_trivy_scan.sh; then
if ! "$SCRIPT_DIR/run_trivy_scan.sh"; then
  echo "❌ Trivy scan failed"
  PIPELINE_FAILED=1
fi

#if [ "$PIPELINE_FAILED" -ne 0 ]; then
#  echo "❌ Pipeline failed due to security issues"
#  exit 1
#fi

#echo "✅ Pipeline complete."
if [ "$PIPELINE_FAILED" -ne 0 ]; then
  echo "❌ Pipeline failed due to security issues"
  #./scanner/notify_slack.sh failure "Security gate or Trivy scan failed"
  "$SCRIPT_DIR/notify_slack.sh" failure "Security gate or Trivy scan failed"
  exit 1
fi

#./scanner/notify_slack.sh success "All security checks passed"
"$SCRIPT_DIR/notify_slack.sh" success "All security checks passed"
echo "✅ Pipeline complete."

