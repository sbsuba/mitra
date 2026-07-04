---
name: selfcare-recommendations
description: |
  Generates personalised self-care recommendations based on Mitra signals.
  Use when risk level is low or watch and user needs actionable guidance.
  Do NOT use for high risk users - use crisis_escalation skill instead.
version: 1.0.0
license: MIT
allowed-tools: Read
---

# Self-care Recommendations Skill

## When to use
- Risk score 0-55 (low or watch level)
- User needs one actionable thing to do today
- After risk scoring completes

## When NOT to use
- Risk score 56+ - use crisis_escalation instead
- User is in active crisis

## Recommendation Logic
See references/low_risk_actions.md for low risk actions
See references/watch_risk_actions.md for watch risk actions
See references/cultural_adaptations.md for cultural context

## Signal to Action Mapping
sleep poor/fair - wind down 30 min before bed, no screens
energy low      - 5 minute walk outside, movement resets energy
social no       - send one message to someone you trust today
mood low        - write 3 things you noticed today, not grateful for

## Tone Rules
- One priority action, not a list of 10
- Specific and achievable today
- Warm like a friend, not prescriptive like a doctor
- Never say "you should" - say "how about" or "try this"

## Output format
1 primary recommendation
1 optional secondary recommendation
Always end with: "Check in again tomorrow"
