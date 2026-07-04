import re
from app.config import SIGNAL_WEIGHTS, VALID_SIGNALS, RISK_THRESHOLDS, INJECTION_PATTERNS, MAX_FREE_TEXT_LENGTH, DISCLAIMER

def sanitise_input(signals):
    cleaned = {}
    for key, value in signals.items():
        if isinstance(value, str):
            for pattern in INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    return {"security_event": True, "reason": "prompt_injection_detected", "route_to_human": True}
            if len(value) > MAX_FREE_TEXT_LENGTH:
                cleaned[key] = value[:MAX_FREE_TEXT_LENGTH] + "...[truncated]"
            else:
                cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned

def calculate_risk_score(signals):
    score = 0
    for signal, value in signals.items():
        if signal not in SIGNAL_WEIGHTS:
            continue
        if value not in VALID_SIGNALS.get(signal, []):
            raise ValueError(f"Invalid value '{value}' for signal '{signal}'. Valid values: {VALID_SIGNALS[signal]}")
        score += SIGNAL_WEIGHTS[signal][value]
    return min(score, 100)

def get_risk_level(score):
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "high"

def should_escalate_crisis(score):
    return score >= RISK_THRESHOLDS["high"][0]

def get_selfcare_recommendations(signals):
    recs = []
    if signals.get("sleep") in ["poor", "fair"]:
        recs.append("Wind down 30 min before bed — no screens.")
    if signals.get("energy") == "low":
        recs.append("A 5-minute walk outside resets energy faster than rest.")
    if signals.get("social") == "no":
        recs.append("Send one message to someone you trust today.")
    if signals.get("mood") == "low":
        recs.append("Write 3 things you noticed today.")
    if not recs:
        recs.append("Your patterns look strong. Check in again tomorrow.")
    return recs

def get_crisis_resources(country="US", language="en"):
    crisis_lines = {
        "US": {"helpline": "988 Suicide and Crisis Lifeline — call or text 988", "url": "https://988lifeline.org"},
        "IN": {"helpline": "iCall — 9152987821", "url": "https://icallhelpline.org"},
        "GB": {"helpline": "Samaritans — 116 123", "url": "https://www.samaritans.org"},
        "AU": {"helpline": "Lifeline — 13 11 14", "url": "https://www.lifeline.org.au"},
        "DEFAULT": {"helpline": "International Association for Suicide Prevention", "url": "https://www.iasp.info/resources/Crisis_Centres/"}
    }
    resources = crisis_lines.get(country, crisis_lines["DEFAULT"])
    return {**resources, "language": language, "disclaimer": DISCLAIMER}
