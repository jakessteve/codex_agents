---
name: dependency-deadlock
description: Detect and break agent dependency cycles. PM must resolve cycles before execution continues.
---

# Dependency Deadlock

## Purpose
Prevent deadlocks where agents wait on each other in a cycle, and ensure dependency graphs are acyclic before execution begins.

## Hard Rules

1. **No Cyclic Dependencies**: If agent dependencies form a cycle (A waits on B, B waits on C, C waits on A), PM must break the cycle before execution continues.

2. **Explicit Dependency Declaration**: Every task contract must declare:
   ```yaml
   dependencies:
     - agent: <agent_name>
       provides: <what this agent provides>
       requires: <what this agent needs from others>
   ```

3. **Cycle Detection**: Before spawning agents, PM must verify the dependency graph is acyclic using:
   - Topological sort of agent dependencies
   - If a cycle is detected, PM must either:
     a. Remove one dependency to break the cycle
     b. Merge the cycling agents into a single agent
     c. Refactor the task to eliminate the circular requirement

4. **One Writer Per File Set**: Only one write-capable agent may own a file set at a time. Use `worktree_isolation` skill for parallel writes.

5. **Read-Only Agents Don't Block**: Read-only agents (explorer, oracle, hallucination_auditor) never create dependencies that block write agents.

## Mechanisms

- `planner_suggest_topology` — suggests routing topology and identifies potential deadlocks
- `planner_review_task_contract` — validates task contracts for completeness including dependencies
- `worktree_isolation` skill — manages git worktrees for parallel agents
- File lock system — `.agent-locks/<agent-name>.json` tracks file ownership

## Enforcement

- PM checks dependency graph before spawning agents
- If a cycle is detected, PM breaks it before execution
- File locks prevent simultaneous writes to the same files
- Worktrees isolate parallel agents
