---
name: spawn-governance
description: Govern subagent spawning with explicit scope, file ownership, and output requirements. Validate before spawning.
---

# Spawn Governance

## Purpose
Prevent uncontrolled agent spawning by requiring explicit scope, file ownership, and output requirements before creating subagents.

## Rules

### 1. Validate Before Spawning
Before creating any subagent, verify:
- The task is clearly defined with explicit output requirements
- The allowed files are listed and non-overlapping with other agents
- The required tests are specified
- The scope drift budget is allocated

### 2. Define Spawn Contract
Every spawn must include:
```yaml
spawn_contract:
  agent: <agent_name>
  task: <clear task description>
  allowed_files: <list of files the agent may modify>
  required_output: <what the agent must produce>
  required_tests: <tests the agent must run>
  scope_drift_budget: <percentage>
  context_budget: <tokens>
  timeout: <maximum turns>
```

### 3. File Ownership
- Only one write-capable agent may own a file set at a time
- Use `worktree_isolation` skill for parallel writes
- Create lock files in `.agent-locks/` for file ownership
- Locks expire after 30 minutes

### 4. Output Requirements
- Every subagent must return: changed files, evidence, risks, next action
- No sibling-to-sibling messaging
- All communication goes through PM

### 5. No Over-Spawning
- Maximum 2 write-capable agents active simultaneously
- Maximum 3 agents per wave
- If more are needed, use sequential waves instead of parallel

## Output Format
```yaml
spawn_result:
  agent: <agent_name>
  status: <completed|failed|timed_out>
  changed_files: <list>
  evidence: <list of verification results>
  risks: <list of identified risks>
  next_action: <recommended next step>
```
