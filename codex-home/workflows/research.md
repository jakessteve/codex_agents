---
name: research
summary: Research workflow for current or official source validation. Read-only — never mutate project state.
---

# Research

## Purpose
Gather information from official and primary sources without mutating project state.

## Hard Rules
- **Read-only**: Never modify any project files, memory, or graph during research
- **Source tiering**: Prefer official docs and repository source over web search
- **No assumptions**: Record what sources say, not what you infer

## Steps

### 1. Read Project Context
- Use `codex_knowledge_project_context` to load existing knowledge
- Use `codex_knowledge_memory_query` to check past research
- Use `codex_knowledge_graph_query` to find relevant entities

### 2. Gather Sources
- **Tier 1**: Repository source code (`read`, `glob`, `grep`)
- **Tier 2**: Official library documentation (`context7_resolve-library-id` + `context7_query-docs`)
- **Tier 3**: Project wiki and knowledge base (`codex_knowledge_vault_search`)
- **Tier 4**: Web search (only if Tier 1-3 are insufficient)

### 3. Summarize Findings
- Compile findings into a compact research contract
- Cite all sources with tier levels
- Flag any contradictions between sources
- Use `cognition_codex_check_aop_consistency` to verify logical consistency

### 4. Output Research Contract
```yaml
research_contract:
  question: <research question>
  findings:
    - claim: <what was found>
      source_tier: <1|2|3|4>
      source: <specific reference>
      confidence: <high|medium|low>
  contradictions:
    - claim_a: <one claim>
      claim_b: <contradicting claim>
      resolution: <which is more authoritative>
  gaps:
    - <what could not be found>
  recommendation: <based on findings>
```

### 5. Do NOT Mutate
- Do not write to any project files
- Do not update memory or graph stores (that's for the implementation phase)
- Do not make implementation decisions (that's for the planning phase)
