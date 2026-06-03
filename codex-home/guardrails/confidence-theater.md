---
name: confidence-theater
description: Prevent inflated confidence scores. Require honest confidence levels backed by evidence, and enforce review triggers at low confidence.
---

# Confidence Theater

## Purpose
Prevent agents from inflating confidence to avoid review. Honest confidence scores with evidence enable better decision-making.

## Hard Rules

1. **Honest Confidence Scoring**: Every output must include a confidence score:
   - **High (90-100%)**: Verified by Tier 1 sources, tests pass, LSP clean
   - **Medium (60-89%)**: Verified by Tier 2 sources, some uncertainty remains
   - **Low (0-59%)**: Unverified, assumptions present, or contradictory evidence exists

2. **Evidence Required for High Confidence**: A claim of high confidence (≥90%) must include:
   - At least one Tier 1 verification source
   - Test results confirming the claim
   - No contradictory evidence from LSP or knowledge graph

3. **Review Trigger at Medium Confidence**: Any output with confidence <80% must trigger:
   - Oracle review before proceeding
   - Additional verification steps
   - Explicit documentation of remaining uncertainty

4. **Review Trigger at Low Confidence**: Any output with confidence <60% must trigger:
   - Stop implementation
   - Escalate to user for clarification
   - Document what information is missing

5. **No Confidence Without Evidence**: Never state "I'm confident" or "this should work" without citing specific evidence. Replace with:
   ```yaml
   confidence: <percentage>
   evidence:
     - source: <verification tool or source>
       finding: <what was verified>
   remaining_uncertainty: <what is still unknown>
   ```

## Mechanisms

- `cognition_codex_check_aop_consistency` — verify logical consistency of claims
- `treesitter_summarize_path` — verify code structure claims
- `codex_knowledge_graph_query` — verify relationship claims
- LSP diagnostics — verify type and reference claims
- Test results — verify behavioral claims

## Enforcement

- Oracle review checks confidence scores and evidence
- Low-confidence outputs are flagged for additional verification
- Confidence inflation (claiming high confidence without evidence) is treated as a hallucination
