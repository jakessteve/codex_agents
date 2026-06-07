---
name: claim-verification
description: Require verification of claims from other agents before acting on them. Enforce source tiering and evidence requirements.
---

# Claim Verification

## Purpose
Prevent cascading errors by requiring that claims from other agents are verified before being acted upon.

## Hard Rules

1. **Never Trust Unverified Claims**: When another agent makes a claim (file path, API behavior, test result, configuration value), verify it independently before acting on it.

2. **Source Tiering for Claims**:
   - **Tier 1 (Trusted)**: Claims verified by reading the actual source code, running the actual command, or checking LSP diagnostics
   - **Tier 2 (Probable)**: Claims from project knowledge graph, memory, or wiki docs
   - **Tier 3 (Unverified)**: Claims from model reasoning, assumptions, or "I think" statements
   - Act on Tier 1 immediately. Verify Tier 2 before acting. Never act on Tier 3 without upgrading to Tier 1 or 2.

3. **Cross-Reference Requirement**: For any claim that affects implementation (file paths, function signatures, data structures, configuration values), cross-reference at least two independent sources.

4. **Evidence Trail**: Record the verification source for every claim:
   ```yaml
   claim_verification:
     claim: <what was claimed>
     source: <who claimed it>
     verified_by: <tool or source used to verify>
     verification_result: <confirmed|refuted|unverifiable>
     action: <proceed|investigate|reject>
   ```

5. **Escalation on Discrepancy**: If verification refutes a claim, escalate to PM. Do not silently override or ignore.

## Mechanisms

- `codex_knowledge_graph_query` — verify entity relationships
- `codex_knowledge_memory_query` — verify past decisions
- `codex_knowledge_project_context` — verify project structure
- `treesitter_summarize_path` — verify code structure
- `codex_knowledge_graph_query` — verify logical consistency
- LSP diagnostics — verify type correctness

## Enforcement

- Builder agents must verify PM claims before implementation
- Oracle must verify builder claims during review
- Any agent receiving a claim from another agent must verify before acting
- The `hallucination_auditor` agent provides formal claim audits
