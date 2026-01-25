import json
import sys
from pathlib import Path

REPORT_FILE = Path("reports/promptfoo-results.json")

if not REPORT_FILE.exists():
    print("❌ Promptfoo report not found.")
    sys.exit(1)

with open(REPORT_FILE) as f:
    data = json.load(f)

prompts = data.get("results", {}).get("prompts", [])

failures = []

for p in prompts:
    raw_prompt = p.get("raw", "")
    metrics = p.get("metrics", {})

    fail_count = metrics.get("testFailCount", 0)
    error_count = metrics.get("testErrorCount", 0)

    if fail_count > 0 or error_count > 0:
        failures.append({
            "prompt": raw_prompt,
            "fails": fail_count,
            "errors": error_count
        })

if failures:
    print("❌ SECURITY GATE FAILED\n")
    for f in failures:
        print(f"Prompt: {f['prompt']}")
        print(f"  ❌ Fails: {f['fails']}, Errors: {f['errors']}\n")
    sys.exit(1)

print("✅ SECURITY GATE PASSED")
sys.exit(0)

