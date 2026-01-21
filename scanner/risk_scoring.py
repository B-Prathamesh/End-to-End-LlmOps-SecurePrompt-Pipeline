def calculate_risk(findings: list):
    score = 0

    for finding in findings:
        if "Injection" in finding:
            score += 3
        if "Jailbreak" in finding:
            score += 4
        if "Sensitive" in finding:
            score += 5

    if score >= 10:
        level = "CRITICAL"
    elif score >= 6:
        level = "HIGH"
    elif score >= 3:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": score, "level": level}

