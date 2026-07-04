# Mitra — Global Mental Health Early Warning Agent
# Sanskrit/Persian: "friend, companion, the one who notices"
# Tagline: "The friend who notices — before you do"

## Project Overview
Mitra is a proactive behavioral health early-warning agent that detects
personal disengagement patterns before they become crises, and guides
individuals toward self-care — globally, in any language, free for everyone.

## Stack
- ADK 2.0 graph workflow API (NOT 1.x SequentialAgent)
- Gemini 3.1 Flash Lite (gemini-3.1-flash-lite)
- Python 3.11+
- SQLite for local signal storage
- FastAPI for ambient trigger endpoint
- MCP for WHO resource lookup

## Coding Standards
- Use Google Style Docstrings for all functions
- Match existing naming patterns when editing files
- Always include version numbers for every library
- One PR per feature — never mix bug fix with refactor
- Max function length: 50 lines
- Use ADK 2.0 graph API only — never 1.x SequentialAgent

## The 4 Clinical Signals
sleep:  poor=30pts, fair=15pts, good=0pts
energy: low=25pts,  fair=10pts, high=0pts
social: no=25pts,   brief=12pts, yes=0pts
mood:   low=20pts,  neutral=8pts, good=0pts

## Risk Thresholds
low:   0-25   → auto_recommend (no LLM)
watch: 26-55  → llm_analysis
high:  56-100 → crisis_escalation + human confirm

## Security Rules (Non-negotiable)
1. NEVER hardcode API keys — use .env only
2. NEVER store user mental health data externally
3. NEVER pass raw user input to LLM without sanitisation
4. NEVER call crisis resources without user confirmation
5. ALWAYS add disclaimer: "This is not clinical advice"
6. ALWAYS show risk explanation before escalation
7. ALWAYS sanitise check-in text fields for injection
8. ALWAYS include crisis helpline even at low risk

## TDD Planning Gate
Every plan MUST include Security Boundaries & Assertions:
- What inputs could be malicious
- What data must never reach the LLM
- What requires user confirmation
- Crisis escalation trigger conditions

## Execution Modes
- Project Generation: propose structure first, confirm before coding
- Feature Generation: match existing style, show diff before applying
- Bug Fixing: evidence prompting only, write failing test first
- Documentation: keep README.md and CHANGELOG.md in sync always

## Agent Architecture
receive_checkin → sanitise_input → calculate_risk
  ├── score 0-25  → auto_recommend (no LLM)
  ├── score 26-55 → llm_analysis → show_explanation
  └── score 56+   → llm_analysis → human_confirm → crisis_escalation
