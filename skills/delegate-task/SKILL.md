---
name: delegate-task
description: Use when `pm` needs to assign bounded work to a subagent.
---

Use this skill only after `pm` has decided delegation is needed.

Steps:
1. Assign one bounded slice of ownership.
2. State the expected output, validation, and file scope.
3. Tell the subagent not to overlap another agent's writes.
4. Require summary-only return content.
