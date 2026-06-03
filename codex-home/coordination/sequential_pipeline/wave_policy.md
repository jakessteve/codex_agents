# Wave Policy

## Purpose
Define when and how to use wave execution (parallel agents) within the sequential pipeline. Waves are a performance optimization, not a default.

## Wave Decision Tree

```
PM has decomposed the task into slices
    │
    ▼
Are there ≥2 slices with NO file dependencies between them?
    │
    ├── NO → Execute slices sequentially (default)
    │
    └── YES → Is context budget sufficient for parallel execution?
                │
                ├── NO → Execute slices sequentially to conserve budget
                │
                └── YES → Has PM explicitly approved wave execution?
                            │
                            ├── NO → Execute slices sequentially
                            └── YES → Spawn Wave (Section 3)
```

## When to Use Waves

Waves are appropriate when ALL of the following are true:

1. **Independent Slices:** The task contains ≥2 slices that have no file dependencies on each other.
   - Verify independence with `bash`: `git diff --name-only <slice_A_base> <slice_A_head>` and compare against slice B's planned files.
2. **PM Approval:** PM has explicitly approved wave execution in writing (e.g., in the task contract or a handoff note).
3. **Context Budget Available:** Total context budget minus sequential overhead leaves ≥8,000 tokens per agent.
   - Calculate: `(total_budget - sequential_overhead) / agent_count ≥ 8,000`.
4. **Complexity Justifies Parallelism:** The task is Medium, Large, or Very Large per the complexity table below.

**Waves are NOT appropriate when:**
- Slices have file dependencies (must be sequential to avoid merge conflicts).
- The task is atomic (single slice, single agent is sufficient).
- Context budget is tight (waves consume more total context due to duplicated system prompts and codebase snapshots).
- The task involves a single critical file that all slices must touch (e.g., a central configuration file).
- Previous wave in the same epic resulted in >2 merge conflicts.

---

## Wave Sizing

### Complexity Table

| Epic Complexity | Max Agents per Wave | Max Waves | Context per Agent | Min Total Budget |
|-----------------|---------------------|-----------|-------------------|------------------|
| Medium (5-10 files, 1 domain) | 2 | 1 | 10,000 tokens | 25,000 tokens |
| Large (11-20 files, 2 domains) | 3 | 2 | 15,000 tokens | 50,000 tokens |
| Very Large (21+ files, 3+ domains) | 3 | 3 | 20,000 tokens | 70,000 tokens |

### Complexity Determination

Use `planner_suggest_topology` to determine complexity:
- Input: `task_type`, `file_count`, `domain_count`
- Output: `complexity` field (Medium, Large, Very Large)

If `planner_suggest_topology` is unavailable, use these heuristics:
- `file_count` = count of files in `allowed_files` from task contract
- `domain_count` = count of distinct architectural layers touched (e.g., API, DB, UI, infra)

---

## Wave Rules

### 1. One Writer Per Branch

- Each agent in a wave works on its own git branch or worktree.
- Branch naming convention: `wave<wave_num>/<slice_id>/<agent_id>`
  - Example: `wave1/auth-middleware/builder-backend`
- Use `worktree_isolation` skill for worktree management.
- Create lock files in `.agent-locks/` to prevent file ownership collisions:
  ```yaml
  # .agent-locks/wave1_auth-middleware.lock
  owner: builder-backend
  files:
    - app/middleware/auth.py
    - tests/middleware/test_auth.py
  expires_at: <ISO-8601>
  ```
- If an agent attempts to modify a locked file, the action is blocked and PM is notified.

### 2. No Sibling Communication

- Agents in a wave do NOT communicate with each other.
- All coordination flows through PM.
- Each agent returns a standardized handoff:
  ```yaml
  wave_agent_output:
    agent_id: <uuid>
    slice_id: <identifier>
    branch: <branch name>
    changed_files:
      - path: <relative path>
        change_type: <create|modify|delete>
    evidence:
      - source: <tool or document>
        finding: <what supports the change>
    risks:
      - risk: <description>
        severity: <critical|major|minor>
    tests:
      passing: <count>
      failing: <count>
    next_action: <awaiting_merge|needs_revision|blocked>
    context_used: <token count>
  ```

### 3. Oracle After Each Wave

- After each wave completes, Oracle reviews ALL outputs before any merge.
- Oracle checks:
  - Each output against its slice contract
  - Cross-slice consistency (no conflicting changes to shared interfaces)
  - AOP consistency with the broader codebase
- Oracle verdict per output:
  - **PASS:** Output is approved for merge.
  - **CONDITIONAL:** Minor issues; fix and re-review.
  - **FAIL:** Major issues; discard and re-assign slice.
- Only outputs with PASS verdict are merged.

### 4. Merge After Approval

- Merge only validated outputs (PASS verdict).
- Use `sequential_pipeline/merge_policy.md` for merge mechanics.
- Use `independent_ensemble/merge_policy.md` if merging elements from multiple wave outputs.
- Merge order:
  1. Interface changes (API contracts, shared types)
  2. Implementation changes
  3. Test changes
- After merge, run integration tests.

### 5. Context Budget

- Each agent gets a proportional share of the total context budget.
- Budget formula: `per_agent_budget = (total_budget - pm_overhead) / agent_count`
- If `per_agent_budget < 8,000 tokens`, reduce wave size or switch to sequential.
- Monitor budget with `token_health_check` skill:
  - Check every 10 minutes during wave execution.
  - If any agent exceeds 90% budget, PM evaluates whether to:
    - Reduce the agent's scope
    - Transfer remaining work to a fresh agent
    - Abort the wave and switch to sequential

---

## Wave Execution Flow

```
PM defines slices
    │
    ▼
PM checks slice independence (no shared files)
    │
    ▼
PM approves wave execution
    │
    ▼
PM calculates wave size from complexity table
    │
    ▼
PM spawns agents on isolated branches
    │
    ▼
Agents execute in parallel (no communication)
    │
    ▼
Agents submit outputs to PM
    │
    ▼
Oracle reviews all outputs
    │
    ├── Any FAIL? → Re-assign failed slices; others proceed
    │
    └── All PASS/CONDITIONAL? → Merge approved outputs
                │
                ▼
        Run integration tests
                │
                ├── Pass? → Next wave or completion
                └── Fail? → Debug, fix, re-run tests
```

---

## Wave Output Format

After each wave, PM produces:

```yaml
wave_report:
  wave_id: <unique identifier>
  task_ref: <task contract reference>
  wave_number: <integer>
  timestamp: <ISO-8601>

  agents:
    - agent_id: <uuid>
      slice_id: <identifier>
      verdict: <PASS|CONDITIONAL|FAIL>
      changed_files: <count>
      context_used: <token count>
      status: <merged|revised|discarded|pending>

  merge:
    files_merged: <count>
    conflicts: <count>
    integration_tests:
      passing: <count>
      failing: <count>

  budget:
    total_allocated: <tokens>
    total_used: <tokens>
    remaining: <tokens>

  next_action: <next_wave|sequential_fallback|completion|escalate>
```

**Persistence:**
- Save `wave_report` to `codex_knowledge_knowledge_capture` with key `wave_<wave_id>`.
- If `next_action: sequential_fallback`, PM reverts to sequential execution for remaining slices.
- If `next_action: escalate`, invoke `gates/escalation_gate.md`.

---

## Tool References

| Tool | Purpose | When to Invoke |
|------|---------|----------------|
| `planner_suggest_topology` | Determine complexity and wave eligibility | Before wave planning |
| `worktree_isolation` skill | Create isolated branches/worktrees | Before spawning agents |
| `token_health_check` skill | Monitor per-agent context usage | During wave execution |
| `bash` with `git diff --name-only` | Verify slice independence | Before wave approval |
| `oracle_review_gate` | Review wave outputs | After wave completion |
| `sequential_pipeline/merge_policy.md` | Merge approved outputs | After Oracle review |
| `codex_knowledge_knowledge_capture` | Persist wave reports | After each wave |
