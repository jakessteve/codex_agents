# Phase 2 MCP Services

status: operational
owner: pm
summary: Codex MCP service roots for planner, CodeGraph facade, graph, treesitter, minimalist, cognition_codex, evolution, ChromaDB, and trace export services.

## CodeGraph Facade

`mcp/codegraph` exposes the stable CodeGraph-first exploration surface used by SOL:

- `codegraph_symbol_lookup`
- `codegraph_callers_callees`
- `codegraph_impact_analysis`
- `codegraph_semantic_search`

Agents call these tools before broad reads. The implementation is dependency-light today and can later delegate to a stronger indexed graph without changing agent contracts.
