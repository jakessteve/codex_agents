---
name: pyrag_reasoning
description: Use when composing a deterministic PyRAG plan from a goal and evidence sources. Includes plan caching for cache hit optimization.
---

# PyRAG Reasoning Skill

## Purpose
Compose deterministic, verifiable reasoning programs using the PyRAG pattern. Includes plan caching to improve cache hit rates for recurring goals.

## Steps

1. **Check Plan Cache**: Before composing a new program, check if a similar goal has been composed before:
   ```
   codex_knowledge_memory_query(query="pyrag_plan", limit=5)
   ```
   If a cached plan matches the goal (semantic similarity ≥ 0.85), reuse it with modifications.

2. **Compose the Program**: Call `cognition_codex_compose_pyrag_program` with the goal, retrieval sources, and constraints.

3. **Cache the Plan**: Store the composed plan for future reuse:
   ```
   codex_knowledge_memory_store(
     key="pyrag_plan:<goal_hash>",
     value=<plan_json>,
     slug="codex_agents"
   )
   ```
   Also store in semantic cache:
   ```
   chromadb_mcp_add_documents(
     collection_name="semantic_cache",
     documents=["<goal text>"],
     ids=["pyrag_<goal_hash>"],
     metadatas=[{"type": "pyrag_plan", "goal_hash": "<hash>"}]
   )
   ```

4. **Execute and Validate**: Execute each step with evidence retrieval. Use the repair loop for failed steps.

5. **Record Cache Hit**: Record whether the plan was a cache hit or miss in the KPI tracking:
   ```
   codex_knowledge_memory_store(
     key="kpi:plan_cache_hit_rate:<date>",
     value=<json_with_hit_or_miss>,
     slug="codex_agents"
   )
   ```

## Cache-Friendly Practices
- Structure goals with stable prefixes (domain + action type) before dynamic specifics
- Use consistent retrieval source names across similar goals
- Reuse constraint lists when goals are semantically similar
- Record plan cache hit rate as a KPI for dreaming optimization
