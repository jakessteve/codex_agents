# Anti Pattern Guardrails

## Purpose
Prevent common anti-patterns that degrade agent performance, waste tokens, and break prompt caches.

## Hard Rules

1. **No Hallucinated Files or APIs**: Every file path, command, and API endpoint must be verified from repository source, LSP diagnostics, or official documentation before use.

2. **No Loops or Thrash**: If the same tool call with the same arguments is made 3 times without progress, STOP and reframe. See `anti_loop` guardrail for enforcement mechanisms.

3. **No Context Explosion**: Never re-read files already read in the current session. Use indexed retrieval (`codex_knowledge_project_context`, `codex_knowledge_memory_query`) instead. See `anti_context_overflow` guardrail for budget thresholds.

4. **No Cache-Busting Patterns**:
   - Never interleave dynamic content into the stable system prefix
   - Never reorder the system prefix within a session
   - Never include volatile timestamps or random IDs in the prefix section
   - Always place task-specific content AFTER the stable prefix

5. **No Redundant Retrieval**: Before making a new search query, check the semantic cache (`codex_knowledge_memory_query` with query prefix `semantic_cache:`). If a similar query was answered before (similarity ≥ 0.92), reuse the cached result.

6. **No Unstructured Inter-Agent Communication**: All handoffs must use YAML or Markdown contracts. No free-form prose between agents.

7. **No Scope Creep Without Budget**: Any change beyond the original task contract must be explicitly approved and tracked against the scope drift budget (default: 5%).

## Enforcement

- `loop_guard.ts` plugin detects repeated tool calls
- `loop-detection guardrails` permission prompts user on detected loops
- `anti_context_overflow` guardrail enforces budget thresholds
- `prompt_caching_rules.md` enforces prefix stability
- `minimalist_review_change` flags over-engineering
