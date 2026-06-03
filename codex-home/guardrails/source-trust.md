---
name: source-trust
description: Enforce source trust tiers. Project source and official docs are truth; scraped or model-generated claims must be verified before use.
---

# Source Trust

## Purpose
Establish clear trust levels for information sources and enforce verification requirements based on source tier.

## Trust Tiers

### Tier 1 — Authoritative (Trusted Without Verification)
- Repository source code (verified via `read`, `glob`, `grep`)
- LSP diagnostics (type errors, undefined references)
- Official library documentation (via `context7`)
- Project knowledge graph (via `codex_knowledge_graph_query`)
- Project memory (via `codex_knowledge_memory_query`)
- Test results (verified execution output)

### Tier 2 — Probable (Verify Before Acting)
- Wiki documentation (may be outdated)
- Code comments (may not match implementation)
- Third-party blog posts or tutorials
- Model reasoning about well-known patterns

### Tier 3 — Unverified (Never Act Without Upgrading)
- Model-generated code that hasn't been tested
- Assumptions about file structure
- "I think" or "it should be" statements
- Web search results from non-official sources
- Claims from other agents that haven't been independently verified

## Hard Rules

1. **Never Act on Tier 3 Alone**: Any Tier 3 claim must be upgraded to Tier 1 or Tier 2 before being used in implementation.

2. **Tier 2 Requires One Verification**: Tier 2 claims require at least one independent verification source before action.

3. **Tier 1 Is Sufficient**: Tier 1 claims can be acted upon immediately, but should still be cross-referenced when the cost of being wrong is high.

4. **Source Citation Required**: When making claims, always cite the source tier:
   ```yaml
   claim:
     statement: <what is claimed>
     source_tier: <1|2|3>
     source: <specific tool or document>
     verified: <true|false|pending>
   ```

5. **Conflict Resolution**: When Tier 1 sources conflict:
   - Repository source code takes precedence over documentation
   - LSP diagnostics take precedence over comments
   - Official docs take precedence over third-party sources
   - When in doubt, test the actual behavior

## Mechanisms

- `codex_knowledge_project_context` — retrieve authoritative project context
- `codex_knowledge_graph_query` — verify entity relationships
- `codex_knowledge_memory_query` — verify past decisions
- `context7_resolve-library-id` + `context7_query-docs` — verify library documentation
- `treesitter_summarize_path` — verify code structure
- LSP diagnostics — verify type correctness

## Enforcement

- Builder agents must cite source tier for all claims
- Oracle reviews source tier citations during review
- Hallucination auditor checks for Tier 3 claims without verification
