---
name: document-sync
summary: Sync approved changes to documentation, indexes, and the local Obsidian vault.
---

# Document Sync

## Purpose
Keep documentation, indexes, and the local Obsidian vault in sync with approved code changes.

## When to Run
- After every Oracle-approved implementation
- After every epic closeout
- After any architectural change

## Steps

### 1. Compare Diff to Approved Docs
- Use `treesitter_changed_symbols` to identify what symbols changed
- Use `codex_knowledge_graph_query` to find documentation linked to those symbols
- List all docs that reference changed symbols:
  ```yaml
  doc_impact:
    changed_symbols: <list from treesitter>
    affected_docs: <list from graph query>
    needs_update: <list of docs that reference changed symbols>
  ```

### 2. Update Indexes
- Use `codex_knowledge_wiki_ingest` to rebuild the wiki index
- Use `codex_knowledge_graph_upsert` to update entity relationships
- Use `codex_knowledge_memory_store` to update memory entries

### 3. Update Traceability
- For each changed component, update:
  - Source-to-doc links in the graph
  - Memory entries for the change
  - Vault documents if they exist

### 4. Sync to Obsidian Vault
- Use `doc_sync_worker` agent for approved summaries
- Run `scripts/sync_obsidian.sh` to push to local Obsidian vault
- Only sync validated, approved content — never raw transcripts

### 5. Capture Lessons
- Use `codex_knowledge_knowledge_capture` to store what was synced
- Use `codex_knowledge_orchestration_lesson` if the sync revealed documentation gaps

## Guardrails
- Only sync approved content (post-Oracle review)
- Never pull in unrelated skill bundles
- Keep summaries compact and traceable
