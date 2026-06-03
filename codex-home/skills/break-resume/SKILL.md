---
name: break-resume
description: Emit compact BreakRequest and ResumePackage contracts for blocked human-in-the-loop phases.
---

# Break/Resume

## Purpose
Use a structured contract when a subagent is genuinely blocked and needs PM-mediated user input.

## BreakRequest

```yaml
break_request:
  agent: <agent_name>
  phase: clarify | explore | scope_lock | plan_review | implementation | final_review
  blocker_type: ambiguity | permission | dependency | conflict | resource
  question: <single clear question>
  context_package:
    task_id: <task_id>
    completed_steps: [...]
    pending_steps: [...]
    relevant_files: [...]
  suggested_options:
    - label: <option_label>
      description: <what this option means>
  max_retries: 2
```

## ResumePackage

```yaml
resume_package:
  answer: <user-answer>
  decision: <chosen-option-label>
  scope_change: null | <scope-change-description>
  context_updates:
    - key: <update-key>
      value: <update-value>
```

## Rules
- Ask one question only.
- Keep the context package under 500 tokens.
- PM is the only role that presents BreakRequests to users.
- Any `scope_change` re-opens Scope Lock.
