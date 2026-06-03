---
name: document-sync
description: Sync approved changes to documentation, indexes, and the local Obsidian vault. Run after every Oracle-approved implementation.
---

# Document Sync

## Purpose
Keep documentation, indexes, and the local Obsidian vault in sync with approved code changes.

## Steps

### 1. Identify Changed Symbols
- Use `treesitter_changed_symbols` to identify what changed
- Use `codex_knowledge_graph_query` to find docs linked to those symbols
- List all affected documentation

### 2. Update Indexes
- Use `codex_knowledge_wiki_ingest` to rebuild the wiki index
- Use `codex_knowledge_graph_upsert` to update entity relationships
- Use `codex_knowledge_memory_store` to update memory entries

### 3. Update Vault Documents
- For each affected doc, update the content to match the code
- Use `codex_knowledge_vault_write` to write updated docs
- Preserve traceability links (source file → doc section)

### 4. Sync to Obsidian
- Use `doc_sync_worker` agent for approved summaries
- Run `scripts/sync_obsidian.sh` to push to local Obsidian vault
- Only sync validated, approved content — never raw transcripts

### 5. Capture Lessons
- Use `codex_knowledge_knowledge_capture` to store what was synced
- Use `evolution_record_retrospective` if the sync revealed documentation gaps

## Guardrails
- Only sync after Oracle approval
- Never pull in unrelated skill bundles
- Keep summaries compact and traceable
