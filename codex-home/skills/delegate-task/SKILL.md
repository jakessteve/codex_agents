---
name: delegate-task
description: Spawn a bounded subtask with clear ownership, scope, and output requirements. Validate before spawning.
---

# Delegate Task

## Purpose
Keep delegation explicit, bounded, and summary-only. Every subagent must know exactly what to produce and what files it can touch.

## Steps

### 1. Define the Exact Output Needed
- What must the subagent produce? (code, review, research, etc.)
- What format should the output be in? (YAML, Markdown, code files)
- What acceptance criteria must the output meet?

### 2. Define Allowed Files and Evidence
- List every file the subagent is allowed to read
- List every file the subagent is allowed to modify
- List every test the subagent must run
- Define the scope drift budget

### 3. Spawn Only the Minimum Required Helper
- Use the smallest agent that can accomplish the task
- Read-only agents for research and review
- Write agents for implementation
- Never spawn more agents than needed

### 4. Collect Summary-Only Return
- Subagent returns: changed files, evidence, risks, next action
- No sibling-to-sibling messaging
- PM manages all inter-agent communication

### 5. Validate the Return
- Check that the output meets the acceptance criteria
- Verify that only allowed files were modified
- Run tests if required
- Use `planner_review_task_contract` to validate scope

### 6. Output Format
```yaml
delegation:
  agent: <agent_name>
  task: <clear task description>
  allowed_files: <list>
  required_output: <what to produce>
  required_tests: <list>
  scope_drift_budget: <percentage>
  result:
    status: <completed|failed|partial>
    changed_files: <list>
    evidence: <list>
    risks: <list>
    next_action: <recommended step>
```
