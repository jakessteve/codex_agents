---
name: file-ownership
description: Enforce single-writer file ownership to prevent conflicts. Only one write-capable agent may own a file set at a time.
---

# File Ownership

## Purpose
Prevent conflicting writes by ensuring only one write-capable agent owns a file set at any given time.

## Hard Rules

1. **Single Writer Rule**: Only one write-capable agent may modify a file at a time. The PM assigns file ownership in the task contract.

2. **Ownership Declaration**: Every task contract must include:
   ```yaml
   allowed_files:
     - path: <file_or_glob>
       agent: <agent_name>
       mode: <write|read>
   ```

3. **Lock File System**: Write-capable agents must create a lock file before modifying:
   ```bash
   .agent-locks/<agent-name>.json
   ```
   Lock file format:
   ```json
   {
     "agent": "<agent-name>",
     "branch": "<branch-name>",
     "worktree": "<path>",
     "files": ["<claimed files>"],
     "started_at": "<ISO timestamp>",
     "expires_at": "<ISO timestamp>"
   }
   ```

4. **Lock Expiry**: Locks expire after 30 minutes by default. Stale locks are cleaned up automatically.

5. **Conflict Resolution**: If two agents need the same file:
   - PM reassigns ownership to the higher-priority agent
   - The lower-priority agent waits or works on a different file set
   - If urgency is equal, PM merges the changes manually

6. **Read-Only Access**: Agents without write permission can always read files. Read access never requires a lock.

## Mechanisms

- `worktree_isolation` skill — manages git worktrees for parallel agents
- Lock files in `.agent-locks/` — track file ownership
- `planner_review_task_contract` — validates file ownership in task contracts
- `codex_knowledge_graph_query` — verify file ownership history

## Enforcement

- PM assigns file ownership in task contracts
- Agents check lock files before writing
- Stale locks are cleaned up after 30 minutes
- Conflicts are escalated to PM for resolution
