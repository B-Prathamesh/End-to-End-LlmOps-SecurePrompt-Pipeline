from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_api_key, verify_jwt, create_jwt
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import json
from pathlib import Path
import os
from dotenv import load_dotenv
import sys
sys.path.append("/app/scanner")  # ✅ FIX: correct path inside Docker

from scanner.scanner_runner import run_security_scan

load_dotenv()  # allow env vars from Docker / GitHub Actions

_metrics_loaded = False
PROMPTFOO_REPORT = Path("reports/promptfoo-results.json")
GATE_STATUS_FILE = Path("reports/gate-status.json")

APP_API_KEY = os.getenv("APP_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET")

if not APP_API_KEY:
    raise RuntimeError("APP_API_KEY is missing")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing")

app = FastAPI()

# =========================
# Prometheus Metrics
# =========================

promptfoo_total_tests = Counter(
    "promptfoo_tests_total",
    "Total Promptfoo tests executed"
)

promptfoo_failed_tests = Counter(
    "promptfoo_tests_failed",
    "Total Promptfoo failed tests"
)

security_gate_status = Gauge(
    "security_gate_status",
    "Security gate result (1=pass, 0=fail)"
)

trivy_high_critical = Gauge(
    "trivy_high_critical_vulns",
    "Number of HIGH/CRITICAL Trivy vulnerabilities"
)

def load_pipeline_metrics():
    global _metrics_loaded

    if _metrics_loaded:
        return

    # ---- Security Gate Status ----
    if GATE_STATUS_FILE.exists():
        with open(GATE_STATUS_FILE) as f:
            gate = json.load(f)
            security_gate_status.set(
                1 if gate.get("status") == "pass" else 0
            )

    # ---- Promptfoo Metrics ----
    if PROMPTFOO_REPORT.exists():
        with open(PROMPTFOO_REPORT) as f:
            data = json.load(f)

        prompts = data.get("results", {}).get("prompts", [])

        total_tests = 0
        failed_tests = 0

        for p in prompts:
            metrics = p.get("metrics", {})
            total_tests += metrics.get("testCount", 0)
            failed_tests += metrics.get("testFailCount", 0)

        if total_tests > 0:
            promptfoo_total_tests.inc(total_tests)
            promptfoo_failed_tests.inc(failed_tests)

    _metrics_loaded = True

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    load_pipeline_metrics()
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    prompt: str

@app.post("/login")
def login(data: LoginRequest):
    if data.username == "admin" and data.password == "pass123":
        token = create_jwt(data.username)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/chat")
def chat(
    data: ChatRequest,
    api_key: str = Depends(verify_api_key),
    user: str = Depends(verify_jwt)
):
    fake_response = f"[LOCAL LLM] Response to: {data.prompt}"

    scan_result = run_security_scan(data.prompt, fake_response)

    return {
        "user": user,
        "prompt": data.prompt,
        "response": fake_response,
        "security_scan": scan_result,
        "backend": "local-fallback"
    }

