---
name: loop-detection
description: Active loop detection and breaking. Use when the agent is repeating the same action, getting the same error, or cycling through tools without progress. MANDATORY check before every 3rd retry.
---

# Loop Detection Skill

## Purpose
Detect and break active loops during agent sessions. This is an ENFORCED mechanism, not just advice.

## Loop Detection Rules

### Rule 1: Three-Strike Rule
If you call the same tool with the same (or semantically equivalent) arguments **3 times** without making progress:
- **STOP immediately**
- Summarize what you've tried and why it failed
- Choose a fundamentally different approach
- If no alternative exists, ask the user for guidance

### Rule 2: Error Loop Rule
If you receive the same error message **3 times in a row**:
- **STOP immediately**
- The error is likely environmental, not fixable by retrying
- Report the error to the user with full context
- Suggest manual intervention

### Rule 3: Progress Check
After every **5 tool calls** in a single task:
- Pause and ask: "Has the task actually progressed?"
- If no measurable progress, reframe the approach
- Use `codex_knowledge_handoff_checkpoint` to save state before reframing

### Rule 4: Context Pressure
If context exceeds **80% of budget** (see context_budget/policy.md):
- Trigger compaction via `codex_knowledge_handoff_checkpoint`
- Do NOT continue adding more context
- Summarize and reduce before proceeding

## Loop Breaking Actions

When a loop is detected, take ONE of these actions in order:

1. **Reframe**: Describe the problem differently and try a completely different tool or approach
2. **Reduce**: Simplify the task to a smaller scope that can be verified
3. **Escalate**: Ask the user for clarification or manual intervention
4. **Checkpoint**: Save state via `codex_knowledge_handoff_checkpoint` and start fresh

## Integration with Other Systems

- **doom_loop permission**: Set to `"ask"` in config.toml — prompts user when loop detected
- **loop_guard plugin**: Counts identical tool calls and warns at 3 repetitions
- **codex_knowledge_graph_query**: Post-hoc classification of repeated failure patterns
- **codex_knowledge_orchestration_lesson**: Detects recurring themes in dreaming cycles

## NEVER
- Never retry the same approach more than 3 times
- Never ignore an error that appears 3+ times
- Never add more context when already at 80% budget
- Never continue a task that shows no progress after 5 tool calls
