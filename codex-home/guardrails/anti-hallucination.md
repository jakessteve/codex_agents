---
name: anti-hallucination
description: Prevent hallucinated paths, commands, file references, and API outputs by requiring verification from authoritative sources before use.
---

# Anti Hallucination

## Purpose
Ensure every path, command, file reference, and API output is verified from the repository or official documentation before being used in any action.

## Hard Rules

1. **Verify Before Use**: Every file path, command, API endpoint, and configuration value must be verified from one of these sources before use:
   - Repository file system (via `read`, `glob`, `grep` tools)
   - LSP diagnostics (via configured language servers)
   - Tree-sitter structural analysis (via `treesitter_summarize_path`)
   - Project knowledge graph (via `codex_knowledge_graph_query`)
   - Project memory (via `codex_knowledge_memory_query`)
   - Official documentation (via `context7_resolve-library-id` + `context7_query-docs`)

2. **Source Tiering**: Sources have different trust levels:
   - **Tier 1 (Authoritative)**: Repository source code, LSP diagnostics, official docs
   - **Tier 2 (Verified)**: Project knowledge graph, project memory, wiki docs
   - **Tier 3 (Unverified)**: Model-generated claims, web search results, assumptions
   - Never act on Tier 3 claims without Tier 1 or Tier 2 verification

3. **No Invented Paths**: Never create a file path that hasn't been confirmed to exist via `glob` or `read`. If you need to create a new path, explicitly state it's new.

4. **No Invented Commands**: Never run a command that hasn't been verified to exist. Check `--help` or `man` pages first if uncertain.

5. **No Invented APIs**: Never call an API endpoint or function that hasn't been verified from source code or official docs. Use `context7` for library documentation.

6. **Hallucination Audit**: For non-trivial changes, run `hallucination_auditor` agent to classify findings using the AgentHallu taxonomy:
   - Factual Hallucination: Claims contradicting verified sources
   - Scope Drift: Output exceeding task scope
   - Logical Inconsistency: Internal contradictions
   - Confident Fabrication: Confident statements about unverified facts
   - Context Overflow: Claims exceeding available context

## Mechanisms

- **LSP servers**: 9 configured (clangd, rust-analyzer, typescript, html, css, json, markdown, eslint, python, yaml)
- **Tree-sitter**: `treesitter_summarize_path` and `treesitter_changed_symbols`
- **Knowledge graph**: `codex_knowledge_graph_query` for entity verification
- **Memory**: `codex_knowledge_memory_query` for past verification records
- **Context7**: `context7_resolve-library-id` + `context7_query-docs` for library docs
- **AOP consistency**: `cognition_codex_check_aop_consistency` for logical consistency

## Enforcement

- Every file path must be verified via `glob` or `read` before writing
- Every command must be verified via `--help` or `man` before execution
- Every API must be verified via source code or official docs before calling
- The `hallucination_auditor` agent can be invoked for formal audits
- The `claim_verification` guardrail applies to claims from other agents

## Output Format

When reporting verification status:
```yaml
verification:
  claim: <what was claimed>
  source_tier: <1|2|3>
  verified_by: <tool or source>
  verified: <true|false|unverifiable>
  alternative: <verified alternative if claim is wrong>
```
