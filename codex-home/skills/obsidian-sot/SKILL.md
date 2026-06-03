---
name: obsidian-sot
description: Sync approved project knowledge into the local Obsidian vault. Only mirror validated summaries, not raw transcripts.
---

# Obsidian SOT (Source of Truth)

## Purpose
Mirror validated, approved summaries to the local Obsidian vault for human-readable reference. Never sync raw transcripts or unverified content.

## Steps

### 1. Confirm the Change is Approved
- Verify Oracle review passed
- Verify all acceptance criteria met
- Verify no outstanding vetoes
- Only sync content that has been validated

### 2. Write a Compact Summary
- Summarize the change in 1-3 paragraphs
- Include: what changed, why, and any decisions made
- Link to the task contract and Oracle review
- Use Markdown format compatible with Obsidian

### 3. Preserve Traceability Links
- Include links to:
  - Task contract reference
  - Oracle review reference
  - Related graph entities
  - Related memory entries
- Use Obsidian wiki-link format: `[[entity-name]]`

### 4. Sync to Vault
- Use `codex_knowledge_vault_write` to write the summary
- Use `doc_sync_worker` agent for batch syncs
- Run `scripts/sync_obsidian.sh` to push to local Obsidian vault

### 5. Update Index
- Use `codex_knowledge_wiki_ingest` to rebuild the wiki index
- Use `codex_knowledge_graph_upsert` to update entity relationships

## Guardrails
- Only sync approved content (post-Oracle review)
- Never sync raw conversation logs
- Never sync unverified claims
- Keep summaries compact and traceable
