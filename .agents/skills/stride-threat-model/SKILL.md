---
name: stride-threat-model
description: |
  Performs STRIDE threat modeling assessment on Mitra codebase.
  Use when starting a new implementation phase or reviewing security.
  Do NOT use for general code review - use code-review skill instead.
version: 1.0.0
license: MIT
allowed-tools: Read Bash Write
---

# STRIDE Threat Modeling Skill for Mitra

## When to use
- Before adding new features to Mitra
- When reviewing security boundaries
- Before deployment to production

## STRIDE Evaluation

### Spoofing
- Can a user impersonate another user check-in history?
- Are user IDs verified before accessing longitudinal data?

### Tampering
- Can users manipulate risk scores through crafted inputs?
- Can prompt injection force low risk scores for high-risk users?

### Repudiation
- Are crisis escalation events logged immutably?
- Can we prove the agent showed resources to a high-risk user?

### Information Disclosure
- Does any mental health signal data appear in logs?
- Does the LLM response ever echo back raw user input?

### Denial of Service
- Is there a circuit breaker on API calls?
- Can a user trigger infinite risk scoring loops?

### Elevation of Privilege
- Can a low-risk user trigger crisis escalation?
- Can unauthenticated requests access stored signals?

## Output
Generate threat_model.md in mitra/ root with findings
and recommended mitigations for each STRIDE category.
