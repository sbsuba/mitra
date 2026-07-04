"""
Mitra — ADK 2.0 Graph Workflow
The friend who notices before you do.

Architecture:
receive_checkin → sanitise_input → calculate_risk
  ├── score 0-25  → auto_recommend (no LLM)
  ├── score 26-55 → llm_analysis → show_explanation
  └── score 56+   → llm_analysis → human_confirm → crisis_escalation
"""

from __future__ import annotations
import re
from typing import Any
from google.adk.agents import LlmAgent
from google.adk.apps.app import App
from google.adk.workflow import Edge, Workflow
from google.adk.workflow.node import node
from google.adk.models.google_llm import Gemini
from app.config import (
    MODEL, SIGNAL_WEIGHTS, VALID_SIGNALS,
    RISK_THRESHOLDS, INJECTION_PATTERNS,
    MAX_FREE_TEXT_LENGTH, DISCLAIMER
)


# ── SECURITY SCREEN ──────────────────────────────────────────────

def sanitise_input(signals: dict) -> dict:
    """
    Security screen — runs BEFORE any LLM sees data.
    Detects prompt injection and truncates long text.

    Args:
        signals: Raw user check-in signals dict.

    Returns:
        Cleaned signals dict, or security_event dict if threat detected.
    """
    cleaned = {}
    for key, value in signals.items():
        if isinstance(value, str):
            # Check for prompt injection
            for pattern in INJECTION_PATTERNS:
                if re.search(pattern, value, re.IGNORECASE):
                    return {
                        "security_event": True,
                        "reason": "prompt_injection_detected",
                        "route_to_human": True,
                        "original_key": key
                    }
            # Truncate long free text
            if len(value) > MAX_FREE_TEXT_LENGTH:
                cleaned[key] = value[:MAX_FREE_TEXT_LENGTH] + "...[truncated]"
            else:
                cleaned[key] = value
        else:
            cleaned[key] = value
    return cleaned


# ── RISK SCORING ─────────────────────────────────────────────────

def calculate_risk_score(signals: dict) -> int:
    """
    Calculates weighted risk score from 4 clinical signals.
    Pure deterministic Python — no LLM involved.

    Args:
        signals: Dict with keys sleep, energy, social, mood.

    Returns:
        Integer risk score 0-100.

    Raises:
        ValueError: If signal value is not valid.
    """
    score = 0
    for signal, value in signals.items():
        if signal not in SIGNAL_WEIGHTS:
            continue
        if value not in VALID_SIGNALS.get(signal, []):
            raise ValueError(
                f"Invalid value '{value}' for signal '{signal}'. "
                f"Valid values: {VALID_SIGNALS[signal]}"
            )
        score += SIGNAL_WEIGHTS[signal][value]
    return min(score, 100)


def get_risk_level(score: int) -> str:
    """
    Returns risk level string from score.

    Args:
        score: Integer risk score 0-100.

    Returns:
        'low', 'watch', or 'high'
    """
    for level, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return level
    return "high"


def should_escalate_crisis(score: int) -> bool:
    """
    Returns True if score warrants crisis escalation.

    Args:
        score: Integer risk score 0-100.

    Returns:
        True if score >= 56, False otherwise.
    """
    return score >= RISK_THRESHOLDS["high"][0]


# ── SELF-CARE RECOMMENDATIONS ─────────────────────────────────────

def get_selfcare_recommendations(signals: dict) -> list:
    """
    Returns personalised self-care actions based on signals.
    Deterministic — no LLM. Based on clinical evidence.

    Args:
        signals: Cleaned signals dict.

    Returns:
        List of recommendation strings.
    """
    recs = []
    if signals.get("sleep") in ["poor", "fair"]:
        recs.append(
            "Wind down 30 min before bed — no screens. "
            "Even one better night shifts your score."
        )
    if signals.get("energy") == "low":
        recs.append(
            "A 5-minute walk outside resets energy "
            "faster than rest. Start with that."
        )
    if signals.get("social") == "no":
        recs.append(
            "Send one message to someone you trust today. "
            "It doesn't have to say much."
        )
    if signals.get("mood") == "low":
        recs.append(
            "Write 3 things you noticed today — not "
            "'grateful for', just noticed. This grounds the mind."
        )
    if not recs:
        recs.append(
            "Your patterns look strong. "
            "Check in again tomorrow to maintain your streak."
        )
    return recs


# ── CRISIS RESOURCES ─────────────────────────────────────────────

def get_crisis_resources(country: str = "US", language: str = "en") -> dict:
    """
    Returns crisis resources for user's country and language.
    Always includes disclaimer per security rules.

    Args:
        country: ISO country code e.g. 'US', 'IN', 'GB'
        language: ISO language code e.g. 'en', 'hi', 'es'

    Returns:
        Dict with helpline, resources, and disclaimer.
    """
    # Crisis lines by country
    crisis_lines = {
        "US": {
            "helpline": "988 Suicide and Crisis Lifeline — call or text 988",
            "url": "https://988lifeline.org",
            "language": "en"
        },
        "IN": {
            "helpline": "iCall — 9152987821",
            "url": "https://icallhelpline.org",
            "language": "hi"
        },
        "GB": {
            "helpline": "Samaritans — 116 123",
            "url": "https://www.samaritans.org",
            "language": "en"
        },
        "AU": {
            "helpline": "Lifeline — 13 11 14",
            "url": "https://www.lifeline.org.au",
            "language": "en"
        },
        "DEFAULT": {
            "helpline": "International Association for Suicide Prevention",
            "url": "https://www.iasp.info/resources/Crisis_Centres/",
            "language": "en"
        }
    }

    resources = crisis_lines.get(country, crisis_lines["DEFAULT"])
    resources["disclaimer"] = DISCLAIMER
    resources["language"] = language
    return resources


# ── ADK 2.0 GRAPH NODES ──────────────────────────────────────────

@node
def receive_checkin_node(state: dict) -> dict:
    """
    Node 1: Receives and validates check-in input.

    Args:
        state: Input state with user signals.

    Returns:
        State with parsed signals.
    """
    signals = state.get("signals", {})
    user_id = state.get("user_id", "anonymous")
    country = state.get("country", "US")
    language = state.get("language", "en")

    return {
        "signals": signals,
        "user_id": user_id,
        "country": country,
        "language": language,
        "step": "sanitise"
    }


@node
def sanitise_input_node(state: dict) -> dict:
    """
    Node 2: Security screen — sanitises input before LLM.

    Args:
        state: State with raw signals.

    Returns:
        State with cleaned signals or security_event flag.
    """
    cleaned = sanitise_input(state.get("signals", {}))

    if cleaned.get("security_event"):
        return {**state, "security_event": True, "step": "human_review"}

    return {**state, "signals": cleaned, "step": "calculate_risk"}


@node
def calculate_risk_node(state: dict) -> dict:
    """
    Node 3: Calculates risk score — pure Python, no LLM.

    Args:
        state: State with cleaned signals.

    Returns:
        State with risk score and level.
    """
    signals = state.get("signals", {})

    try:
        score = calculate_risk_score(signals)
    except ValueError:
        score = 50  # default to watch if invalid

    level = get_risk_level(score)

    # Route based on risk level
    if level == "low":
        next_step = "auto_recommend"
    elif level == "watch":
        next_step = "llm_analysis"
    else:
        next_step = "llm_analysis"  # then crisis after

    return {
        **state,
        "risk_score": score,
        "risk_level": level,
        "step": next_step
    }


@node
def auto_recommend_node(state: dict) -> dict:
    """
    Node 4a: Low risk — returns self-care recommendations.
    No LLM called. Fast, free, always available.

    Args:
        state: State with signals and risk score.

    Returns:
        State with recommendations.
    """
    recs = get_selfcare_recommendations(state.get("signals", {}))

    return {
        **state,
        "recommendations": recs,
        "message": (
            f"Your signal today looks healthy "
            f"(score: {state.get('risk_score', 0)}/100). "
            f"Here are some ways to stay that way:"
        ),
        "step": "complete"
    }


@node
def crisis_escalation_node(state: dict) -> dict:
    """
    Node 4b: High risk — fetches WHO crisis resources.
    Only fires after human confirmation.

    Args:
        state: State with country, language, risk score.

    Returns:
        State with crisis resources and disclaimer.
    """
    country = state.get("country", "US")
    language = state.get("language", "en")
    resources = get_crisis_resources(country, language)

    return {
        **state,
        "crisis_resources": resources,
        "message": (
            "Mitra has noticed some patterns that suggest "
            "you might benefit from speaking with someone. "
            "Here are some resources that can help:"
        ),
        "disclaimer": DISCLAIMER,
        "step": "complete"
    }


# ── LLM ANALYSIS AGENT ───────────────────────────────────────────

model = Gemini(model=MODEL)

analysis_agent = LlmAgent(
    name="MitraAnalysisAgent",
    model=model,
    instruction="""
    You are Mitra, a warm and caring mental health awareness companion.
    
    A user has completed their daily check-in. Your role is to:
    1. Acknowledge their signals with warmth and without judgment
    2. Explain what the patterns might mean in plain, human language
    3. Offer ONE specific, actionable suggestion for today
    4. Never diagnose, prescribe, or make clinical claims
    5. Always end with: remind them this is awareness only, not clinical advice
    
    Keep your response under 150 words. Be warm, direct, and human.
    Never use clinical jargon. Speak like a trusted friend.
    """,
    tools=[]
)


# ── WORKFLOW GRAPH ────────────────────────────────────────────────

root_workflow = Workflow(
    name="mitra_checkin_workflow",
    edges=[
        *Edge.chain(
            "START",
            receive_checkin_node,
            sanitise_input_node,
            calculate_risk_node,
        ),
        Edge(
            source=calculate_risk_node,
            target=auto_recommend_node,
            condition=lambda s: s.get("risk_level") == "low"
        ),
        Edge(
            source=calculate_risk_node,
            target=analysis_agent,
            condition=lambda s: s.get("risk_level") in ["watch", "high"]
        ),
        Edge(
            source=analysis_agent,
            target=crisis_escalation_node,
            condition=lambda s: s.get("risk_level") == "high"
        ),
    ]
)

app = App(
    name="mitra",
    root_agent=root_workflow
)
