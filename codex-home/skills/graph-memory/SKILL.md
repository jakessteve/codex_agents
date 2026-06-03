---
name: graph-memory
description: Record and query structured project relationships in the knowledge graph. Use for entity relationships, dependency tracking, and decision tracing.
---

# Graph Memory

## Purpose
Store traceable relationships between docs, agents, decisions, and evidence in the project knowledge graph.

## When to Use
- Recording a design decision and its rationale
- Tracking dependencies between components
- Linking requirements to implementations
- Storing entity relationships (exports, imports, contains, etc.)

## Steps

### 1. Identify the Relation
- What is the subject? (e.g., `calendarEngine`, `project:lich-viet`)
- What is the relation? (e.g., `EXPORTS`, `HAS_TECH_STACK`, `DEPENDS_ON`)
- What is the target? (e.g., `getLunarDate`, `React+TypeScript+Vite`)

### 2. Store the Relation
- Use `codex_knowledge_graph_upsert` with:
  - slug: project slug
  - src: subject entity
  - rel: relationship type
  - dst: target entity
  - payload: evidence or description

### 3. Query the Graph
- Use `codex_knowledge_graph_query` to search by term
- Use `codex_knowledge_graph_neighbors` to find related entities
- Use `codex_knowledge_project_context` for project-level context

### 4. Capture Only Durable Facts
- Store relationships that will remain true over time
- Don't store temporary state or implementation details
- Don't store information that changes frequently

## Common Relation Types
- `EXPORTS`: entity exports these functions/classes
- `IMPORTS`: entity imports from another entity
- `DEPENDS_ON`: entity depends on another entity
- `CONTAINS`: entity contains these sub-components
- `HAS_TECH_STACK`: project uses these technologies
- `IS_ENGINE`: entity is an engine module
- `IS_COMPONENT`: entity is a UI component
- `IS_SERVICE`: entity is a service module
- `DECIDED_BY`: decision was made by this ADR
