import re

SENSITIVE_PATTERNS = {
    "Email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "Phone": r"\+?\d{10,13}",
    "CreditCard": r"\b(?:\d[ -]*?){13,16}\b",
    "APIKey": r"(sk|hf)_[A-Za-z0-9]{20,}",
}

def scan_data_leakage(text: str):
    findings = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append(f"Sensitive Data Detected: {label}")
    return findings

