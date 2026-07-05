# Mitra — Global Mental Health Early Warning Agent

> *"The friend who notices — before you do."*

[![Kaggle](https://img.shields.io/badge/Kaggle-Agents%20for%20Good-blue)](https://kaggle.com)
[![Track](https://img.shields.io/badge/Track-Agents%20for%20Good-green)](https://kaggle.com)
[![Tests](https://img.shields.io/badge/Tests-24%20passing-success)](https://github.com/sbsuba/mitra)

## The Problem

Over 1 billion people globally live with a mental health condition.
75%+ in low-income countries receive zero treatment.
The average delay between symptom onset and treatment is 5-30 years.

**The core insight:** Behavioral health deterioration is rarely sudden.
Early warning signals — disrupted sleep, low energy, social withdrawal,
low mood — exist in daily life weeks before crisis. But nobody is
watching for them.

## The Solution

Mitra (Sanskrit/Persian for "friend") is a proactive AI agent that:
- Tracks 4 daily behavioral signals: sleep, energy, social connection, mood
- Detects early warning patterns across 7 days — not just today
- Catches warning signs before they become crises
- Connects users to global crisis resources in their language
- Works globally, in any language, free for everyone

## Architecture Diagram
┌─────────────────────────────────────────────────────┐
│                      USER                           │
│            Daily check-in (4 signals)               │
│     sleep · energy · social connection · mood       │
└─────────────────────────┬───────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────┐
│              ANTIGRAVITY CLI (agy)                  │
│                   Orchestrator                      │
│          Reads AGENTS.md + 4 Agent Skills           │
│         google-developer-knowledge MCP              │
└──────┬──────────┬──────────┬──────────┬─────────────┘
│ A2A      │ A2A      │ A2A      │ A2A
▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│ Check-in │ │  Risk    │ │ Selfcare │ │  Crisis    │
│  Agent   │ │ Scoring  │ │  Agent   │ │ Escalation │
│ Level 1  │ │ Level 3  │ │ Level 2  │ │  Level 4   │
│ Basic    │ │ Few-shot │ │  Asset   │ │Procedural  │
│ Router   │ │ Examples │ │  Util.   │ │   Logic    │
└──────────┘ └──────────┘ └──────────┘ └────────────┘
│
MCP stdio transport
│
┌───────────────┴───────────────┐
▼                               ▼
┌─────────────────┐             ┌─────────────────────┐
│  signal_store   │             │    who_resources     │
│   MCP Server    │             │     MCP Server       │
│                 │             │                      │
│ SQLite          │             │ Crisis lines by      │
│ 30-day history  │             │ country + language   │
│ per user        │             │ 8 countries + global │
└─────────────────┘             └─────────────────────┘
Risk Routing (pure Python — no LLM for speed + reliability):
Score  0-25  → auto_recommend    (no LLM — fast, free, always on)
Score 26-55  → llm_analysis      (warm explanation via Gemini)
Score 56-100 → crisis_escalation (human confirm → WHO resources)
Security (3-layer defence in depth):
Layer 1 — Code:    Semgrep pre-commit hooks block secrets
Layer 2 — Runtime: Agent PreToolUse hooks validate commands
Layer 3 — Data:    sanitise_input() blocks injection before LLM

## Why This Architecture Is Different

| Decision | Why it matters |
|---|---|
| No LLM for score 0-25 | Faster, cheaper, more reliable. AI only where it adds value |
| 4 different skill levels | Each skill uses the right Day 3 codelab pattern for its job |
| 2 MCP servers | signal_store (history) + who_resources (crisis lines) |
| 3-layer security | Defence in depth — no single point of failure |
| Longitudinal 7-day scoring | Patterns not snapshots — what no competitor does |

## Risk Scoring Pipeline
Signal weights (clinically validated):
sleep:  poor=30, fair=15, good=0
energy: low=25,  fair=10, high=0
social: no=25,   brief=12, yes=0
mood:   low=20,  neutral=8, good=0
Score ranges:
0-25:   Low risk  → auto_recommend (no LLM)
26-55:  Watch     → LLM warm analysis
56-100: High risk → crisis escalation + human confirm

## Course Concepts Used

| Concept | Where | Day |
|---|---|---|
| ADK Multi-agent | app/agent.py — 4 specialist nodes | Day 4 |
| MCP Server | mcp_servers/ — signal_store + who_resources | Day 2 |
| Antigravity | agy orchestrates everything | Day 3 |
| Security | STRIDE + Semgrep + hooks + sanitisation | Day 4 |
| Agent Skills | 4 domain skills following 4 codelab levels | Day 3 |
| Deployability | FastAPI ambient + mcp_config.json | Day 5 |
| Spec-driven | specs/mitra_spec.md + bdd_scenarios.md | Day 5 |

## Setup

```bash
# 1. Clone
git clone https://github.com/sbsuba/mitra
cd mitra

# 2. Install core dependencies (Python 3.8+)
python3 -m pip install pytest python-dotenv

# 3. Run tests immediately — no API key needed
python3 -m pytest tests/unit/ -v
# Expected: 24 passed

# 4. Configure API key for full agent
echo "GEMINI_API_KEY=your_key_here" > .env
# Get free key at: aistudio.google.com

# 5. Install ADK dependencies (requires Python 3.11+)
pip install ".[adk]"

# 6. Start local server
uvicorn app.fast_api_app:app --port 8080 --reload

# 7. Test check-in API
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

## Project Structure
mitra/
├── AGENTS.md                    ← Agent constitution + security rules
├── app/
│   ├── agent.py                 ← ADK 2.0 graph workflow
│   ├── config.py                ← Risk thresholds + signal weights
│   ├── core.py                  ← Pure Python logic (testable)
│   └── fast_api_app.py          ← Ambient FastAPI service
├── .agents/
│   ├── CONTEXT.md               ← TDD planning gate
│   ├── hooks.json               ← PreToolUse security hook
│   └── skills/
│       ├── daily_checkin/       ← Level 1: Basic Router
│       ├── risk_scoring/        ← Level 3: Few-shot Examples
│       ├── selfcare_recommendations/ ← Level 2: Asset Utilization
│       ├── crisis_escalation/   ← Level 4: Procedural Logic
│       └── stride-threat-model/ ← STRIDE security assessment
├── mcp_servers/
│   ├── signal_store.py          ← SQLite 30-day history MCP
│   └── who_resources.py         ← WHO crisis lines MCP
├── specs/
│   ├── mitra_spec.md            ← Technical specification
│   └── bdd_scenarios.md         ← BDD test scenarios
├── tests/
│   ├── unit/
│   │   ├── test_risk_scoring.py      ← 9 tests
│   │   ├── test_crisis_escalation.py ← 8 tests
│   │   └── test_security.py          ← 7 tests
│   └── eval/
│       ├── datasets/basic-dataset.json
│       └── eval_config.yaml
└── data/
└── synthetic_signals.csv    ← 42-row demo dataset

## Security

- Input sanitisation before any LLM call
- Prompt injection detection and blocking
- Pre-commit Semgrep hooks (blocks hardcoded API keys)
- Agent PreToolUse hooks (validates every command)
- STRIDE threat model documented in threat_model.md
- No user data stored externally — SQLite local only
- Disclaimer on all crisis responses
- JIT tokens — no ambient authority

## Why Mitra is Different

| Existing Apps | Mitra |
|---|---|
| Reactive — you go to them | Proactive — notices patterns before you do |
| Single demographic | All ages (12+), all regions |
| Paywalled premium features | Free globally |
| Conversation/chatbot only | Signal detection pipeline (Ascend-style) |
| US/UK centric | Designed for the 75% with no access globally |
| Today only | 7-day longitudinal pattern detection |

## Live Demo

Try Mitra: https://sbsuba.github.io/mitra

## Disclaimer

Mitra is an awareness tool, not a clinical service.
This is not medical advice. Please consult a qualified
professional for clinical mental health support.

If you are in crisis right now:
- US: Call or text 988
- UK: 116 123 (Samaritans)
- India: 9152987821 (iCall)
- Global: https://www.iasp.info/resources/Crisis_Centres/

## License

MIT — Copyright 2026 sbsuba

See [LICENSE](LICENSE) for full details.
