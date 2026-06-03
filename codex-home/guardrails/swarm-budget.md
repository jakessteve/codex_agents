---
name: swarm-budget
description: Limit the number of active write-capable agents and batch related tasks into single waves to prevent conflicts and context explosion.
---

# Swarm Budget

## Purpose
Prevent context explosion and file conflicts by limiting the number of active write-capable agents and batching related tasks.

## Hard Rules

1. **Maximum Concurrent Writers**: No more than 2 write-capable agents may be active simultaneously. If more are needed, use wave execution with one writer per branch.

2. **Wave Sizing**: When using `independent_ensemble` topology:
   - Maximum 3 agents per wave
   - Each agent gets a proportional context budget
   - Merge via ensemble merge policy after all agents complete

3. **Batch Related Tasks**: If multiple tasks touch the same files or modules, batch them into a single agent rather than spawning multiple agents:
   ```yaml
   batch:
     tasks: [task_a, task_b, task_c]
     reason: "All touch src/components/AmLichPage.tsx"
     agent: builder_frontend
   ```

4. **Read-Only Agents Don't Count**: Explorer, oracle, hallucination_auditor, and other read-only agents don't count against the writer budget. They can run in parallel with writers.

5. **Context Budget Per Agent**: Each agent in a wave gets a proportional share of the total context budget:
   - Total budget / number of agents = per-agent budget
   - If per-agent budget < 8,000 tokens, reduce the wave size

6. **File Ownership**: Each write-capable agent must declare its file set in the task contract. No two agents may write to the same file simultaneously.

## Sizing Guidelines

| Task Complexity | Max Writers | Max Readers | Max Total |
|---------------|-------------|------------|-----------|
| Atomic | 1 | 1 | 2 |
| Medium | 1 | 2 | 3 |
| Epic (sequential) | 1 | 3 | 4 |
| Epic (wave) | 2 | 2 | 4 |

## Output Format

When reporting swarm status:
```yaml
swarm_status:
  active_writers: <count>
  active_readers: <count>
  total_agents: <count>
  context_budget_per_agent: <tokens>
  file_conflicts: <list of conflicting files, if any>
  action: <proceed|reduce_wave|serialize>
```
