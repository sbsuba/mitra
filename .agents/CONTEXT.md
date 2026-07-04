# Mitra Project Context

## Stack
- ADK 2.0 graph workflow API (NOT 1.x SequentialAgent)
- Gemini 3.1 Flash Lite
- Python 3.11+, FastAPI, SQLite, MCP

## Security Rules
1. NEVER hardcode API keys — use .env only
2. NEVER store user mental health data externally
3. NEVER pass raw user input to LLM without sanitisation
4. NEVER call crisis resources without user confirmation
5. ALWAYS add disclaimer: "This is not clinical advice"
6. ALWAYS sanitise check-in text fields for injection

## TDD Planning Gate
Every plan MUST include Security Boundaries & Assertions:
- What inputs could be malicious
- What data must never reach the LLM
- What requires user confirmation
- Crisis escalation trigger conditions
