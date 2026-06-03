---
name: aop_consistency
description: Use when checking claims, relations, and rules for contradiction.
---

Use the Codex cognition MCP service before manual consistency review.
Prefer explicit contradictions and repair prompts over vague synthesis.

Steps:
1. Call `check_aop_consistency` on the current claims and relations.
2. Inspect the violations and crystallisation score.
3. Return the smallest repair guidance that resolves the conflict.
