# Anti Loop

## Hard Rules (ENFORCED)

1. **Three-Strike Rule**: If the same tool call with the same arguments is made 3 times without progress, STOP and reframe.
2. **Error Loop Rule**: If the same error appears 3 times consecutively, STOP and escalate to the user.
3. **Progress Check**: After every 5 tool calls, verify measurable progress. If none, reframe or checkpoint.
4. **Context Pressure**: At 80% context budget, checkpoint and compact. Do NOT continue expanding context.

## Mechanisms

- **Platform**: `loop-detection guardrails` in config.toml prompts user on detected loops
- **Plugin**: `loop_guard.ts` counts identical tool calls and warns at 3 repetitions
- **Skill**: `loop-detection` skill provides explicit rules for agents
- **Post-hoc**: `codex_knowledge_graph_query` classifies repeated failures after the fact

## Breaking a Loop

When stuck in a loop:
1. **Reframe** — describe the problem differently, use a different tool
2. **Reduce** — simplify to a smaller verifiable scope
3. **Escalate** — ask the user for guidance
4. **Checkpoint** — save state via `codex_knowledge_handoff_checkpoint` and start fresh
