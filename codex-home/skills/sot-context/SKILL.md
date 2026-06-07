---
name: sot-context
description: Load project state from curated source of truth docs. Prefer indexed retrieval over broad scanning.
---

# SOT Context

## Purpose
Load project context efficiently from curated source of truth documents, avoiding broad file scanning.

## Steps

### 1. Read the Project Index
- Use `codex_knowledge_project_index` to get the project overview
- This gives you the list of available documents and their categories

### 2. Read the Current Project Context
- Use `codex_knowledge_project_context` with a specific query
- This retrieves the most relevant context for your task
- Much more efficient than reading entire documents

### 3. Read Only the Linked Source Docs
- From the project context, identify which specific documents are relevant
- Use `codex_knowledge_vault_read` to read only those documents
- Use `codex_knowledge_vault_search` to search within the vault
- Do NOT read entire document trees

### 4. Supplement with Memory and Graph
- Use `codex_knowledge_memory_query` for past decisions
- Use `codex_knowledge_graph_query` for entity relationships
- Use `codex_knowledge_project_context` for multi-perspective queries

## Efficiency Rules
- Always prefer `codex_knowledge_project_context` over reading files
- Always prefer `codex_knowledge_memory_query` over re-reading conversation history
- Always prefer `codex_knowledge_graph_query` over searching all files
- Only read specific documents when the indexed context is insufficient
