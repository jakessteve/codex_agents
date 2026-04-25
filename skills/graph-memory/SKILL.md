---
name: graph-memory
description: Use for Kuzu, vector memory, checkpoints, and durable graph capture.
---

Treat graph and memory updates as durable project state.

Steps:
1. Record only validated lessons.
2. Keep graph edges and checkpoints minimal.
3. Do not write speculative memory.
4. Preserve approval gates before capture.
