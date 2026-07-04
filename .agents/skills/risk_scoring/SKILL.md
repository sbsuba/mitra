---
name: risk-scoring
description: |
  Calculates Mitra risk score from 4 daily signals using clinical weights.
  Use when check-in signals are collected and need to be scored.
  Do NOT use for crisis intervention or self-care recommendations.
version: 1.0.0
license: MIT
allowed-tools: Read Bash
---

# Risk Scoring Skill

## When to use
- After daily_checkin skill collects all 4 signals
- When calculating longitudinal risk trend over 7 days
- When routing user to correct next step

## When NOT to use
- Before all 4 signals are collected
- For clinical diagnosis - this is awareness only

## Scoring Logic
sleep:  poor=30, fair=15, good=0
energy: low=25,  fair=10, high=0
social: no=25,   brief=12, yes=0
mood:   low=20,  neutral=8, good=0
Total max = 100

## Risk Levels
0-25:   low   - auto_recommend, no LLM needed
26-55:  watch - LLM analysis, show warm explanation
56-100: high  - crisis escalation + human confirm

## Examples
Input: sleep=poor, energy=low, social=no, mood=low
Output: score=100, level=high, route=crisis_escalation

Input: sleep=fair, energy=fair, social=brief, mood=neutral
Output: score=45, level=watch, route=llm_analysis

Input: sleep=good, energy=high, social=yes, mood=good
Output: score=0, level=low, route=auto_recommend

## Security
Run sanitise_input BEFORE scoring
Never pass raw user text to LLM without sanitisation
