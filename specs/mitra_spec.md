# Mitra — Technical Specification v1.0

## Background
1 billion+ people globally have mental health conditions.
75%+ in low-income countries receive zero treatment.
Average delay to treatment: 5-30 years.
Mitra catches early warning signals before crisis escalates.
Name: Sanskrit/Persian for "friend" — 3,500 years old.

## Problem Statement
"Hundreds of millions worldwide are heading toward a mental
health crisis they don't yet recognize in themselves, with no
accessible, private, culturally aware system to help them
notice the warning signs early enough to act."

## Architecture
ADK 2.0 graph workflow with 4 specialist nodes:
1. receive_checkin → sanitise_input → calculate_risk
2. Low risk (0-25): auto_recommend (no LLM)
3. Watch risk (26-55): llm_analysis → show_explanation
4. High risk (56+): llm_analysis → human_confirm → crisis_escalation

## Signal Weights
```yaml
sleep:  poor: 30, fair: 15, good: 0
energy: low: 25,  fair: 10, high: 0
social: no: 25,   brief: 12, yes: 0
mood:   low: 20,  neutral: 8, good: 0
```

## Risk Thresholds
```yaml
low:   0-25   # auto_recommend, no LLM
watch: 26-55  # llm_analysis
high:  56-100 # crisis_escalation + human confirm
```

## MCP Servers
- signal_store: SQLite, 30-day history, stdio transport
- who_resources: WHO crisis lines by country/language, SSE

## Security
- Input sanitisation before LLM
- Prompt injection detection
- JIT tokens, no ambient authority
- Pre-commit Semgrep hooks
- Agent PreToolUse hooks
- STRIDE threat model documented

## Libraries
```yaml
google-adk: ">=2.0.0a0"
google-genai: ">=1.0.0"
fastapi: ">=0.110.0"
uvicorn: ">=0.27.0"
pydantic: ">=2.0.0"
mcp: ">=1.0.0"
pytest: ">=8.0.0"
```
