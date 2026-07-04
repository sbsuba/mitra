---
name: crisis-escalation
description: |
  Fetches WHO crisis resources when Mitra detects high risk signals.
  Use ONLY when risk score is 56 or above AND user has confirmed.
  Do NOT use for low or watch risk, or without user confirmation first.
version: 1.0.0
license: MIT
allowed-tools: Read Bash
---

# Crisis Escalation Skill

## When to use
- Risk score >= 56 (high level only)
- User has explicitly confirmed they want resources
- After human_confirm node approves escalation

## When NOT to use
- Risk score below 56
- Without user confirmation - NEVER auto-escalate
- As a replacement for emergency services

## Workflow
1. Run scripts/escalate.py with user country and language
2. Script fetches resources from who_resources MCP server
3. Return resources with disclaimer
4. Log escalation event for audit trail

## Security Rules
- NEVER escalate without user confirmation
- ALWAYS include disclaimer in response
- NEVER store crisis interaction details externally
- Log escalation timestamp for governance audit

## Required Output Fields
- helpline: string with phone number
- url: string with resource URL
- disclaimer: must contain "not clinical advice"
- language: must match user requested language

## Disclaimer
Always append: "This is not clinical advice. Mitra is an awareness
tool not a medical service. Please consult a qualified professional."

## Anti-patterns to avoid
- Don't auto-escalate without confirmation
- Don't skip disclaimer ever
- Don't recommend specific therapists or medications
