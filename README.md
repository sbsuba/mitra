# Mitra — Global Mental Health Early Warning Agent

> *"The friend who notices — before you do."*

[![Kaggle](https://img.shields.io/badge/Kaggle-Agents%20for%20Good-blue)](https://kaggle.com)
[![Track](https://img.shields.io/badge/Track-Agents%20for%20Good-green)](https://kaggle.com)

## The Problem

Over 1 billion people globally live with a mental health condition.
75%+ in low-income countries receive zero treatment.
The average delay between symptom onset and treatment is 5-30 years.

**The core insight:** Behavioral health deterioration is rarely sudden.
Early warning signals — missed routines, reduced engagement, withdrawal
— exist in daily life but nobody is watching for them.

## The Solution

Mitra (Sanskrit/Persian for "friend") is a proactive AI agent that:
- Tracks 4 daily behavioral signals: sleep, energy, social connection, mood
- Detects early warning patterns across 7 days — not just today
- Catches warning signs before they become crises
- Connects users to global crisis resources in their language
- Works globally, in any language, free for everyone
## Architecture
User Check-in

↓

Antigravity CLI (agy) — Orchestrator

↓ A2A protocol

┌─────────────────────────────────────────┐

│ daily_checkin │ risk_scoring │ selfcare │ crisis │

│    skill      │    skill     │  skill   │ skill  │

└─────────────────────────────────────────┘

↓ MCP servers

┌─────────────────────────────────────────┐

│ signal_store  │  who_resources          │

│ (SQLite)      │  (crisis lines)         │

└─────────────────────────────────────────┘
**Risk Scoring Pipeline:**
- Sleep poor=30, fair=15, good=0
- Energy low=25, fair=10, high=0
- Social no=25, brief=12, yes=0
- Mood low=20, neutral=8, good=0
- Score 0-25: Auto-recommend (no LLM)
- Score 26-55: LLM warm analysis
- Score 56-100: Crisis escalation + human confirm

## Course Concepts Used

| Concept | Where |
|---|---|
| ADK Multi-agent | app/agent.py — 4 specialist nodes |
| MCP Server | mcp_servers/ — signal_store + who_resources |
| Antigravity | agy orchestrates everything |
| Security | STRIDE + Semgrep + hooks + sanitisation |
| Agent Skills | 4 domain skills + stride + code-review |
| Deployability | FastAPI + Agent Runtime + Pub/Sub |

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/mitra
cd mitra

# Install
pip install uv
uv venv && source .venv/bin/activate
uv pip install -e .

# Configure
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run tests
pytest tests/unit/

# Start local server
uvicorn app.fast_api_app:app --port 8080 --reload

# Test check-in
curl -X POST http://localhost:8080/checkin \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "signals": {
      "sleep": "poor",
      "energy": "low",
      "social": "no",
      "mood": "low"
    },
    "language": "en",
    "country": "US"
  }'
```

## Security

- Input sanitisation before any LLM call
- Prompt injection detection
- Pre-commit Semgrep hooks
- Agent PreToolUse hooks
- STRIDE threat model documented
- No user data stored externally
- Disclaimer on all crisis responses

## Why Mitra is Different

| Existing Apps | Mitra |
|---|---|
| Reactive — you go to them | Proactive — notices patterns |
| Single demographic | All ages, all regions |
| Paywalled | Free globally |
| Conversation only | Signal detection pipeline |
| US/UK centric | Designed for the 75% with no access |

## Disclaimer

Mitra is an awareness tool, not a clinical service.
This is not medical advice. Please consult a qualified
professional for clinical mental health support.

## License
MIT
