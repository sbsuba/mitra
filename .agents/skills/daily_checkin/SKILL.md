---
name: daily-checkin
description: |
  Conducts Mitra daily 4-question mental health check-in with a user.
  Use when the user wants to check in, start their daily assessment,
  report how they are feeling, or track their mental wellness today.
  Do NOT use for crisis support, resource lookup, or historical analysis.
version: 1.0.0
license: MIT
allowed-tools: Read
---

# Daily Check-in Skill

## When to use
- User says "check in", "how am I doing", "start my daily check"
- User wants to report their mood, sleep, or energy today
- User opens Mitra for the first time each day

## When NOT to use
- User is already in crisis - use crisis_escalation skill
- User wants history - query signal store directly

## The 4 Questions in order
1. How did you sleep last night? poor/fair/good
2. How is your energy today? low/fair/high
3. Have you connected with anyone in last 48 hours? no/brief/yes
4. How is your overall mood right now? low/neutral/good

## Tone Rules
- Warm, non-judgmental, never clinical
- Ask one question at a time, never all 4 at once
- Never make user feel judged for any answer

## Output format
Return structured signals: sleep, energy, social, mood
