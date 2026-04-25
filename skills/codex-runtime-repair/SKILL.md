---
name: codex-runtime-repair
description: Use for Codex binary, PATH, config, agent, skill, or MCP failures.
---

Focus on the failing runtime surface first.

Steps:
1. Identify the broken command or config path.
2. Reproduce the failure with the smallest command.
3. Patch the runtime artifact only as far as needed.
4. Verify the repair and note any remaining environment gap.
