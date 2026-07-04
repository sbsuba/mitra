"""
Mitra Configuration
Central config for risk thresholds, model, and signal weights.
All business rules live here — never hardcoded in agent logic.
"""

# Model
MODEL = "gemini-3.1-flash-lite"

# Risk thresholds
RISK_THRESHOLDS = {
    "low":   (0,  25),   # auto-recommend, no LLM
    "watch": (26, 55),   # LLM analysis
    "high":  (56, 100)   # crisis escalation + human confirm
}

# Signal weights — clinically validated early warning signals
SIGNAL_WEIGHTS = {
    "sleep":  {"poor": 30, "fair": 15, "good": 0},
    "energy": {"low":  25, "fair": 10, "high": 0},
    "social": {"no":   25, "brief": 12, "yes": 0},
    "mood":   {"low":  20, "neutral": 8, "good": 0}
}

# Valid signal values
VALID_SIGNALS = {
    "sleep":  ["poor", "fair", "good"],
    "energy": ["low",  "fair", "high"],
    "social": ["no",   "brief", "yes"],
    "mood":   ["low",  "neutral", "good"]
}

# Security
MAX_API_CALLS_PER_SESSION = 3  # circuit breaker
MAX_FREE_TEXT_LENGTH = 200     # truncate beyond this

# Injection patterns to block
INJECTION_PATTERNS = [
    "ignore previous",
    "bypass",
    "system prompt",
    "forget instructions",
    "auto-approve",
    "auto approve",
    "you are now",
    "disregard",
    "override"
]

# Disclaimer — must appear in ALL crisis responses
DISCLAIMER = (
    "This is not clinical advice. "
    "Mitra is an awareness tool, not a medical service. "
    "Please consult a qualified professional for clinical support."
)
