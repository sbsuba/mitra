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
def store_checkin_result(state: dict) -> dict:
    """
    Prepares check-in result for MCP signal store.
    Called after risk scoring completes.
    Enables 7-day longitudinal pattern detection.

    Args:
        state: State dict with user_id, signals, risk_score, risk_level.

    Returns:
        State with stored=True flag.
    """
    from datetime import date
    result = {
        "user_id": state.get("user_id", "anonymous"),
        "date": str(date.today()),
        "sleep": state.get("signals", {}).get("sleep"),
        "energy": state.get("signals", {}).get("energy"),
        "social": state.get("signals", {}).get("social"),
        "mood": state.get("signals", {}).get("mood"),
        "risk_score": state.get("risk_score", 0),
        "risk_level": state.get("risk_level", "unknown")
    }
    # In production: call signal_store MCP server
    # mcp_client.call_tool("store_checkin", result)
    return {**state, "stored": True, "stored_result": result}


def get_longitudinal_trend(history: list) -> dict:
    """
    Analyses 7-day check-in history to detect pattern shifts.
    This is Mitra's core differentiator — pattern not snapshot.

    Args:
        history: List of daily check-in dicts with risk_score.

    Returns:
        Dict with trend direction, average, and insight text.
    """
    if not history:
        return {"trend": "no_data", "average": 0, "insight": ""}

    scores = [h.get("risk_score", 0) for h in history[-7:]]
    avg = sum(scores) / len(scores)

    if len(scores) >= 3:
        recent = sum(scores[-3:]) / 3
        earlier = sum(scores[:3]) / 3
        if recent < earlier - 10:
            trend = "improving"
            insight = f"Your average risk score has dropped from {int(earlier)} to {int(recent)} over the last week. That is real progress."
        elif recent > earlier + 10:
            trend = "deteriorating"
            insight = f"Mitra has noticed your scores rising over the last week — from {int(earlier)} to {int(recent)}. This pattern is worth addressing today."
        else:
            trend = "stable"
            insight = f"Your patterns have been relatively stable this week, averaging {int(avg)}."
    else:
        trend = "insufficient_data"
        insight = "Keep checking in — Mitra needs 7 days to detect patterns."

    return {
        "trend": trend,
        "average": round(avg, 1),
        "scores": scores,
        "insight": insight
    }
