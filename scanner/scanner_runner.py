from prompt_injection import scan_prompt_injection
from jailbreak import scan_jailbreak
from data_leakage import scan_data_leakage
from risk_scoring import calculate_risk

def run_security_scan(prompt: str, response: str):
    findings = []

    findings.extend(scan_prompt_injection(prompt))
    findings.extend(scan_jailbreak(prompt))
    findings.extend(scan_data_leakage(response))

    risk = calculate_risk(findings)

    return {
        "findings": findings,
        "risk": risk
    }

