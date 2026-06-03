---
name: cognifold_memory
description: Use when folding events, concepts, and intents into Cognifold state. Includes cache-aware memory folding for better cache hit rates.
---

# Cognifold Memory Skill

## Purpose
Fold events, concepts, and intents into compact persistent memory using the Cognifold MCP service. Includes cache-aware memory structuring for better prompt cache hit rates.

## Steps

1. **Check Semantic Cache**: Before folding new memories, check if similar concepts already exist:
   ```
   chromadb_mcp_query_collection(
     collection_name="semantic_cache",
     query_texts=["<concept or intent text>"],
     n_results=3
   )
   ```
   If a similar concept exists with high similarity (≥ 0.92), reference it instead of creating a duplicate.

2. **Fold into Cognifold**: Call `cognition_codex_fold_cognifold` with new events, concepts, and intents.

3. **Mirror to Memory Store**: The bridge plugin automatically mirrors `fold_cognifold` to `codex_knowledge_memory_store`.

4. **Store in Semantic Cache**: Cache the folded concepts for future retrieval:
   ```
   chromadb_mcp_add_documents(
     collection_name="semantic_cache",
     documents=["<concept text>"],
     ids=["cognifold_<hash>"],
     metadatas=[{"type": "cognifold_concept", "source": "fold_cognifold"}]
   )
   ```

5. **Review Stored Counts**: Check the top concepts and intents to ensure durable signals are preserved.

## Cache-Aware Memory Practices
- Prefer compact, validated memory folds over reactive note-taking
- Structure concept names with stable prefixes (domain + category) for better cacheability
- Deduplicate concepts before folding (check semantic cache first)
- Record memory fold cache hit rate as a KPI
