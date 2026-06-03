---
name: priority-scheduling
description: Enforce priority ordering so critical repairs and user-blocking work always outrank cleanup, refactors, and documentation.
---

# Priority Scheduling

## Purpose
Ensure that the most important work is done first. Critical repairs and user-blocking issues always take precedence over cleanup, refactors, and documentation.

## Priority Tiers

### P0 — Critical (Drop Everything)
- Production outage or data loss
- Security vulnerability with active exploit
- Build completely broken (no tests pass)
- User is blocked and cannot proceed

**Action**: Drop all other work. Fix immediately. No review gate needed for P0 fixes under 10 lines.

### P1 — High (Same Day)
- Feature regression (previously working, now broken)
- Performance degradation >50%
- Security vulnerability without active exploit
- User-facing bug with workaround available

**Action**: Prioritize in current sprint. Oracle review required before merge.

### P2 — Medium (This Sprint)
- New feature implementation
- Non-critical bug fix
- Performance improvement <50%
- Documentation update for changed behavior

**Action**: Normal pipeline with full review gates.

### P3 — Low (Backlog)
- Code cleanup and refactoring
- Documentation improvements
- Test coverage improvements
- Technical debt reduction

**Action**: Only if no P0-P2 work exists. Full review gates apply.

## Hard Rules

1. **P0 Preempts Everything**: If a P0 issue is identified, all P1-P3 work stops until the P0 is resolved.

2. **Priority Escalation**: Any agent can escalate a task's priority if they discover it's more urgent than initially classified. Escalation requires PM approval.

3. **Priority Downgrade**: PM can downgrade priority only with evidence that the issue is less severe than initially thought.

4. **No P3 During P0/P1**: When P0 or P1 work is active, no P3 tasks should be in progress.

## Scheduling Decision Tree

```
Is there a P0 issue? → YES → Drop everything, fix now
                     → NO  → Is there a P1 issue? → YES → Prioritize this sprint
                                                   → NO  → Is there a P2 issue? → YES → Normal pipeline
                                                                                    → NO  → P3 backlog
```

## Output Format

When reporting priority:
```yaml
priority:
  task: <task description>
  tier: <P0|P1|P2|P3>
  reason: <why this tier>
  blocking: <what is blocked by this>
  estimated_effort: <lines of code or time>
```
