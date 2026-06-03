# Break/Resume Protocol

## Purpose
Enable compact human-in-the-loop pauses when a phase is genuinely blocked.

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
- Emit BreakRequest only when blocked.
- Ask one clear question.
- Keep context under 500 tokens.
- PM presents the question to the user.
- Scope changes trigger Scope Lock re-evaluation.
