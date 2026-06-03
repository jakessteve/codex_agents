---
name: worktree-isolation
description: Manage git worktrees for parallel agent execution. Use when multiple write-capable agents need to work simultaneously on the same repository.
---

# Worktree Isolation Skill

## Purpose
Prevent conflicts when multiple write-capable agents work in parallel by using git worktrees.

## When to Use
- Multiple agents need to modify files simultaneously
- Parallel implementation of independent features
- When Oracle review and implementation overlap

## Worktree Management

### Create Worktree
```bash
git worktree add ../<branch-name> -b <branch-name>
```

### Lock File System
Each agent writes a lock file to `.agent-locks/<agent-name>.json`:
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

### Lock Rules
1. Only one agent may claim a file at a time
2. Locks expire after 30 minutes by default
3. Agents must check locks before writing
4. PM agent manages lock conflicts

### Merge Worktree
```bash
cd ../<branch-name>
git add -A && git commit -m "<message>"
cd <main-repo>
git merge <branch-name> --no-ff
git worktree remove ../<branch-name>
git branch -d <branch-name>
```

### Cleanup Stale Locks
```bash
# Remove locks older than 30 minutes
find .agent-locks/ -name "*.json" -mmin +30 -delete
```

## Guardrails
- Never have two write-capable agents on the same branch
- Always use worktrees for parallel work
- Clean up worktrees and branches after merge
- Record worktree state in codex_knowledge for cross-agent visibility
